from PyQt6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class SnipperWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.m_width = 400
        self.m_height = 500

        self.setWindowTitle("Snipper")
        self.setMinimumSize(self.m_width, self.m_height)

        layout = QVBoxLayout()

        self.label = ImageLabel()
        self.label.setVisible(True)

        self.btn_capture = QPushButton("Capture")
        self.btn_capture.clicked.connect(self.capture)

        self.btn_save = QPushButton("Save")
        self.btn_save.clicked.connect(self.save)
        self.btn_save.setVisible(False)

        layout.addWidget(self.btn_capture)
        layout.addWidget(self.label)
        layout.addWidget(self.btn_save)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def capture(self) -> None:
        self.capturer = Capture(self)
        self.btn_save.setVisible(True)

    def save(self) -> None:
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save Image", "", "Image files (*.png *.jpg *.bmp)"
        )

        if file_name:
            image = self.label.get_image()
            assert image is not None
            image.save(file_name)


from components.capture import Capture
from components.image_label import ImageLabel
