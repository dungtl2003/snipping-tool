from typing import Callable
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QPushButton

import os
from preload import ICON_DIR

COPY_ICON = os.path.join(ICON_DIR, "copy.svg")
TICK_ICON = os.path.join(ICON_DIR, "tick.svg")


class CopyButton(QPushButton):
    def __init__(self, on_copy_event: Callable[[], None]) -> None:
        super().__init__(QIcon(COPY_ICON), "")

        self.setToolTip("Copy")
        self.clicked.connect(self.__copy)

        self.__on_copy_event = on_copy_event

    def __copy(self):
        self.__animate_button()
        self.__on_copy_event()

    def __animate_button(self):
        # Change to "tick" icon
        self.setIcon(QIcon(TICK_ICON))

        # Set a timer to revert the icon back to "copy"
        QTimer.singleShot(1000, self.__reset_icon)

    def __reset_icon(self):
        # Revert to the original "copy" icon
        self.setIcon(QIcon(COPY_ICON))
