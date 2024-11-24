from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QPushButton

import os
from definitions import ICON_DIR

SAVE_ICON = os.path.join(ICON_DIR, "save.svg")


class SaveButton(QPushButton):
    def __init__(self) -> None:
        super().__init__(QIcon(SAVE_ICON), "")

        self.setToolTip("Save")
        self.clicked.connect(self.__save)

    def __save(self):
        print("Save button clicked")
