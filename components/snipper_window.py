from typing import Callable, List, Optional, Tuple
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap, QResizeEvent
from PyQt6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QWidget,
)
from components.copy import CopyButton
from components.image_viewer import ImageViewer
from components.save import SaveButton
from definitions import ICON_DIR
import os

from components.mouse_observer import MouseObserver

APP_ICON = os.path.join(ICON_DIR, "scissors.svg")


class SnipperWindow(QMainWindow):

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Becap")
        # Not working
        icon = QIcon()
        icon.addPixmap(QPixmap(APP_ICON), QIcon.Mode.Selected, QIcon.State.On)
        self.setWindowIcon(icon)

        self.viewer = ImageViewer()
        # self.label = ImageLabel()

        self.setFixedSize(450, 100)
        self.is_expand_before = False

        self.__init_functions()
        self.__set_layout()

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

    def show_with_expand(self) -> None:
        if not self.is_expand_before:
            self.is_expand_before = True

            self.__toolbar_top.show_center_section()
            self.__toolbar_top.show_right_section()
            self.__toolbar_bottom.show()

            self.setMinimumSize(450, 500)
            self.setMaximumSize(16777215, 16777215)
            self.resize(450, 500)

        self.show()

    def resizeEvent(self, a0: Optional[QResizeEvent]) -> None:
        if not self.is_expand_before:
            return

        # Toggle middle section visibility based on window width
        # must hide first to remove widget from layout
        if self.width() < 600:  # change this number to your desired width
            self.__toolbar_top.hide_center_section()
            self.__toolbar_bottom.show()
        else:
            self.__toolbar_bottom.hide()
            self.__toolbar_top.show_center_section()

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

        # Window configuration

    def __init_functions(self) -> None:
        """
        Init the functions.
        :return: None
        """
        self.__new_capture = NewCapture(self)
        self.__mode_switching = ModeSwitching()
        self.__color_picker = ColorPicker(self)
        self.__save = SaveButton()
        self.__copy = CopyButton()


from components.color_picker import ColorPicker
from components.capture import NewCapture
from components.image_label import ImageLabel, ScrollLabel
from components.toolbar import MiddleToolBar, TopToolBar, BottomToolBar
from components.mode_switching import ModeSwitching
