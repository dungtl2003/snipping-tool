from __future__ import annotations
from enum import Enum
from typing import Callable, Optional, Tuple

from PyQt6 import QtGui
from PyQt6.QtCore import QPoint, QRect, QSize, Qt
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QIcon,
    QPaintEvent,
    QPainter,
    QPixmap,
)
from PyQt6.QtWidgets import QPushButton, QWidget

from components.utils import (
    get_focus_screen_geometry,
    set_cross_cursor,
    set_normal_cursor,
    capture_all_screens_mss,
    get_combined_screen_geometry_mss,
)
import os
from preload import ICON_DIR

PLUS_ICON = os.path.join(ICON_DIR, "plus.svg")


class NewCapture(QPushButton):
    def __init__(
        self,
        on_pre_capture: Callable[[], None],
        on_post_capture: Callable[[Tuple[QRect, QPixmap] | None], None],
    ) -> None:
        super().__init__(QIcon(PLUS_ICON), " New")

        self.clicked.connect(self.capture)
        self.__on_pre_capture = on_pre_capture
        self.__on_post_capture = on_post_capture

    def capture(self) -> None:
        """
        Capture the screen.
        Note that when capturing, no other actions can be performed.
        :return: None
        """
        self.__on_pre_capture()
        self.capturer = SnapshotOverlay(self.__on_post_capture)


class CaptureMode(Enum):
    """
    If user only clicks, the whole screen is captured.
    If user clicks and drags, the area is captured.
    """

    AREA = 1
    SCREEN = 2


class SnapshotOverlay(QWidget):
    def __init__(
        self,
        on_capture: Callable[[Tuple[QRect, QPixmap] | None], None],
    ) -> None:
        super().__init__()

        self.__on_capture = on_capture

        # Calculate the geometry that covers all screens
        self.__full_geometry = get_combined_screen_geometry_mss()
        self.setWindowFlags(
            self.windowFlags()
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.X11BypassWindowManagerHint  # Fking multi-monitor
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        set_cross_cursor()

        self.__screen_pixmap = capture_all_screens_mss()
        self.__selection_start = QPoint()
        self.__selection_rect = QRect()
        self.__capture_mode = CaptureMode.SCREEN

        self.setGeometry(self.__full_geometry)
        self.showFullScreen()

    def paintEvent(self, a0: Optional[QPaintEvent]) -> None:
        painter = QPainter(self)

        # Draw the frozen screen as background
        painter.drawPixmap(self.rect(), self.__screen_pixmap)

        # Draw the darkened overlay
        painter.setBrush(QBrush(QColor(0, 0, 0, 150)))  # Semi-transparent black
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.rect())

        # Draw the selection area (revealing the original screen content)
        if not self.__selection_rect.isNull():
            painter.drawPixmap(
                self.__selection_rect, self.__screen_pixmap, self.__selection_rect
            )

    def keyPressEvent(self, a0: Optional[QtGui.QKeyEvent]) -> None:
        self.close()
        set_normal_cursor()
        self.__on_capture(None)

    def keyReleaseEvent(self, a0: Optional[QtGui.QKeyEvent]) -> None:
        self.close()
        set_normal_cursor()
        self.__on_capture(None)

    def mousePressEvent(self, a0: Optional[QtGui.QMouseEvent]) -> None:
        assert a0 is not None

        if a0.button() == Qt.MouseButton.LeftButton:
            # Start the rubber band selection from the clicked position
            self.__selection_start = a0.globalPosition().toPoint()
            self.__selection_rect = QRect(self.__selection_start, QSize())

    def mouseMoveEvent(self, a0: Optional[QtGui.QMouseEvent]) -> None:
        assert a0 is not None

        if not self.__selection_start.isNull():
            self.__capture_mode = CaptureMode.AREA
            # Update the selection rectangle based on mouse position
            self.__selection_rect = QRect(
                self.__selection_start, a0.globalPosition().toPoint()
            ).normalized()
            self.update()

    def mouseReleaseEvent(self, a0: Optional[QtGui.QMouseEvent]) -> None:
        assert a0 is not None

        if a0.button() == Qt.MouseButton.LeftButton:
            self.close()
            capture_area = QRect()
            if self.__capture_mode == CaptureMode.SCREEN:
                capture_area = get_focus_screen_geometry()
            elif self.__capture_mode == CaptureMode.AREA:
                capture_area = QRect(
                    self.__selection_rect.topLeft(), self.__selection_rect.size()
                )

            capture_pixmap = self.__screen_pixmap.copy(
                capture_area.translated(-self.__full_geometry.topLeft())
            )

            set_normal_cursor()
            self.__on_capture((capture_area, capture_pixmap))
