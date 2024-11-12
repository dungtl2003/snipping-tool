from typing import Callable, List, Tuple
from PyQt6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from components.mouse_observer import MouseObserver


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

        self.color_picker = ColorPicker(self)
        self.btn_pick_color = QPushButton("Pick Color")
        self.btn_pick_color.clicked.connect(self.toggle_color_picker)

        self.btn_capture = QPushButton("Capture")
        self.btn_capture.clicked.connect(self.capture)

        self.btn_save = QPushButton("Save")
        self.btn_save.clicked.connect(self.save)
        self.btn_save.setVisible(False)

        layout.addWidget(self.btn_capture)
        layout.addWidget(self.btn_pick_color)
        layout.addWidget(self.label)
        layout.addWidget(self.btn_save)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def subscribers(
        self,
    ) -> List[Tuple[Callable[..., None], MouseObserver.SubscribeEvent]]:
        """
        Return the subscribers.
        :return: the subscribers
        :rtype: List[Tuple[Callable[..., None], MouseObserver.SubscribeEvent]]
        """
        return [
            (self.color_picker.pick_color, MouseObserver.SubscribeEvent.PRESSED),
            (
                self.color_picker.handle_mouse_movement,
                MouseObserver.SubscribeEvent.MOVED,
            ),
        ]

    def toggle_color_picker(self) -> None:
        """
        Toggle the color picker.
        :return: None
        """
        self.color_picker.toggle()

    def capture(self) -> None:
        """
        Capture the screen.
        Note that when capturing, no other actions can be performed.
        :return: None
        """
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


from components.color_picker import ColorPicker
from components.capture import Capture
from components.image_label import ImageLabel
