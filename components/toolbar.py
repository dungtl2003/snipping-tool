from PyQt6.QtWidgets import QHBoxLayout, QSizePolicy, QToolBar, QWidget

from components.blur import Blur
from components.painter import Painter
from components.upload import UploadButton
from components.zoom import Zoom
from utils.styles import qtoolbar_style
from components.mode_switching import ModeSwitching
from components.capture import NewCapture
from components.color_picker import ColorPicker
from components.save import SaveButton
from components.copy_btn import CopyButton


class BaseToolBar(QToolBar):
    def __init__(self) -> None:
        super().__init__()

        self.setMovable(False)
        self.setStyleSheet(qtoolbar_style)


class MiddleToolBar(BaseToolBar):
    def __init__(
        self, eye_dropper: ColorPicker, blur_btn: Blur, zoom: Zoom, painter: Painter
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
        layout.addWidget(blur_btn)
        layout.addWidget(painter)
        layout.addWidget(right_spacer)
        layout.addWidget(zoom)

        widget = QWidget()
        widget.setLayout(layout)
        self.addWidget(widget)

        self.__eye_dropper = eye_dropper
        self.__blur_btn = blur_btn
        self.__painter = painter

        self.__eye_dropper.toggled.connect(self.__on_eye_dropper_toggled)
        self.__blur_btn.toggled.connect(self.__on_blur_toggled)
        self.__painter.toggled.connect(self.__on_paint_toggled)

    def __on_paint_toggled(self) -> None:
        """
        Handle the paint toggled.
        :return: None
        """
        if self.__painter.isChecked():
            self.__eye_dropper.deactivate()
            self.__blur_btn.deactivate()

    def __on_eye_dropper_toggled(self) -> None:
        """
        Handle the eye dropper toggled.
        :return: None
        """
        if self.__eye_dropper.isChecked():
            self.__blur_btn.deactivate()
            self.__painter.deactivate()

    def __on_blur_toggled(self) -> None:
        """
        Handle the blur toggled.
        :return: None
        """
        if self.__blur_btn.isChecked():
            self.__eye_dropper.deactivate()
            self.__painter.deactivate()


class TopToolBar(BaseToolBar):
    def __init__(
        self,
        new_capture: NewCapture,
        mode_switching: ModeSwitching,
        middle_toolbar: MiddleToolBar,
        save: SaveButton,
        copy: CopyButton,
        upload: UploadButton,
    ) -> None:
        super().__init__()

        self.__new_capture_btn = new_capture
        self.__mode_switching = mode_switching
        self.__middle_toolbar = middle_toolbar
        self.__save_btn = save
        self.__copy_btn = copy
        self.__upload_btn = upload

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

    #  save copy | upload
    def __add_right_section(self):
        self.__right_toolbar = QToolBar()
        self.__right_toolbar.setMovable(False)
        self.__right_toolbar.setStyleSheet("QToolBar { padding: 0px; }")

        # Space
        space = QWidget()
        space.setFixedSize(30, 30)
        self.__right_toolbar.addWidget(space)

        # Save
        self.__right_toolbar.addWidget(self.__save_btn)

        # Space
        space = QWidget()
        space.setFixedSize(3, 3)
        self.__right_toolbar.addWidget(space)

        # Copy
        self.__right_toolbar.addWidget(self.__copy_btn)

        # Space
        space = QWidget()
        space.setFixedSize(10, 10)
        self.__right_toolbar.addWidget(space)

        # Separator
        self.__right_toolbar.addSeparator()

        # Space
        space = QWidget()
        space.setFixedSize(10, 10)
        self.__right_toolbar.addWidget(space)

        # Upload
        self.__right_toolbar.addWidget(self.__upload_btn)

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
        self.__left_toolbar.addWidget(self.__new_capture_btn)

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

        # Space
        space = QWidget()
        space.setFixedSize(30, 30)
        self.__left_toolbar.addWidget(space)


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
