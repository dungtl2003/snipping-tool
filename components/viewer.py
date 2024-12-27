from enum import Enum
from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QVBoxLayout, QWidget

from components.image_viewer import ImageViewer
from components.video_player import VideoPlayer


class Mode(Enum):
    IMAGE = 1
    VIDEO = 2


class Viewer(QWidget):

    def __init__(self) -> None:
        super().__init__()

        self.__image_viewer = ImageViewer()
        self.__video_player = VideoPlayer()
        self.mode: Mode = Mode.IMAGE

        layout = QVBoxLayout()
        layout.addWidget(self.__image_viewer)
        layout.addWidget(self.__video_player)
        self.setLayout(layout)

        self.set_mode(Mode.IMAGE)

    def save(self):
        if self.mode == Mode.IMAGE:
            self.__image_viewer.save()
        elif self.mode == Mode.VIDEO:
            self.__video_player.save()

    def get_pixmap(self) -> QPixmap | None:
        if self.mode == Mode.IMAGE:
            return self.__image_viewer.get_original_pixmap()
        elif self.mode == Mode.VIDEO:
            raise Exception("Cannot get pixmap in video mode")

        raise Exception("Unknown mode")

    def set_mode(self, mode: Mode):
        self.mode = mode

        if mode == Mode.IMAGE:
            self.__image_viewer.show()
            self.__video_player.hide()
        elif mode == Mode.VIDEO:
            self.__image_viewer.hide()
            self.__video_player.show()

    def is_in_bound(self, pos: QPointF) -> bool:
        if self.mode == Mode.IMAGE:
            return self.__image_viewer.is_in_bound(pos)
        elif self.mode == Mode.VIDEO:
            raise Exception("Cannot check in bound in video mode")

        raise Exception("Unknown mode")

    def is_in_viewer_bound(self, pos: QPointF) -> bool:
        local_pos = self.mapFromGlobal(pos)

        if (
            local_pos.x() < 0
            or local_pos.y() < 0
            or local_pos.x() > self.width()
            or local_pos.y() > self.height()
        ):
            return False

        return True

    def get_original_pixmap_coords_from_global(self, pos):
        if self.mode == Mode.IMAGE:
            return self.__image_viewer.get_original_pixmap_coords_from_global(pos)
        elif self.mode == Mode.VIDEO:
            raise Exception("Cannot get original pixmap coords in video mode")

    def get_image(self):
        if self.mode == Mode.IMAGE:
            return self.__image_viewer.get_image()
        elif self.mode == Mode.VIDEO:
            raise Exception("Cannot get image in video mode")

    def set_pixmap(self, pixmap):
        if self.mode == Mode.IMAGE:
            self.__image_viewer.set_pixmap(pixmap)
        elif self.mode == Mode.VIDEO:
            raise Exception("Cannot set pixmap in video mode")

    def set_video(self, video_path: str):
        if self.mode == Mode.VIDEO:
            self.__video_player.set_video(video_path)
        elif self.mode == Mode.IMAGE:
            raise Exception("Cannot set video in image mode")
