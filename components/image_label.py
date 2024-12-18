from re import error
from typing import Optional, Tuple
from PyQt6.QtCore import QPoint, QPointF, Qt
from PyQt6.QtGui import (
    QImage,
    QMouseEvent,
    QPixmap,
    QResizeEvent,
    QWheelEvent,
)
from PyQt6.QtWidgets import QLabel, QScrollArea, QSizePolicy, QVBoxLayout, QWidget


class ScrollLabel(QScrollArea):
    def __init__(self) -> None:
        super().__init__()

        # making widget resizable
        self.setWidgetResizable(True)

        self.label = ImageLabel()
        self.setWidget(self.label)

        # making qwidget object
        # content = QWidget(self)
        # self.setWidget(content)

        # vertical box layout
        # lay = QVBoxLayout(content)
        # self.label = ImageLabel()
        # lay.addWidget(self.label)

    def get_image(self) -> QImage | None:
        """
        Return the image (without scaling).

        :return: the image (if existed)
        :rtype: QImage or None
        """
        return self.label.get_image()

    def is_in_bound(self, glob_point: QPointF) -> bool:
        """
        Check if the point is within the image bounds.

        :param glob_point: the global position
        :type glob_point: QPointF
        :return: True if the point is within the image bounds, False otherwise
        :rtype: bool
        """
        return self.label.is_in_bound(glob_point)

    def get_original_pixmap_coords_from_global(
        self, point: QPointF | QPoint
    ) -> Tuple[float, float] | None:
        """
        Get the original pixmap coordinates from the global position.
        :param point: the global position
        :type point: QPointF
        :return: the original pixmap coordinates
        :rtype: Tuple[float, float] or None
        """
        return self.label.get_original_pixmap_coords_from_global(point)

    def setPixmap(self, a0: QPixmap) -> None:
        self.label.setPixmap(a0)


class ImageLabel(QLabel):
    def __init__(self) -> None:
        super().__init__()

        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__zoom_factor = 1.0  # 100%
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMouseTracking(True)
        self.__original_pixmap = None

    def get_image(self) -> QImage | None:
        """
        Return the image (without scaling).

        :return: the image (if existed)
        :rtype: QImage or None
        """
        return (
            None if self.__original_pixmap is None else self.__original_pixmap.toImage()
        )

    def is_in_bound(self, glob_point: QPointF) -> bool:
        """
        Check if the point is within the image bounds.

        :param glob_point: the global position
        :type glob_point: QPointF
        :return: True if the point is within the image bounds, False otherwise
        :rtype: bool
        """
        if self.__original_pixmap is None:
            return False

        # Get click position relative to the scaled image
        (pixmap_x, pixmap_y) = self.__get_pixmap_coords_from_global_unchecked(
            glob_point
        )

        # Check if click is within the scaled image bounds
        if not self.__is_in_bound(
            (pixmap_x, pixmap_y),
            (self.pixmap().width(), self.pixmap().height()),
        ):
            return False

        return True

    def get_original_pixmap_coords_from_global(
        self, point: QPointF | QPoint
    ) -> Tuple[float, float] | None:
        """
        Get the original pixmap coordinates from the global position.
        :param point: the global position
        :type point: QPointF
        :return: the original pixmap coordinates
        :rtype: Tuple[float, float] or None
        """
        if self.__original_pixmap is None:
            return

        # Get click position relative to the scaled image
        (pixmap_x, pixmap_y) = self.__get_pixmap_coords_from_global_unchecked(point)

        # Check if click is within the scaled image bounds
        if not self.__is_in_bound(
            (pixmap_x, pixmap_y),
            (self.pixmap().width(), self.pixmap().height()),
        ):
            return None

        # Get click position relative to the original image
        original_x = pixmap_x / (self.scale_factor * self.__zoom_factor)
        original_y = pixmap_y / (self.scale_factor * self.__zoom_factor)
        if not self.__is_in_bound(
            (original_x, original_y),
            (self.__original_pixmap.width(), self.__original_pixmap.height()),
        ):
            return None

        return (original_x, original_y)

    def wheelEvent(self, a0: Optional[QWheelEvent]) -> None:
        if a0 is None:
            raise error("wheelEvent should not be None")

        # Zoom in or out based on the scroll direction
        if a0.angleDelta().y() > 0:  # Scroll up
            self.__zoom_factor = min(2, self.__zoom_factor + 0.1)  # Max 200%
        elif a0.angleDelta().y() < 0:  # Scroll down
            self.__zoom_factor = max(0.1, self.__zoom_factor - 0.1)  # Min 10%

        # Update the display with the new scale factor
        self.__update_image_display()

    def resizeEvent(self, a0: Optional[QResizeEvent]) -> None:
        self.__update_image_display()

    def setPixmap(self, a0: QPixmap) -> None:
        self.__original_pixmap = a0
        self.__update_image_display()

    def __record_coordinates(self, ev: QMouseEvent) -> None:
        assert ev is not None

        point = self.get_original_pixmap_coords_from_global(ev.globalPosition())
        if point is None:
            return

        (x, y) = point
        print(f"Clicked at ({x}, {y}) in image")

    def __get_pixmap_coords_from_global_unchecked(
        self, point: QPointF | QPoint
    ) -> Tuple[float, float]:
        label_pos = self.mapFromGlobal(point)

        # Get scaled image offset relative to the label
        pixmap_offset_x = (self.width() - self.pixmap().width()) / 2
        pixmap_offset_y = (self.height() - self.pixmap().height()) / 2

        # Get click position relative to the scaled image
        pixmap_x = label_pos.x() - pixmap_offset_x
        pixmap_y = label_pos.y() - pixmap_offset_y

        return (pixmap_x, pixmap_y)

    def __update_image_display(self) -> None:
        if self.__original_pixmap is None:
            return

        scaled_pixmap = self.__original_pixmap.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        self.scale_factor = scaled_pixmap.width() / self.__original_pixmap.width()

        scaled_pixmap = scaled_pixmap.scaled(
            scaled_pixmap.size() * self.__zoom_factor,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        # Set the scaled or original pixmap to the QLabel
        super().setPixmap(scaled_pixmap)

    def __is_in_bound(
        self, point: Tuple[float, float], area: Tuple[float, float]
    ) -> bool:
        (x, y) = point
        (w, h) = area

        return x >= 0 and x < w and y >= 0 and y < h

    def __debug(self):
        if self.__original_pixmap is None:
            return

        print()
        print(f"label size: {self.width()} - {self.height()}")
        print(
            f"image size: {self.__original_pixmap.width()} - {self.__original_pixmap.height()}"
        )
        print(f"scaled image size: {self.pixmap().width()} - {self.pixmap().height()}")
        print(f"scale factor: {self.scale_factor}")
        print(f"zoom factor: {self.__zoom_factor}")
        print()
