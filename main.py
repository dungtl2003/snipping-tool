import sys
import os

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication,
)

from components import SnipperWindow, MouseObserver
from utils.styles import styles
from definitions import ICON_DIR
from globals import kill_all_processes

APP_ICON = os.path.join(ICON_DIR, "scissors.svg")


def error_handler(etype, value, tb):
    print(f"An error occurred: {value}")
    print("Killing all processes")
    kill_all_processes()
    exit(1)


if __name__ == "__main__":
    if not (3, 10) <= sys.version_info < (3, 11):
        sys.exit(
            "This project requires Python >= 3.10 and < 3.11. Please update your Python version."
        )

    sys.excepthook = error_handler  # redirect std error

    try:
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
    except Exception as e:
        print(f"Error on main process: {e}")
        kill_all_processes()

        sys.exit(1)
