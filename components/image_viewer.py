from enum import Enum
import time
from os import error
from typing import Callable, Optional, Tuple
from PyQt6.QtCore import QPoint, QPointF, Qt
from PyQt6.QtGui import QImage, QPixmap, QResizeEvent, QWheelEvent
from PyQt6.QtWidgets import (
    QFrame,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)
from ffmpeg.nodes import os

from preload import BECAP_PICTURE_PATH


class ZoomState(Enum):
    IN = 1
    OUT = 2
    RESET = 3


class ImageViewer(QWidget):
    def __init__(self, on_wheel_zoom_event: Callable[[float], None]) -> None:
        super().__init__()

        self.scroll_area = ScrollArea(self, self.__on_wheel_event)
        self.label = ImageLabel(self.scroll_area)
        self.scroll_area.setWidget(self.label)
        self.__on_wheel_zoom_event = on_wheel_zoom_event

        lay = QVBoxLayout(self)
        self.setLayout(lay)

        lay.addWidget(self.scroll_area)

    def resizeEvent(self, a0: Optional[QResizeEvent]) -> None:
        self.label.update_image_display()

    def save(self) -> None:
        """
        Save the image.
        :return: None
        """
        image = self.get_image()
        assert image is not None and not image.isNull()

        saved_time = time.strftime("%Y%m%d%H%M%S")
        image_path = os.path.join(BECAP_PICTURE_PATH, f"becap_image_{saved_time}.png")
        image.save(image_path)

    def copy_to_clipboard(self) -> QPixmap:
        """
        Copy the image to the clipboard.
        :return: None
        """
        pixmap = self.label.pixmap()

        return pixmap

    def get_original_pixmap(self) -> QPixmap | None:
        """
        Get the pixmap.
        :return: the pixmap
        :rtype: QPixmap
        """
        return self.label.get_original_pixmap()

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
        # Check if the click is within the scroll area and the image label
        return self.scroll_area.is_in_bound(glob_point) and self.label.is_in_bound(
            glob_point
        )

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

    def set_pixmap(self, a0: QPixmap) -> None:
        """
        Set the pixmap to the label.
        :param a0: the pixmap
        :type a0: QPixmap
        :return: None
        """
        self.label.setPixmap(a0)

    def __on_wheel_event(self, a0: Optional[QWheelEvent]) -> None:
        if a0 is None:
            raise error("wheelEvent should not be None")

        delta = a0.angleDelta().y()
        if a0.modifiers() == Qt.KeyboardModifier.ControlModifier:  # Ctrl + Scroll
            state = None
            if delta is not None and delta > 0:  # Scroll up
                state = ZoomState.IN
            elif delta is not None:  # Scroll down
                state = ZoomState.OUT

            assert state is not None
            new_zoom = self.__zoom(state)
            self.__on_wheel_zoom_event(new_zoom)
        else:  # Scroll
            self.__scroll(delta)

    def zoom_in(self) -> float:
        """
        Zoom in the image.
        :return: the new zoom factor
        :rtype: float
        """
        return self.__zoom(ZoomState.IN)

    def zoom_out(self) -> float:
        """
        Zoom out the image.
        :return: the new zoom factor
        :rtype: float
        """
        return self.__zoom(ZoomState.OUT)

    def reset_zoom(self) -> float:
        """
        Reset the zoom.
        :return: the new zoom factor
        :rtype: float
        """
        return self.__zoom(ZoomState.RESET)

    def __zoom(self, state: ZoomState) -> float:
        # Update the display with the new scale factor
        self.scroll_area.snapshot()

        new_zoom_factor = self.label.zoom_image(state)

        image_size = self.label.pixmap().size()
        scroll_area_viewport = self.scroll_area.viewport()
        assert scroll_area_viewport is not None
        scroll_area_size = scroll_area_viewport.size()

        if image_size.width() > scroll_area_size.width():
            self.scroll_area.setHorizontalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOn
            )
        else:
            self.scroll_area.setHorizontalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOff
            )

        if image_size.height() > scroll_area_size.height():
            self.scroll_area.setVerticalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOn
            )
        else:
            self.scroll_area.setVerticalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOff
            )

        self.scroll_area.update()
        self.scroll_area.restore()

        return new_zoom_factor

    def __scroll(self, delta: int):
        self.scroll_area.scroll_v(delta)


class ImageLabel(QLabel):
    def __init__(self, parent: QScrollArea) -> None:
        super().__init__()

        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__zoom_factor = 1.0  # 100%
        self.setMouseTracking(True)
        self.__original_pixmap = None
        self.__parent = parent
        self.__max_zoom = 5  # 500%
        self.__min_zoom = 0.1  # 10%
        self.__zoom_delta = 0.1  # 10%

    def get_image(self) -> QImage | None:
        """
        Return the image (without scaling).
        :return: the image (if existed)
        :rtype: QImage or None
        """
        return (
            None if self.__original_pixmap is None else self.__original_pixmap.toImage()
        )

    def get_original_pixmap(self) -> QPixmap | None:
        """
        Get the pixmap.
        :return: the pixmap
        :rtype: QPixmap
        """
        return self.__original_pixmap

    def is_in_bound(self, glob_point: QPointF) -> bool:
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

    def setPixmap(self, a0: QPixmap) -> None:
        """
        Set the pixmap to the label.
        :param a0: the pixmap
        :type a0: QPixmap
        :return: None
        """
        self.__original_pixmap = a0
        self.update_image_display()

    def zoom_image(self, state: ZoomState) -> float:
        """
        Zoom the image.
        :param state: the zoom state
        :type state: ZoomState
        :return: the new zoom factor
        :rtype: float
        """
        if state == ZoomState.IN:
            self.__zoom_factor = min(
                self.__max_zoom, self.__zoom_factor + self.__zoom_delta
            )
        elif state == ZoomState.OUT:
            self.__zoom_factor = max(
                self.__min_zoom, self.__zoom_factor - self.__zoom_delta
            )
        elif state == ZoomState.RESET:
            self.__zoom_factor = 1.0

        self.update_image_display()
        return self.__zoom_factor

    def update_image_display(self) -> None:
        """
        Update the image display based on the zoom factor and the scroll direction.
        :param delta: the scroll direction
        :type delta: int or None
        :return: None
        """
        if self.__original_pixmap is None:
            return

        scroll_area = self.__parent
        available_size = scroll_area.size()

        scaled_pixmap = self.__original_pixmap.scaled(
            available_size,
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

    def __is_in_bound(
        self, point: Tuple[float, float], area: Tuple[float, float]
    ) -> bool:
        (x, y) = point
        (w, h) = area

        return x >= 0 and x < w and y >= 0 and y < h


class ScrollArea(QScrollArea):
    def __init__(self, parent: QWidget, on_wheel_event: Callable[..., None]) -> None:
        super().__init__(parent)

        self.setWidgetResizable(True)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.setWidgetResizable(True)

        self.setFrameShape(QFrame.Shape.NoFrame)

        self.setContentsMargins(0, 0, 0, 0)
        self.setContentsMargins(0, 0, 0, 0)

        self.__prev_h_value = None
        self.__prev_v_value = None

        self.__on_wheel_event = on_wheel_event

    def snapshot(self) -> None:
        """
        Take a snapshot of the current properties.
        :return: None
        """
        horizontal_scroll_bar = self.horizontalScrollBar()
        vertical_scroll_bar = self.verticalScrollBar()

        if horizontal_scroll_bar is not None:
            self.__prev_h_value = horizontal_scroll_bar.value()

        if vertical_scroll_bar is not None:
            self.__prev_v_value = vertical_scroll_bar.value()

    def restore(self) -> None:
        """
        Restore the snapshot of the properties. Remember to call snapshot() before calling this method.
        :return: None
        """
        horizontal_scroll_bar = self.horizontalScrollBar()
        vertical_scroll_bar = self.verticalScrollBar()

        if horizontal_scroll_bar is not None and self.__prev_h_value is not None:
            horizontal_scroll_bar.setValue(self.__prev_h_value)

        if vertical_scroll_bar is not None and self.__prev_v_value is not None:
            vertical_scroll_bar.setValue(self.__prev_v_value)

    def wheelEvent(self, a0: Optional[QWheelEvent]) -> None:
        self.__on_wheel_event(a0)

    def scroll_v(self, delta: int) -> None:
        """
        Scroll vertically.
        :param delta: the delta value
        :type delta: int
        :return: None
        """
        # Scroll vertically
        scroll_bar_vertical = self.verticalScrollBar()
        assert scroll_bar_vertical is not None
        if delta > 0:
            scroll_bar_vertical.setValue(scroll_bar_vertical.value() - 50)
        else:
            scroll_bar_vertical.setValue(scroll_bar_vertical.value() + 50)

    def is_in_bound(self, glob_point: QPointF) -> bool:
        """
        Check if the point is within the scroll area bounds.
        :param glob_point: the global position
        :type glob_point: QPointF
        :return: True if the point is within the scroll area bounds, False otherwise
        :rtype: bool
        """
        viewport = self.viewport()
        assert viewport is not None

        # Get click position relative to the label
        label_pos = viewport.mapFromGlobal(glob_point)
        viewport_size = viewport.size()

        return (
            label_pos.x() >= 0
            and label_pos.x() < viewport_size.width()
            and label_pos.y() >= 0
            and label_pos.y() < viewport_size.height()
        )
