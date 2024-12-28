import os
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QMovie
from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout

from preload import ANIMATION_DIR

LOADING_GIF = os.path.join(ANIMATION_DIR, "loading.gif")


class LoadingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Set dialog properties
        self.setWindowTitle("Loading...")
        self.setFixedSize(200, 200)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)  # Hide the window frame
        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground
        )  # Make the window transparent

        # Layout for the dialog
        layout = QVBoxLayout()

        # Loading animation
        self.loading_label = QLabel(self)
        movie = QMovie(LOADING_GIF)
        self.loading_label.setMovie(movie)
        movie.start()

        layout.addWidget(self.loading_label)
        self.setLayout(layout)

    def show_loading(self):
        self.exec()
