from re import error
from typing import Optional, Tuple
from PyQt6.QtCore import Qt
from PyQt6.QtGui import (
    QImage,
    QMouseEvent,
    QPixmap,
    QResizeEvent,
    QWheelEvent,
)
from PyQt6.QtWidgets import QLabel, QSizePolicy


class ImageLabel(QLabel):
    def __init__(self) -> None:
        super().__init__()

        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.zoom_factor = 1.0  # 100%
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.setMouseTracking(True)
        self.original_pixmap = None

    def get_image(self) -> QImage | None:
        """
        Return the image (without scaling).

        :return: the image (if existed)
        :rtype: QImage or None
        """
        return None if self.original_pixmap is None else self.original_pixmap.toImage()

    # For testing only
    def mouseMoveEvent(self, ev: Optional[QMouseEvent]) -> None:
        if ev is None:
            return

        point = self.get_pixmap_relative_pos(ev.pos().x(), ev.pos().y())
        if point is None:
            return

        (x, y) = point
        print(f"Clicked at ({x}, {y}) in image")

    def get_pixmap_relative_pos(self, x: float, y: float) -> Tuple[float, float] | None:
        if self.original_pixmap is None:
            return

        # Get scaled image offset cooridination origin (0, 0)
        scaled_img_rel_offset_x = (self.width() - self.pixmap().width()) / 2
        scaled_img_rel_offset_y = (self.height() - self.pixmap().height()) / 2

        scaled_img_rel_x = x - scaled_img_rel_offset_x
        scaled_img_rel_y = y - scaled_img_rel_offset_y
        # Check if click is within the scaled image bounds
        if not self.__is_in_bound(
            (scaled_img_rel_x, scaled_img_rel_y),
            (self.pixmap().width(), self.pixmap().height()),
        ):
            return None

        # Get click position relative to the original image
        x = scaled_img_rel_x / (self.scale_factor * self.zoom_factor)
        y = scaled_img_rel_y / (self.scale_factor * self.zoom_factor)
        if not self.__is_in_bound(
            (x, y), (self.original_pixmap.width(), self.original_pixmap.height())
        ):
            return None

        return (x, y)

    def wheelEvent(self, a0: Optional[QWheelEvent]) -> None:
        if a0 is None:
            raise error("wheelEvent should not be None")

        # Zoom in or out based on the scroll direction
        if a0.angleDelta().y() > 0:  # Scroll up
            self.zoom_factor = min(2, self.zoom_factor + 0.1)  # Max 200%
        elif a0.angleDelta().y() < 0:  # Scroll down
            self.zoom_factor = max(0.1, self.zoom_factor - 0.1)  # Min 10%

        # Update the display with the new scale factor
        self.__update_image_display()

    def resizeEvent(self, a0: Optional[QResizeEvent]) -> None:
        self.__update_image_display()

    def setPixmap(self, a0: QPixmap) -> None:
        self.original_pixmap = a0
        self.__update_image_display()

    def __update_image_display(self) -> None:
        if self.original_pixmap is None:
            return

        # Get the current label width
        label_width = self.width()

        # Scale the image if the window width is smaller than the image width
        if label_width < self.original_pixmap.width():
            self.scale_factor = label_width / self.original_pixmap.width()

            scaled_pixmap = self.original_pixmap.scaledToWidth(
                label_width, Qt.TransformationMode.SmoothTransformation
            )

            scaled_pixmap = scaled_pixmap.scaled(
                scaled_pixmap.size() * self.zoom_factor,
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )  # Apply zoom factor
        else:
            scaled_pixmap = self.original_pixmap.scaled(
                self.original_pixmap.size() * self.zoom_factor,
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.scale_factor = 1.0

        # Set the scaled or original pixmap to the QLabel
        super().setPixmap(scaled_pixmap)
        # self.__debug()

    def __is_in_bound(
        self, point: Tuple[float, float], area: Tuple[float, float]
    ) -> bool:
        (x, y) = point
        (w, h) = area

        return x >= 0 and x < w and y >= 0 and y < h

    def __debug(self):
        if self.original_pixmap is None:
            return

        print()
        print(f"label size: {self.width()} - {self.height()}")
        print(
            f"image size: {self.original_pixmap.width()} - {self.original_pixmap.height()}"
        )
        print(f"scaled image size: {self.pixmap().width()} - {self.pixmap().height()}")
        print(f"scale factor: {self.scale_factor}")
        print(f"zoom factor: {self.zoom_factor}")
        print()
