from enum import Enum
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QWidget

import os
from preload import ICON_DIR
from utils.styles import qpushbutton_style

CAMERA_MODE_ICON = os.path.join(ICON_DIR, "camera-mode.svg")
VIDEO_MODE_ICON = os.path.join(ICON_DIR, "video-mode.svg")

btn_style: str = "".join(
    (
        qpushbutton_style,
        """
    QPushButton {
        background-color: #503e3e; /* Button background for QAction */
    }
""",
    )
)


class ModeSwitching(QWidget):
    class Mode(Enum):
        CAMERA = 0
        VIDEO = 1

    def __init__(self) -> None:
        super().__init__()

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.show()

        self.__camera_mode_action = QPushButton(QIcon(CAMERA_MODE_ICON), "")
        self.__camera_mode_action.setToolTip("Camera mode")
        self.__camera_mode_action.setStyleSheet(btn_style)
        self.__camera_mode_action.setCheckable(True)
        self.__camera_mode_action.setChecked(True)

        self.__video_mode_action = QPushButton(QIcon(VIDEO_MODE_ICON), "")
        self.__video_mode_action.setToolTip("Video mode")
        self.__video_mode_action.setStyleSheet(btn_style)
        self.__video_mode_action.setCheckable(True)

        self.__mode = self.Mode.CAMERA

        self.__camera_mode_action.clicked.connect(
            lambda: self.__switch_mode(self.Mode.CAMERA)
        )
        self.__video_mode_action.clicked.connect(
            lambda: self.__switch_mode(self.Mode.VIDEO)
        )

        layout.addWidget(self.__camera_mode_action)
        layout.addWidget(self.__video_mode_action)

        self.setLayout(layout)

    def mode(self) -> Mode:
        """Return the current mode."""
        return self.__mode

    def __switch_mode(self, mode: Mode) -> None:
        """Handle mode switching logic."""
        if mode == self.Mode.CAMERA:
            self.__camera_mode_action.setChecked(True)
            self.__video_mode_action.setChecked(False)
        else:
            self.__camera_mode_action.setChecked(False)
            self.__video_mode_action.setChecked(True)

        self.__mode = mode
