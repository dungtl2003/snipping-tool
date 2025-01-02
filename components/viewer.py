from enum import Enum
from typing import Callable, Optional, Tuple
from PyQt6.QtCore import QPoint, QPointF
from PyQt6.QtGui import QColor, QImage, QPixmap, QResizeEvent
from PyQt6.QtWidgets import QVBoxLayout, QWidget

from components.image_viewer import ImageViewer
from components.painter import ColorPalette
from components.video_player import VideoPlayer


class Mode(Enum):
    IMAGE = 1
    VIDEO = 2


class Viewer(QWidget):

    def __init__(
        self,
        on_wheel_zoom_event: Callable[[float], None],
        on_select_color: Callable[[QColor], None],
    ) -> None:
        super().__init__()

        self.__image_viewer = ImageViewer(on_wheel_zoom_event)
        self.__video_player = VideoPlayer()
        self.mode: Mode = Mode.IMAGE

        layout = QVBoxLayout()
        layout.addWidget(self.__image_viewer)
        layout.addWidget(self.__video_player)
        self.setLayout(layout)
        self.color_palette = ColorPalette(self, on_select_color)

        self.set_mode(Mode.IMAGE)

    def resizeEvent(self, a0: Optional[QResizeEvent]) -> None:
        self.color_palette.move_to_top_middle()
        self.color_palette.update()

    def hide_palette(self) -> None:
        """
        Hide the color palette.

        :return: None
        """
        self.color_palette.hide()

    def show_palette(self) -> None:
        """
        Show the color palette.

        :return: None
        """
        self.color_palette.show()

    def toggle_palette(self) -> None:
        """
        Toggle the color palette visibility.

        :return: None
        """
        if self.color_palette.isVisible():
            self.color_palette.hide()
        else:
            self.color_palette.show()

    def save(self):
        """
        Save the current image or video.

        :return: None
        """
        if self.mode == Mode.IMAGE:
            self.__image_viewer.save()
        elif self.mode == Mode.VIDEO:
            self.__video_player.save()

    def zoom_pixmap_in(self) -> float:
        """
        Zoom in the pixmap in the viewer.

        :return: The new zoom level
        :rtype: float
        """
        if self.mode == Mode.IMAGE:
            return self.__image_viewer.zoom_in()
        elif self.mode == Mode.VIDEO:
            raise Exception("Cannot zoom in video")

        raise Exception("Unknown mode")

    def zoom_pixmap_out(self) -> float:
        """
        Zoom out the pixmap in the viewer.

        :return: The new zoom level
        :rtype: float
        """
        if self.mode == Mode.IMAGE:
            return self.__image_viewer.zoom_out()
        elif self.mode == Mode.VIDEO:
            raise Exception("Cannot zoom out video")

        raise Exception("Unknown mode")

    def reset_zoom(self) -> float:
        """
        Reset the zoom of the pixmap in the viewer.

        :return: The new zoom level
        :rtype: float
        """
        if self.mode == Mode.IMAGE:
            return self.__image_viewer.reset_zoom()
        elif self.mode == Mode.VIDEO:
            raise Exception("Cannot reset zoom in video")

        raise Exception("Unknown mode")

    def get_pixmap(self) -> QPixmap | None:
        """
        Get the pixmap if the viewer is in image mode. Otherwise, raise an exception.

        :return: The pixmap
        :rtype: QPixmap | None
        """
        if self.mode == Mode.IMAGE:
            return self.__image_viewer.get_original_pixmap()
        elif self.mode == Mode.VIDEO:
            raise Exception("Cannot get pixmap in video mode")

        raise Exception("Unknown mode")

    def set_mode(self, mode: Mode) -> None:
        """
        Set the viewer mode.

        :param mode: The mode to set
        :type mode: Mode
        :return: None
        """
        self.mode = mode

        if mode == Mode.IMAGE:
            self.__image_viewer.show()
            self.__video_player.hide()
        elif mode == Mode.VIDEO:
            self.__image_viewer.hide()
            self.__video_player.show()

    def get_video_path(self) -> str:
        """
        Get the video path if the viewer is in video mode. Otherwise, raise an exception.

        :return: The video path
        :rtype: str
        """
        if self.mode == Mode.VIDEO:
            return self.__video_player.video_path
        elif self.mode == Mode.IMAGE:
            raise Exception("Cannot get video path in image mode")

        raise Exception("Unknown mode")

    def is_in_pixmap_bound(self, pos: QPointF) -> bool:
        """
        Check if the given position is in bound of the image viewer.

        :param pos: The position to check
        :type pos: QPointF
        :return: True if the position is in bound, False otherwise
        :rtype: bool
        """

        if self.mode == Mode.IMAGE:
            return self.__image_viewer.is_in_bound(pos)
        elif self.mode == Mode.VIDEO:
            raise Exception("Cannot check in bound in video mode")

        raise Exception("Unknown mode")

    def is_in_viewer_bound(self, pos: QPointF) -> bool:
        """
        Check if the given position is in bound of the viewer.

        :param pos: The position to check
        :type pos: QPointF
        :return: True if the position is in bound, False otherwise
        :rtype: bool
        """
        local_pos = self.mapFromGlobal(pos)

        if (
            local_pos.x() < 0
            or local_pos.y() < 0
            or local_pos.x() > self.width()
            or local_pos.y() > self.height()
        ):
            return False

        return True

    def get_original_pixmap_coords_from_global(
        self, pos: QPointF | QPoint
    ) -> Tuple[float, float] | None:
        """
        Get the original pixmap coordinates from the global coordinates. Only works in image mode.

        :param pos: The global coordinates
        :type pos: QPointF | QPoint
        :return: The original pixmap coordinates
        :rtype: Tuple[float, float] | None
        """
        if self.mode == Mode.IMAGE:
            return self.__image_viewer.get_original_pixmap_coords_from_global(pos)
        elif self.mode == Mode.VIDEO:
            raise Exception("Cannot get original pixmap coords in video mode")

    def get_image(self) -> QImage | None:
        """
        Get the image if the viewer is in image mode. Otherwise, raise an exception.

        :return: The image
        :rtype: QImage | None
        """
        if self.mode == Mode.IMAGE:
            return self.__image_viewer.get_image()
        elif self.mode == Mode.VIDEO:
            raise Exception("Cannot get image in video mode")

    def set_pixmap(self, pixmap: QPixmap) -> None:
        """
        Set the pixmap to the image viewer.

        :param QPixmap pixmap: The pixmap to set
        :return: None
        """
        if self.mode == Mode.IMAGE:
            self.__image_viewer.set_pixmap(pixmap)
        elif self.mode == Mode.VIDEO:
            raise Exception("Cannot set pixmap in video mode")

    def set_video(self, video_path: str) -> None:
        """
        Set the video to be played. Only works in video mode.

        :param str video_path: Path to the video file.
        :return: None
        """
        if self.mode == Mode.VIDEO:
            self.__video_player.set_video(video_path)
        elif self.mode == Mode.IMAGE:
            raise Exception("Cannot set video in image mode")
