from enum import Enum
import os
from typing import Callable, List, Optional, Tuple
from PyQt6.QtCore import QPoint, QPointF, Qt
from PyQt6.QtGui import QColor, QIcon, QMouseEvent, QPainter, QPixmap
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QScrollArea,
    QWidget,
)

from components.shortcut_blocking import ShortcutBlockable
from preload import ICON_DIR

PAINT_ICON = os.path.join(ICON_DIR, "paint.svg")


class MouseState(Enum):
    NORMAL = 1
    PAINTING = 2


class Painter(QPushButton, ShortcutBlockable):
    def __init__(
        self,
        toggle_palette: Callable[[], None],
        hide_palette: Callable[[], None],
        receive_pixmap: Callable[[], QPixmap | None],
        check_bound: Callable[[QPointF], bool],
        update_pixmap: Callable[[QPixmap], None],
        map_to_pixmap: Callable[[QPointF | QPoint], Tuple[float, float] | None],
        push_pixmap: Callable[[QPixmap], None],
    ) -> None:
        super().__init__()

        self.setIcon(QIcon(PAINT_ICON))
        self.setToolTip("Paint")
        self.setCheckable(True)
        self.setMouseTracking(True)

        self.__toggle_palette = toggle_palette
        self.__hide_palette = hide_palette
        self.__map_to_pixmap = map_to_pixmap
        self.__update_pixmap = update_pixmap
        self.__check_bound = check_bound
        self.__receive_pixmap = receive_pixmap
        self.__push_pixmap = push_pixmap
        self.__last_pos = None

        self.__is_active = False
        self.__mouse_state = MouseState.NORMAL
        self.__current_color = QColor("#000000")
        self.__modified_pixmap = None

    def set_color(self, color: QColor) -> None:
        """
        Change the color of the painter.
        :param color: the new color
        :type color: QtGui.QColor
        :return: None
        """
        self.__current_color = color

    def activate(self):
        """
        Activate the painter.
        :return: None
        """
        self.__is_active = True
        self.setChecked(True)
        self.__mouse_state = MouseState.NORMAL

    def deactivate(self):
        """
        Deactivate the painter.
        :return: None
        """
        self.__is_active = False
        self.setChecked(False)
        self.__mouse_state = MouseState.NORMAL
        self.__hide_palette()

    def toggle(self):
        """
        Toggle the painter.
        :return: None
        """
        if self.__is_active:
            self.deactivate()
        else:
            self.activate()

    def mousePressEvent(self, e: Optional[QMouseEvent]) -> None:
        assert e is not None
        if e.button() == Qt.MouseButton.LeftButton:
            self.toggle()
        elif e.button() == Qt.MouseButton.RightButton:
            if self.__is_active:
                self.__toggle_palette()

    def handle_mouse_movement(self, a0: QMouseEvent) -> None:
        """
        Handle the mouse movement.
        :param a0: the mouse event
        :type a0: QtGui.QMouseEvent
        :return: None
        """
        if not self.__is_active:
            return

        if self.__mouse_state == MouseState.PAINTING:
            self.__draw(a0.globalPosition())

    def on_mouse_press(self, ev: QMouseEvent) -> None:
        if not self.__is_active:
            return

        if ev.button() == Qt.MouseButton.LeftButton:
            self.__on_left_mouse_press(ev.globalPosition())
        elif ev.button() == Qt.MouseButton.RightButton:
            self.__toggle_palette()

    def __on_left_mouse_press(self, pos: QPointF) -> None:
        if not self.__check_bound(pos):
            return

        self.__mouse_state = MouseState.PAINTING
        self.block()
        self.__modified_pixmap = self.__receive_pixmap()
        if self.__modified_pixmap is None:
            return

        self.__modified_pixmap = self.__modified_pixmap.copy()
        start_pos = self.__map_to_pixmap(pos)
        if start_pos is None:
            return

        self.__last_pos = None

    def on_mouse_release(self) -> None:
        if not self.__is_active:
            return

        self.__mouse_state = MouseState.NORMAL
        self.unblock()

        if self.__modified_pixmap is None:
            return

        self.__push_pixmap(self.__modified_pixmap)
        self.__update_pixmap(self.__modified_pixmap)

        self.__modified_pixmap = None

    def __draw(self, pos: QPointF) -> None:
        if self.__modified_pixmap is None:
            return

        end_pos = self.__map_to_pixmap(pos)
        if end_pos is None:
            return

        painter = QPainter(self.__modified_pixmap)
        pen = painter.pen()
        pen.setWidth(5)
        pen.setColor(self.__current_color)
        painter.setPen(pen)
        if self.__last_pos is not None:
            painter.drawLine(QPointF(*self.__last_pos), QPointF(*end_pos))
        else:
            painter.drawPoint(QPointF(*end_pos))
        painter.end()

        self.__last_pos = end_pos

        self.__update_pixmap(self.__modified_pixmap)


class ColorPalette(QWidget):
    def __init__(self, parent: QWidget, on_select_color: Callable[[QColor], None]):
        super().__init__(parent)

        self.__parent = parent
        self.__max_preferred_width = 200
        self.__color_list: List[PaletteButton] = []
        self.__on_select_color = on_select_color
        self.init_ui()
        self.hide()

    def move_to_top_middle(self):
        """Move the palette to the top-middle of its parent."""
        max_possible_width = self.__calculate_max_width()
        parent_width = self.__parent.width()
        selected_width = min(max_possible_width, self.__max_preferred_width)

        x = (parent_width - selected_width) // 2  # Center horizontally
        y = 0  # Small margin from the top

        self.setFixedSize(selected_width, 90)
        self.move(x, y)

    def init_ui(self):
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

        content_widget = QWidget()
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 10, 0, 10)
        content_layout.setSpacing(5)

        self.__max_preferred_width = 20  # don't know why but it works

        # Define a list of colors
        colors = [
            # 17 undertones https://lospec.com/palette-list/17undertones
            "#000000",
            "#141923",
            "#414168",
            "#3a7fa7",
            "#35e3e3",
            "#8fd970",
            "#5ebb49",
            "#458352",
            "#dcd37b",
            "#fffee5",
            "#ffd035",
            "#cc9245",
            "#a15c3e",
            "#a42f3b",
            "#f45b7a",
            "#c24998",
            "#81588d",
            "#bcb0c2",
            "#ffffff",
        ]

        for color in colors:
            self.__max_preferred_width += 45  # 40 + 5 margin
            btn = PaletteButton(color, self.select_color)
            self.__color_list.append(btn)
            content_layout.addWidget(btn)

        # we cannot use activate() here because it will trigger the on_select_color, which will call painter and painter is not initialized yet
        # we need to make sure the first color in here is the same as the first color in painter
        self.__color_list[0].setChecked(True)

        content_widget.setLayout(content_layout)
        self.scroll_area.setWidget(content_widget)
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.scroll_area)
        self.setLayout(main_layout)

    def select_color(self, button: "PaletteButton"):
        for btn in self.__color_list:
            if btn != button:
                btn.deactivate()

        self.__on_select_color(QColor(button.color))

    def __calculate_max_width(self):
        parent_width = self.__parent.width()
        return parent_width * 2 // 3


class PaletteButton(QPushButton):

    def __init__(self, color: str, on_select: Callable[["PaletteButton"], None]):
        super().__init__()
        self.setFixedSize(40, 40)
        self.setCheckable(True)
        self.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {color};
                border-radius: 5px;
            }}
            QPushButton:hover {{
                border: 2px solid #fff;
            }}
            QPushButton:checked {{
                border: 4px solid #fff;
            }}
        """
        )
        self.color = color
        self.clicked.connect(self.activate)
        self.__on_select = on_select

    def activate(self):
        self.setChecked(True)
        self.__on_select(self)

    def deactivate(self):
        self.setChecked(False)
