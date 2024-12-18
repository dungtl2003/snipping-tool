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


class ImageViewer(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.__scroll_area = ScrollArea(self, self.__on_wheel_event)
        self.__label = ImageLabel(self.__scroll_area)
        self.__scroll_area.setWidget(self.__label)

        lay = QVBoxLayout(self)
        self.setLayout(lay)

        lay.addWidget(self.__scroll_area)

    def __on_wheel_event(self, a0: Optional[QWheelEvent]) -> None:
        if a0 is None:
            raise error("wheelEvent should not be None")

        delta = a0.angleDelta().y()
        if a0.modifiers() == Qt.KeyboardModifier.ControlModifier:  # Ctrl + Scroll
            self.__zoom(delta)
        else:  # Scroll
            self.__scroll(delta)

    def resizeEvent(self, a0: Optional[QResizeEvent]) -> None:
        self.__label.update_image_display(None)

    def get_image(self) -> QImage | None:
        return self.__label.get_image()

    def is_in_bound(self, glob_point: QPointF) -> bool:
        return self.__label.is_in_bound(glob_point)

    def get_original_pixmap_coords_from_global(
        self, point: QPointF | QPoint
    ) -> Tuple[float, float] | None:
        return self.__label.get_original_pixmap_coords_from_global(point)

    def setPixmap(self, a0: QPixmap) -> None:
        self.__label.setPixmap(a0)

    def __zoom(self, delta: int) -> None:
        # Update the display with the new scale factor
        self.__scroll_area.snapshot()
        self.__label.update_image_display(delta)

        image_size = self.__label.pixmap().size()
        scroll_area_viewport = self.__scroll_area.viewport()
        assert scroll_area_viewport is not None
        scroll_area_size = scroll_area_viewport.size()

        if image_size.width() > scroll_area_size.width():
            self.__scroll_area.setHorizontalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOn
            )
        else:
            self.__scroll_area.setHorizontalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOff
            )

        if image_size.height() > scroll_area_size.height():
            self.__scroll_area.setVerticalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOn
            )
        else:
            self.__scroll_area.setVerticalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOff
            )

        self.__scroll_area.update()
        self.__scroll_area.restore()

    def __scroll(self, delta: int):
        self.__scroll_area.scroll_v(delta)


class ImageLabel(QLabel):
    def __init__(self, parent: QScrollArea) -> None:
        super().__init__()

        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__zoom_factor = 1.0  # 100%
        # self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMouseTracking(True)
        self.__original_pixmap = None
        self.__parent = parent

    def get_image(self) -> QImage | None:
        return (
            None if self.__original_pixmap is None else self.__original_pixmap.toImage()
        )

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
        self.__original_pixmap = a0
        self.update_image_display(None)

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

    def update_image_display(self, delta: int | None) -> None:
        if self.__original_pixmap is None:
            return

        scroll_area = self.__parent
        available_size = scroll_area.size()

        # Zoom in or out based on the scroll direction
        if delta is not None and delta > 0:  # Scroll up
            self.__zoom_factor = min(5, self.__zoom_factor + 0.1)  # Max 500%
        elif delta is not None:  # Scroll down
            self.__zoom_factor = max(0.1, self.__zoom_factor - 0.1)  # Min 10%

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

    def restore_scroll_position(
        self, scroll_area, horizontal_scroll_pos, vertical_scroll_pos
    ):
        """Restore the scroll position after the layout update."""
        # Ensure the scroll bar positions are restored after the layout is complete
        scroll_area.horizontalScrollBar().setValue(horizontal_scroll_pos)
        scroll_area.verticalScrollBar().setValue(vertical_scroll_pos)

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
        """Scroll the image if it's larger than the label size."""
        # Scroll vertically
        scroll_bar_vertical = self.verticalScrollBar()
        assert scroll_bar_vertical is not None
        if delta > 0:
            scroll_bar_vertical.setValue(scroll_bar_vertical.value() - 50)
        else:
            scroll_bar_vertical.setValue(scroll_bar_vertical.value() + 50)
