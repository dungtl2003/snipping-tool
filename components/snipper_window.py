import time
from typing import Callable, List, Optional, Tuple
from PyQt6.QtCore import QMetaObject, QRect, Qt
from PyQt6.QtGui import QIcon, QKeySequence, QPixmap, QResizeEvent, QShortcut
from PyQt6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QWidget,
)
from components.clipboard_manager import ClipboardManager
from components.copy_btn import CopyButton
from components.save import SaveButton
from preload import ICON_DIR, APP_NAME
import os

from components.mouse_observer import MouseObserver
from components.color_picker import ColorPicker
from components.capture import NewCapture
from components.toolbar import MiddleToolBar, TopToolBar, BottomToolBar
from components.mode_switching import ModeSwitching
from components.video_recorder import VideoRecorder
from components.viewer import Viewer, Mode

APP_ICON = os.path.join(ICON_DIR, "scissors.svg")


class SnipperWindow(QMainWindow):

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle(APP_NAME)
        # Not working
        icon = QIcon()
        icon.addPixmap(QPixmap(APP_ICON), QIcon.Mode.Selected, QIcon.State.On)
        self.setWindowIcon(icon)

        self.viewer = Viewer()
        self.__clipboard_manager = ClipboardManager()

        self.setFixedSize(450, 100)
        self.is_expand_before = False

        self.__init_functions()
        self.__set_layout()

        self.__setup_shortcut()

    def subscribers(
        self,
    ) -> List[Tuple[Callable[..., None], MouseObserver.SubscribeEvent]]:
        """
        Return the subscribers.
        :return: the subscribers
        :rtype: List[Tuple[Callable[..., None], MouseObserver.SubscribeEvent]]
        """
        return [
            (self.__color_picker.pick_color, MouseObserver.SubscribeEvent.PRESSED),
            (
                self.__color_picker.handle_mouse_movement,
                MouseObserver.SubscribeEvent.MOVED,
            ),
        ]

    def resizeEvent(self, a0: Optional[QResizeEvent]) -> None:
        if not self.is_expand_before:
            return

        self.__set_dynamic_size()

    def __set_dynamic_size(self) -> None:
        if (
            self.viewer.mode == Mode.IMAGE
        ):  # only in image mode we need to toggle the middle section
            # Toggle middle section visibility based on window width
            # must hide first to remove widget from layout
            self.__middle_toolbar.show()
            if self.width() < 600:  # change this number to your desired width
                self.__toolbar_top.hide_center_section()
                self.__toolbar_bottom.show()
            else:
                self.__toolbar_bottom.hide()
                self.__toolbar_top.show_center_section()
        elif self.viewer.mode == Mode.VIDEO:
            self.__color_picker.set_active(False)
            self.__toolbar_bottom.hide()
            self.__toolbar_top.hide_center_section()
            self.__middle_toolbar.hide()

    def __show_with_expand(self) -> None:
        if not self.is_expand_before:
            self.__toolbar_top.show_right_section()
            self.is_expand_before = True
            self.setMinimumSize(450, 500)
            self.setMaximumSize(16777215, 16777215)
            self.resize(450, 500)
        else:
            self.__set_dynamic_size()

        self.show()

    def __set_layout(self) -> None:
        """
        Set the layout.
        :return: None
        """
        # Main central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Main layout
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.__middle_toolbar = MiddleToolBar(self.__color_picker)

        # Toolbar (at the top)
        self.__toolbar_top = TopToolBar(
            self.__new_capture,
            self.__mode_switching,
            self.__middle_toolbar,
            self.__save,
            self.__copy,
        )
        # Main section
        self.viewer.setVisible(True)
        # Toolbar (at the bottom)
        self.__toolbar_bottom = BottomToolBar(self.__middle_toolbar)

        # Create a QScrollArea and set the QLabel as its widget
        self.main_layout.addWidget(
            self.__toolbar_top, alignment=Qt.AlignmentFlag.AlignTop
        )
        self.main_layout.addWidget(self.viewer)
        self.main_layout.addWidget(
            self.__toolbar_bottom, alignment=Qt.AlignmentFlag.AlignBottom
        )

    def __init_functions(self) -> None:
        """
        Init the functions.
        :return: None
        """
        self.__new_capture = NewCapture(self.__on_pre_capture, self.__on_post_capture)
        self.__mode_switching = ModeSwitching()
        self.__color_picker = ColorPicker(self.viewer)
        self.__save = SaveButton(self.__on_save)
        self.__copy = CopyButton(self.__on_copy)

    def __on_save(self) -> None:
        self.viewer.save()

    def __on_copy(self) -> None:
        img = self.viewer.copy_to_clipboard()
        self.__clipboard_manager.add_item(img)

    def __on_pre_capture(self) -> None:
        self.hide()
        time.sleep(0.2)  # wait for main screen to hide

    def __on_post_capture(
        self,
        capture_result: Tuple[QRect, QPixmap] | None,
    ) -> None:
        if capture_result is None:
            self.show()
            return

        capture_area, capture_pixmap = capture_result
        if self.__mode_switching.mode() == ModeSwitching.Mode.CAMERA:
            self.viewer.set_mode(Mode.IMAGE)
            self.viewer.setPixmap(capture_pixmap)
            self.__show_with_expand()
        elif self.__mode_switching.mode() == ModeSwitching.Mode.VIDEO:
            self.viewer.set_mode(Mode.VIDEO)

            self.video_recorder = VideoRecorder(
                capture_area, self.__on_post_video_recording
            )
            self.video_recorder.start_recording()

    def __on_post_video_recording(self) -> None:
        self.viewer.set_video(self.video_recorder.video_file_path)
        self.__show_with_expand()

    def __setup_shortcut(self):
        shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        shortcut.activated.connect(self.__new_capture.capture)

        shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        shortcut.activated.connect(self.close)

    def toggle_clipboard_manager(self):
        QMetaObject.invokeMethod(self.__clipboard_manager, "toggle")
