import sys
import os
import json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout,
    QScrollArea, QWidget, QFileDialog, QPushButton
)
from PyQt6.QtGui import QPixmap, QKeySequence, QShortcut
from PyQt6.QtCore import Qt

class ClipboardWindow(QMainWindow):
    """
    The main window for displaying clipboard items in a scrollable horizontal layout.
    """

    def __init__(self, clipboard_widget: QWidget):
        super().__init__()
        self.setWindowTitle("Clipboard Viewer")
        self.setGeometry(150, 150, 600, 200)

        scroll_area = QScrollArea()
        scroll_area.setWidget(clipboard_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.setCentralWidget(scroll_area)

class ClipboardWidget(QWidget):
    """
    Widget to manage clipboard items and enable selection and storage of images or videos.
    """

    CLIPBOARD_DATA_FILE: str = "clipboard_data.json"

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setSpacing(10)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.setLayout(self.layout)
        self.__selected_item: QPixmap | None = None
        self.__clipboard_data: list[str] = []
        self.__load_clipboard_data()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def add_item(self, pixmap: QPixmap, file_path: str) -> None:
        """
        Add a new item to the clipboard widget.

        :param QPixmap pixmap: The pixmap to display
        :param str file_path: The file path of the item
        """
        label = QLabel()
        label.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio))
        label.setToolTip(file_path)

        label.mousePressEvent = lambda event: self.__select_item(label, pixmap)
        self.layout.addWidget(label)

        if file_path not in self.__clipboard_data:
            self.__clipboard_data.append(file_path)
            self.__save_clipboard_data()

    def __select_item(self, label: QLabel, pixmap: QPixmap) -> None:
        """
        Select an item and copy it to the system clipboard.

        :param QLabel label: The label associated with the pixmap
        :param QPixmap pixmap: The pixmap to be copied
        """
        for i in range(self.layout.count()):
            widget = self.layout.itemAt(i).widget()
            widget.setStyleSheet("")

        label.setStyleSheet("border: 2px solid blue;")
        self.__selected_item = pixmap

        clipboard = QApplication.clipboard()
        clipboard.setPixmap(pixmap)
        print("Selected image copied to clipboard.")

        clipboard_window = self.parentWidget().parentWidget().parentWidget()
        if clipboard_window:
            clipboard_window.hide()

    def __save_clipboard_data(self) -> None:
        """
        Save the clipboard data to a JSON file.
        """
        with open(self.CLIPBOARD_DATA_FILE, "w") as file:
            json.dump(self.__clipboard_data, file)

    def __load_clipboard_data(self) -> None:
        """
        Load clipboard data from a JSON file.
        """
        if os.path.exists(self.CLIPBOARD_DATA_FILE):
            with open(self.CLIPBOARD_DATA_FILE, "r") as file:
                self.__clipboard_data = json.load(file)
                for file_path in self.__clipboard_data:
                    if os.path.exists(file_path):
                        if file_path.lower().endswith((".png", ".jpg", ".jpeg")):
                            pixmap = QPixmap(file_path)
                            self.add_item(pixmap, file_path)
                        elif file_path.lower().endswith((".mp4", ".avi", ".mkv")):
                            video_icon = QPixmap(100, 100)
                            video_icon.fill(Qt.GlobalColor.black)
                            self.add_item(video_icon, file_path)

class MainWindow(QMainWindow):
    """
    The main application window for managing screenshots and clipboard items.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Snipping Tool with Clipboard")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.main_layout = QVBoxLayout(self.central_widget)
        self.setCentralWidget(self.central_widget)

        self.capture_display = QLabel("Capture Area")
        self.capture_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.capture_display.setStyleSheet("border: 2px dashed gray; height: 400px;")
        self.main_layout.addWidget(self.capture_display)

        capture_image_button = QPushButton("Capture Image")
        capture_image_button.clicked.connect(self.__capture_image)

        capture_video_button = QPushButton("Capture Video")
        capture_video_button.clicked.connect(self.__capture_video)

        button_layout = QHBoxLayout()
        button_layout.addWidget(capture_image_button)
        button_layout.addWidget(capture_video_button)
        self.main_layout.addLayout(button_layout)

        self.__clipboard_widget = ClipboardWidget()
        self.__clipboard_window = ClipboardWindow(self.__clipboard_widget)

        clipboard_shortcut = QShortcut(QKeySequence("Ctrl+Shift+V"), self)
        clipboard_shortcut.activated.connect(self.__show_clipboard_window)

    def __show_clipboard_window(self) -> None:
        """
        Show the clipboard window.
        """
        self.__clipboard_window.show()

    def __capture_image(self) -> None:
        """
        Capture an image and add it to the clipboard.
        """
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            pixmap = QPixmap(file_path)
            self.capture_display.setPixmap(pixmap.scaled(400, 300, Qt.AspectRatioMode.KeepAspectRatio))
            self.__clipboard_widget.add_item(pixmap, file_path)

    def __capture_video(self) -> None:
        """
        Capture a video and add it to the clipboard.
        """
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Video", "", "Videos (*.mp4 *.avi *.mkv)")
        if file_path:
            self.capture_display.setText(f"Video: {file_path}")
            video_icon = QPixmap(100, 100)
            video_icon.fill(Qt.GlobalColor.black)
            self.__clipboard_widget.add_item(video_icon, file_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
