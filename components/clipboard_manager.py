import os
from typing import Callable, Optional

from PyQt6.QtCore import (
    QEasingCurve,
    QEvent,
    QMetaObject,
    QPropertyAnimation,
    QRect,
    Qt,
    pyqtSlot,
)
from PyQt6.QtGui import QEnterEvent, QFont, QMouseEvent, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
from pynput import keyboard

from components import utils
from preload import BECAP_CLIPBOARD_MANAGER_PATH


class ClipboardItem(QWidget):
    def __init__(self, image: QPixmap, file_path: str, created_at: float) -> None:
        super().__init__()

        self.image = image
        self.file_path = file_path
        self.created_at = created_at


class AnimatedLabel(QLabel):
    def __init__(
        self,
        item: ClipboardItem,
        w: int,
        h: int,
        on_selected: Callable[[ClipboardItem], None],
    ) -> None:
        super().__init__()
        self.setFixedSize(w, h)
        self.setPixmap(item.image.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio))
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(
            """
            QLabel {
                background-color: #444;
                color: white;
                border: 2px solid #888;
                border-radius: 10px;
            }
        """
        )
        self.hover_animation = QPropertyAnimation(self, b"geometry")
        self.hover_animation.setDuration(200)
        self.__original_y = None
        self.__original_geometry = None
        self.__on_selected = on_selected
        self.__item = item

    def unlock_animation(self):
        # x coordinate can be changed depending on the list
        self.__original_y = self.y()

    def lock_animation(self):
        self.__original_y = None

    def mousePressEvent(self, ev: Optional[QMouseEvent]) -> None:
        assert ev is not None
        if ev.button() == Qt.MouseButton.LeftButton:
            self.__on_selected(self.__item)

    def enterEvent(self, event: Optional[QEnterEvent]) -> None:
        # Animate to move up when hovered
        if self.__original_y is None:
            return

        self.__original_x = self.x()
        self.__original_geometry = QRect(
            self.__original_x, self.__original_y, self.width(), self.height()
        )
        rect = QRect(self.__original_x, self.__original_y, self.width(), self.height())
        rect.moveTop(rect.top() - 10)  # Move up by 10 pixels
        self.hover_animation.setStartValue(self.geometry())
        self.hover_animation.setEndValue(rect)
        self.hover_animation.start()
        self.update_border_color("#A9CDFF")
        super().enterEvent(event)

    def leaveEvent(self, a0: Optional[QEvent]) -> None:
        # Animate back to original position when not hovered
        if self.__original_y is None or self.__original_geometry is None:
            return

        self.hover_animation.setStartValue(self.geometry())
        self.hover_animation.setEndValue(self.__original_geometry)
        self.hover_animation.start()

        self.update_border_color("#888")  # Default border
        super().leaveEvent(a0)

    def update_border_color(self, color: str):
        # Update the label's style sheet dynamically
        self.setStyleSheet(
            f"""
            QLabel {{
                background-color: #444;
                color: white;
                border: 2px solid {color};
                border-radius: 10px;
            }}
        """
        )


class ClipboardManager(QWidget):

    def __init__(self, max_capacity: int = 20) -> None:
        super().__init__()

        self.__lw, self.__lh = 200, 200  # Label width and height
        self.setFixedHeight(self.__lh + 50)  # 50 for padding

        self.__max_capacity = max_capacity
        self.__items: list[ClipboardItem] = []
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowFlags(Qt.WindowType.Tool)
        # self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Main Layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 0)
        main_layout.setSpacing(0)

        # Scrollable Area
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scroll_area.setStyleSheet("background: transparent; border: none;")

        # Content Widget inside Scroll Area
        self.content_widget = QWidget()
        self.content_widget.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred
        )
        self.content_layout = QHBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(10)  # Spacing between labels
        self.content_widget.setLayout(self.content_layout)

        self.scroll_area.setWidget(self.content_widget)
        main_layout.addWidget(self.scroll_area)

        self.setLayout(main_layout)

        self.__is_active = False
        self.__is_animating = False
        self.__load_items()

    def __load_no_items_label(self):
        # Create the label
        message_label = QLabel("No items in clipboard manager")
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Update font size and style
        font = QFont("Arial", 16)  # Use your preferred font and size
        font.setBold(True)
        message_label.setFont(font)
        self.content_layout.addWidget(message_label)

        self.setFixedWidth(message_label.width())

    def __load_items(self):
        self.__items = []

        if not os.path.exists(BECAP_CLIPBOARD_MANAGER_PATH):
            print("Missing clipboard manager directory")
            self.__load_no_items_label()
            return

        for file in os.listdir(BECAP_CLIPBOARD_MANAGER_PATH):
            if file.endswith(".png"):
                file_path = os.path.join(BECAP_CLIPBOARD_MANAGER_PATH, file)
                created_at = os.path.getctime(file_path)
                image = QPixmap(file_path)
                self.__items.append(ClipboardItem(image, file_path, created_at))

        # Sort items by creation time (newest first)
        self.__items.sort(key=lambda x: x.created_at, reverse=True)
        while len(self.__items) > self.__max_capacity:
            item = self.__items.pop()  # Remove the oldest item
            print(
                f"Over capacity: {len(self.__items)}, removing oldest item: {item.file_path}"
            )
            os.remove(item.file_path)

        total_width = 20  # Padding
        for i in range(self.content_layout.count()):
            item = self.content_layout.itemAt(i)
            if item is not None:
                item = item.widget()
                if item:
                    item.deleteLater()

        for item in self.__items:
            total_width += self.__lw + 10
            self.content_layout.addWidget(
                AnimatedLabel(item, self.__lw, self.__lh, self.__on_label_selected)
            )

        if len(self.__items) == 0:
            self.__load_no_items_label()
            return

        max_width = self.__calculate_max_width()
        self.setFixedWidth(min(total_width, max_width))

    @pyqtSlot()
    def toggle(self):
        if self.__is_active:
            self.__hide_with_animation()
        else:
            self.__show_with_animation()

    def __show_with_animation(self):
        # Determine the active screen
        if self.__is_animating:
            return

        # Maximum of 20 items, so this is ok to call every time
        self.__load_items()

        self.__lock_animation()
        self.__is_active = True
        screen_geometry = utils.get_focus_screen_geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        self.show()

        self.start_x = (
            screen_geometry.x() + (screen_width - self.width()) // 2
        )  # Center horizontally
        self.start_y = (
            screen_height - self.height()
        )  # Start at the bottom of the screen
        self.end_y = screen_height - self.height() - 30  # Final position

        # Animation for showing
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(200)  # Duration in ms
        self.animation.setStartValue(
            QRect(self.start_x, self.start_y, self.width(), self.height())
        )
        self.animation.setEndValue(
            QRect(self.start_x, self.end_y, self.width(), self.height())
        )
        self.animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.animation.start()
        self.animation.finished.connect(lambda: self.__unlock_animation())

    def __calculate_max_width(self):
        screen_geometry = utils.get_focus_screen_geometry()
        screen_width = screen_geometry.width()
        return screen_width * 2 // 3

    def __hide_with_animation(self):
        if self.__is_animating:
            return

        self.__lock_animation()
        self.__is_active = False
        # Animation for hiding
        start_geometry = QRect(self.start_x, self.end_y, self.width(), self.height())
        end_geometry = QRect(self.start_x, self.start_y, self.width(), self.height())

        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(200)  # Duration in ms
        self.animation.setStartValue(start_geometry)
        self.animation.setEndValue(end_geometry)
        self.animation.setEasingCurve(QEasingCurve.Type.InQuad)
        self.animation.start()
        self.animation.finished.connect(lambda: self.hide())
        self.animation.finished.connect(lambda: self.__unlock_animation())

    def __lock_animation(self):
        self.__is_animating = True
        for i in range(self.content_layout.count()):
            widget = self.content_layout.itemAt(i)
            if widget is not None:
                widget = widget.widget()
                if isinstance(widget, AnimatedLabel):
                    widget.lock_animation()

    def __unlock_animation(self):
        self.__is_animating = False
        for i in range(self.content_layout.count()):
            widget = self.content_layout.itemAt(i)
            assert widget is not None
            widget = widget.widget()
            if widget is not None and isinstance(widget, AnimatedLabel):
                widget.unlock_animation()

    def __on_label_selected(self, item: ClipboardItem):
        if self.__is_animating:
            return

        clipboard = QApplication.clipboard()
        if clipboard is None:
            return

        clipboard.setPixmap(item.image)
        self.__hide_with_animation()


def run_clipboard_manager():
    app = QApplication([])
    clipboard_manager = ClipboardManager()

    def on_activate():
        QMetaObject.invokeMethod(
            clipboard_manager, "toggle", Qt.ConnectionType.QueuedConnection
        )

    # Start global keyboard listener
    with keyboard.GlobalHotKeys(
        {"<ctrl>+<alt>+<up>": on_activate},
    ):
        app.exec()
