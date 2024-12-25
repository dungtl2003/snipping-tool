from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QSizePolicy, QToolBar, QWidget

from utils.styles import qtoolbar_style
from components.mode_switching import ModeSwitching
from components.capture import NewCapture
from components.color_picker import ColorPicker
from components.save import SaveButton
from components.copy_btn import CopyButton

import os
from preload import ICON_DIR

MORE_ICON = os.path.join(ICON_DIR, "more.svg")


class BaseToolBar(QToolBar):
    def __init__(self) -> None:
        super().__init__()

        self.setMovable(False)
        self.setStyleSheet(qtoolbar_style)


class MiddleToolBar(BaseToolBar):
    def __init__(
        self,
        eye_dropper: ColorPicker,
    ) -> None:
        super().__init__()

        self.setStyleSheet("QToolBar { padding: 0px; }")

        left_spacer = QWidget()
        left_spacer.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        right_spacer = QWidget()
        right_spacer.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(left_spacer)
        layout.addWidget(eye_dropper)
        layout.addWidget(right_spacer)

        widget = QWidget()
        widget.setLayout(layout)
        self.addWidget(widget)


class TopToolBar(BaseToolBar):
    # new     | mode |       eye dropper
    def __init__(
        self,
        new_capture: NewCapture,
        mode_switching: ModeSwitching,
        middle_toolbar: MiddleToolBar,
        save: SaveButton,
        copy: CopyButton,
    ) -> None:
        super().__init__()

        self.__new_capture = new_capture
        self.__mode_switching = mode_switching
        self.__middle_toolbar = middle_toolbar
        self.__save = save
        self.__copy = copy

        self.__spacer = QWidget()
        self.__spacer.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        self.__add_left_section()
        self.__add_center_section()
        self.__add_right_section()

        self.hide_center_section()
        self.hide_right_section()

    def __add_center_section(self):
        self.__middle_layout = QHBoxLayout()
        self.__middle_layout.setContentsMargins(0, 0, 0, 0)
        self.__middle_layout.addWidget(self.__middle_toolbar)

        middle_widget = QWidget()
        middle_widget.setLayout(self.__middle_layout)
        self.addWidget(middle_widget)

    def show_center_section(self) -> None:
        """
        Show the center section.
        :return: None
        """
        self.__middle_layout.removeWidget(self.__spacer)
        self.__middle_layout.addWidget(self.__middle_toolbar)

    def hide_center_section(self) -> None:
        """
        Hide the center section.
        :return: None
        """
        self.__middle_layout.removeWidget(self.__middle_toolbar)
        self.__middle_layout.addWidget(self.__spacer)

    def show_right_section(self) -> None:
        """
        Show the right section.
        :return: None
        """
        self.__right_toolbar.show()

    def hide_right_section(self) -> None:
        """
        Hide the right section.
        :return: None
        """
        self.__right_toolbar.hide()

    def show_left_section(self) -> None:
        """
        Show the left section.
        :return: None
        """
        self.__left_toolbar.show()

    def hide_left_section(self) -> None:
        """
        Hide the left section.
        :return: None
        """
        self.__left_toolbar.hide()

    # save copy | more
    def __add_right_section(self):
        self.__right_toolbar = QToolBar()
        self.__right_toolbar.setMovable(False)
        self.__right_toolbar.setStyleSheet("QToolBar { padding: 0px; }")

        # Save
        self.__right_toolbar.addWidget(self.__save)

        # Space
        space = QWidget()
        space.setFixedSize(3, 3)
        self.__right_toolbar.addWidget(space)

        # Copy
        self.__right_toolbar.addWidget(self.__copy)

        # Space
        space = QWidget()
        space.setFixedSize(10, 10)
        self.__right_toolbar.addWidget(space)

        # |
        self.__right_toolbar.addSeparator()

        # Space
        space = QWidget()
        space.setFixedSize(10, 10)
        self.__right_toolbar.addWidget(space)

        # More
        more_button = QPushButton(QIcon(MORE_ICON), "")
        self.__right_toolbar.addWidget(more_button)

        right_layout = QHBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.addWidget(self.__right_toolbar)

        right_widget = QWidget()
        right_widget.setLayout(right_layout)

        self.addWidget(right_widget)

    # new  |  mode
    def __add_left_section(self):
        self.__left_toolbar = QToolBar()
        self.__left_toolbar.setMovable(False)
        self.__left_toolbar.setStyleSheet("QToolBar { padding: 0px; }")

        # New
        self.__left_toolbar.addWidget(self.__new_capture)

        # Space
        space = QWidget()
        space.setFixedSize(10, 10)
        self.__left_toolbar.addWidget(space)

        # |
        self.__left_toolbar.addSeparator()

        # Space
        space = QWidget()
        space.setFixedSize(10, 10)
        self.__left_toolbar.addWidget(space)

        # Mode
        self.__left_toolbar.addWidget(self.__mode_switching)

        left_layout = QHBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(self.__left_toolbar)

        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        self.addWidget(left_widget)


class BottomToolBar(BaseToolBar):
    # eye dropper
    def __init__(
        self,
        middle_toolbar: MiddleToolBar,
    ) -> None:
        super().__init__()

        self.__middle_toolbar = middle_toolbar
        self.__layout = QHBoxLayout()
        self.__layout.setContentsMargins(0, 0, 0, 0)
        self.__layout.addWidget(self.__middle_toolbar)

        widget = QWidget()
        widget.setLayout(self.__layout)
        self.addWidget(widget)

        self.hide()

    def show(self) -> None:
        """
        Show the middle section.
        :return: None
        """
        self.__layout.addWidget(self.__middle_toolbar)
        return super().show()

    def hide(self) -> None:
        """
        Hide the middle section.
        :return: None
        """
        self.__layout.removeWidget(self.__middle_toolbar)
        return super().hide()
