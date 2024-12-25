from enum import Enum
from PyQt6.QtWidgets import QVBoxLayout, QWidget


class Mode(Enum):
    IMAGE = 1
    VIDEO = 2


class Viewer(QWidget):

    def __init__(self) -> None:
        super().__init__()

        self.__image_viewer = ImageViewer()
        self.__video_player = VideoPlayer()
        self.__mode: Mode = Mode.IMAGE

        layout = QVBoxLayout()
        layout.addWidget(self.__image_viewer)
        layout.addWidget(self.__video_player)
        self.setLayout(layout)

        self.set_mode(Mode.IMAGE)

    def set_mode(self, mode: Mode):
        self.__mode = mode

        if mode == Mode.IMAGE:
            self.__image_viewer.show()
            self.__video_player.hide()
        elif mode == Mode.VIDEO:
            self.__image_viewer.hide()
            self.__video_player.show()

    def is_in_bound(self, pos):
        if self.__mode == Mode.IMAGE:
            return self.__image_viewer.is_in_bound(pos)
        elif self.__mode == Mode.VIDEO:
            return self.__video_player.is_in_bound(pos)

    def get_original_pixmap_coords_from_global(self, pos):
        if self.__mode == Mode.IMAGE:
            return self.__image_viewer.get_original_pixmap_coords_from_global(pos)
        elif self.__mode == Mode.VIDEO:
            return self.__video_player.get_original_pixmap_coords_from_global(pos)

    def get_image(self):
        if self.__mode == Mode.IMAGE:
            return self.__image_viewer.get_image()
        elif self.__mode == Mode.VIDEO:
            return self.__video_player.get_image()

    def setPixmap(self, pixmap):
        if self.__mode == Mode.IMAGE:
            self.__image_viewer.setPixmap(pixmap)
        elif self.__mode == Mode.VIDEO:
            raise Exception("Cannot set pixmap in video mode")


from components.image_viewer import ImageViewer
from components.video_player import VideoPlayer
