import sys, os

from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
)

from components import SnipperWindow, MouseObserver
from utils.styles import styles
from definitions import ICON_DIR

APP_ICON = os.path.join(ICON_DIR, "scissors.svg")


if __name__ == "__main__":
    if not (3, 10) <= sys.version_info < (3, 11):
        sys.exit(
            "This project requires Python >= 3.10 and < 3.11. Please update your Python version."
        )

    app = QApplication(sys.argv)
    icon = QIcon(APP_ICON)
    app.setStyleSheet(styles)
    w = SnipperWindow()
    w.show()

    window = w.window()
    assert window is not None

    window_handle = window.windowHandle()
    assert window_handle is not None

    mouse_observer = MouseObserver(window_handle)
    mouse_observer.subcribe(w.subscribers())

    sys.exit(app.exec())
