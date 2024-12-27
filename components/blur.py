from enum import Enum
import os

from typing import Callable, Tuple
from PyQt6.QtCore import QPoint, QPointF, QRect, Qt
from PyQt6.QtGui import QColor, QIcon, QMouseEvent, QPainter, QPixmap
from PyQt6.QtWidgets import QPushButton

from components.utils import set_cross_cursor, set_normal_cursor
from functionalities.blur import apply_blur_effect
from preload import ICON_DIR

BLUR_ICON = os.path.join(ICON_DIR, "blur.svg")


class MouseState(Enum):
    NORMAL = 0
    DRAGGING = 1


class Blur(QPushButton):
    def __init__(
        self,
        receive_pixmap: Callable[[], QPixmap | None],
        check_bound: Callable[[QPointF], bool],
        update_pixmap: Callable[[QPixmap], None],
        map_to_pixmap: Callable[[QPointF | QPoint], Tuple[float, float] | None],
        push_pixmap: Callable[[QPixmap], None],
    ) -> None:
        super().__init__(QIcon(BLUR_ICON), "")
        self.setToolTip("Blur")

        self.setCheckable(True)
        self.setMouseTracking(True)

        self.__receive_pixmap = receive_pixmap
        self.__check_bound = check_bound
        self.__update_pixmap = update_pixmap
        self.__map_to_pixmap = map_to_pixmap

        self.__is_last_in_bound = False
        self.__is_active = False
        self.__mouse_state = MouseState.NORMAL
        self.__selection_start: QPoint = QPoint()
        self.__selection_end: QPoint = QPoint()
        self.__original_pixmap: QPixmap | None = None
        self.__selection_rect: QRect = QRect()
        self.__modified_pixmap: QPixmap | None = None
        self.__push_pixmap = push_pixmap

        self.clicked.connect(self.toggle)

    def deactivate(self) -> None:
        """
        Deactivate the blur button.
        :return: None
        """
        self.__is_active = False
        self.setChecked(False)
        self.__mouse_state = MouseState.NORMAL

    def toggle(self) -> None:
        """
        Toggle the color picker.
        :return: None
        """
        self.__is_active = not self.__is_active
        self.setChecked(self.__is_active)

    def handle_mouse_movement(self, a0: QMouseEvent) -> None:
        """
        Handle the mouse movement.
        :param a0: the mouse event
        :type a0: QtGui.QMouseEvent
        :return: None
        """
        if not self.__is_active:
            return

        self.__update_mouse_ui(a0)

        if self.__mouse_state == MouseState.DRAGGING:
            self.__draw_selection(a0)

    def on_mouse_press(self, a0: QMouseEvent) -> None:
        """
        Handle the press event.
        :param a0: the mouse event
        :type a0: QtGui.QMouseEvent
        :return: None
        """
        if not self.__is_active:
            return

        in_bound = self.__check_bound(a0.globalPosition())

        if not in_bound:
            return

        self.__mouse_state = MouseState.DRAGGING
        self.__original_pixmap = self.__receive_pixmap()
        if self.__original_pixmap is None:
            return

        self.__original_pixmap = self.__original_pixmap.copy()
        start_pos = self.__map_to_pixmap(a0.globalPosition())
        if start_pos is not None:
            start_pos = QPointF(*start_pos)
            self.__selection_start = start_pos.toPoint()
        else:
            self.__selection_start = QPoint()

    def on_mouse_release(self, a0: QMouseEvent) -> None:
        """
        Handle the release event.
        :param a0: the mouse event
        :type a0: QtGui.QMouseEvent
        :return: None
        """
        if not self.__is_active:
            return

        self.__mouse_state = MouseState.NORMAL

        if self.__selection_rect.isNull():
            return

        pixmap = self.__original_pixmap
        assert pixmap is not None
        img = pixmap.toImage()

        blured_img = apply_blur_effect(img, self.__selection_rect)
        self.__modified_pixmap = QPixmap.fromImage(blured_img)
        self.__update_pixmap(self.__modified_pixmap)
        self.__push_pixmap(self.__modified_pixmap)

        self.__selection_start = QPoint()
        self.__selection_end = QPoint()
        self.__original_pixmap = None
        self.__selection_rect = QRect()
        self.__modified_pixmap = None

    def __update_mouse_ui(self, a0: QMouseEvent) -> None:
        mouse_glob_pos = a0.globalPosition()
        in_bound = self.__check_bound(mouse_glob_pos)

        if not in_bound:
            if self.__is_last_in_bound is not False:
                self.__is_last_in_bound = False
                set_normal_cursor()
        else:
            if self.__is_last_in_bound is not True:
                self.__is_last_in_bound = True
                set_cross_cursor()

    def __draw_selection(self, a0: QMouseEvent) -> None:
        if self.__original_pixmap is None:
            return

        if self.__selection_start.isNull():
            return

        pixmap = self.__original_pixmap.copy()
        end_pos = self.__map_to_pixmap(a0.globalPosition())
        if end_pos is None:
            return

        end_pos = QPointF(*end_pos)
        self.__selection_end = end_pos.toPoint()
        self.__selection_rect = QRect(
            self.__selection_start, self.__selection_end
        ).normalized()

        painter = QPainter(pixmap)
        painter.setPen(QColor(255, 255, 255))
        painter.setBrush(
            Qt.BrushStyle.NoBrush
        )  # No fill for the rectangle (transparent inside)
        painter.drawRect(self.__selection_rect)
        painter.end()

        self.__update_pixmap(pixmap)
