from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QPushButton

import os
from preload import ICON_DIR

COPY_ICON = os.path.join(ICON_DIR, "copy.svg")


class CopyButton(QPushButton):
    def __init__(self) -> None:
        super().__init__(QIcon(COPY_ICON), "")

        self.setToolTip("Copy")
        self.clicked.connect(self.__copy)

    def __copy(self):
        print("Copy button clicked")
