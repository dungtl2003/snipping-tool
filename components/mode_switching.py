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

        self.camera_mode_btn = QPushButton(QIcon(CAMERA_MODE_ICON), "")
        self.camera_mode_btn.setToolTip("Camera mode")
        self.camera_mode_btn.setStyleSheet(btn_style)
        self.camera_mode_btn.setCheckable(True)
        self.camera_mode_btn.setChecked(True)

        self.video_mode_btn = QPushButton(QIcon(VIDEO_MODE_ICON), "")
        self.video_mode_btn.setToolTip("Video mode")
        self.video_mode_btn.setStyleSheet(btn_style)
        self.video_mode_btn.setCheckable(True)

        self.__mode = self.Mode.CAMERA

        self.camera_mode_btn.clicked.connect(
            lambda: self.__switch_mode(self.Mode.CAMERA)
        )
        self.video_mode_btn.clicked.connect(lambda: self.__switch_mode(self.Mode.VIDEO))

        layout.addWidget(self.camera_mode_btn)
        layout.addWidget(self.video_mode_btn)

        self.setLayout(layout)

    def mode(self) -> Mode:
        """Return the current mode."""
        return self.__mode

    def __switch_mode(self, mode: Mode) -> None:
        """Handle mode switching logic."""
        if mode == self.Mode.CAMERA:
            self.camera_mode_btn.setChecked(True)
            self.video_mode_btn.setChecked(False)
        else:
            self.camera_mode_btn.setChecked(False)
            self.video_mode_btn.setChecked(True)

        self.__mode = mode
