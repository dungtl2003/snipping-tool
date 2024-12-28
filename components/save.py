from typing import Callable
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QPushButton

import os
from preload import ICON_DIR

SAVE_ICON = os.path.join(ICON_DIR, "save.svg")
TICK_ICON = os.path.join(ICON_DIR, "tick.svg")


class SaveButton(QPushButton):
    def __init__(self, on_save_event: Callable[[], None]) -> None:
        super().__init__(QIcon(SAVE_ICON), "")

        self.setToolTip("Save")
        self.clicked.connect(self.__save)

        self.__on_save_event = on_save_event

    def __save(self):
        self.__animate_button()
        self.__on_save_event()

    def enable(self):
        self.setEnabled(True)

    def disable(self):
        self.setEnabled(False)

    def __animate_button(self):
        # Change to "tick" icon
        self.setIcon(QIcon(TICK_ICON))

        QTimer.singleShot(1000, self.__reset_icon)

    def __reset_icon(self):
        self.setIcon(QIcon(SAVE_ICON))
