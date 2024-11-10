import sys

from PyQt6.QtWidgets import (
    QApplication,
)

from components.snipper_window import SnipperWindow


if __name__ == "__main__":
    if not (3, 10) <= sys.version_info < (3, 11):
        sys.exit(
            "This project requires Python >= 3.10 and < 3.11. Please update your Python version."
        )

    app = QApplication(sys.argv)
    app.setStyleSheet(
        """
    QFrame {
        background-color: #3f3f3f;
    }
    QPushButton {
        border-radius: 5px;
        background-color: rgb(60, 90, 255);
        padding: 10px;
        color: white;
        font-weight: bold;
        font-family: Arial;
        font-size: 12px;
    }
    QPushButton::hover {
        background-color: rgb(60, 20, 255)
    }
    """
    )
    window = SnipperWindow()
    window.show()
    sys.exit(app.exec())
