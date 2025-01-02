from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout


class CustomInformationDialog(QDialog):
    def __init__(self, title: str, message: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(400, 200)  # Set a fixed size for the dialog
        self.setStyleSheet(
            """
            QDialog {
                background-color: #3b4252;  /* Dark background */
                border: 1px solid #4c566a; /* Subtle border */
                border-radius: 10px;
            }
            QLabel {
                color: #d8dee9;           /* Text color */
            }
            QPushButton {
                background-color: #88c0d0; /* Button background */
                color: #2e3440;           /* Button text */
                border: 1px solid #81a1c1;
                border-radius: 5px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #81a1c1; /* Hover effect */
            }
        """
        )
        self.init_ui(message)

    def init_ui(self, message: str):
        # Create the layout
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        # Create and style the icon label
        icon_label = QLabel()
        icon_label.setPixmap(QIcon.fromTheme("dialog-information").pixmap(48, 48))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)

        # Create and style the message label
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont("Arial", 12)
        font.setBold(True)
        message_label.setFont(font)
        layout.addWidget(message_label)

        # Create the "OK" button
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        ok_button.setFixedWidth(80)
        ok_button.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(ok_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # Apply the layout
        self.setLayout(layout)


class CustomCriticalDialog(QDialog):
    def __init__(self, title: str, message: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(400, 200)  # Set a fixed size for the dialog
        self.setStyleSheet(
            """
            QDialog {
                background-color: #2e3440;  /* Dark theme background */
                border: 1px solid #4c566a; /* Subtle border */
                border-radius: 10px;
            }
            QLabel {
                color: #d8dee9;           /* Text color */
            }
            QPushButton {
                background-color: #bf616a; /* Button background */
                color: #eceff4;           /* Button text */
                border: 1px solid #d08770;
                border-radius: 5px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #d08770; /* Hover effect */
            }
        """
        )
        self.setModal(True)
        self.init_ui(message)

    def init_ui(self, message: str):
        # Create the layout
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        # Create and style the icon label
        icon_label = QLabel()
        icon_label.setPixmap(QIcon.fromTheme("dialog-error").pixmap(48, 48))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)

        # Create and style the message label
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont("Arial", 12)
        font.setBold(True)
        message_label.setFont(font)
        layout.addWidget(message_label)

        # Create the "OK" button
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        ok_button.setFixedWidth(80)
        ok_button.setCursor(Qt.CursorShape.PointingHandCursor)
        # ok_button.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(ok_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # Apply the layout
        self.setLayout(layout)
