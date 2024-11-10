from __future__ import annotations
from typing import Dict, Optional

from PyQt6 import QtGui
from PyQt6.QtCore import QPoint, QRect, QSize, Qt
from PyQt6.QtGui import QCursor, QPainter, QPixmap, QScreen
from PyQt6.QtWidgets import QApplication, QRubberBand, QWidget
from PyQt6.sip import voidptr


class Capture(QWidget):
    def __init__(self, main_window: "SnipperWindow") -> None:
        super().__init__()

        self.main = main_window
        self.main.hide()

        self.setMouseTracking(True)

        # Calculate the geometry that covers all screens
        self.full_geometry = self.__get_combined_screen_geometry()
        self.setWindowFlags(
            self.windowFlags()
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.X11BypassWindowManagerHint  # Fking multi-monitor
        )

        # Set up a frameless, transparent window that covers all monitors and stays on top
        self.setGeometry(self.full_geometry)
        self.setWindowOpacity(0.15)
        self.show()

        # Initialize individual rubber bands for each screen
        self.rubber_bands: Dict[QScreen, QRubberBand] = {}
        for screen in QApplication.screens():
            rubber_band = QRubberBand(QRubberBand.Shape.Rectangle, self)
            rubber_band.setGeometry(screen.geometry())
            self.rubber_bands[screen] = rubber_band

        self.origin = QPoint()
        self.selection_rect = QRect()

        QApplication.setOverrideCursor(QCursor(Qt.CursorShape.CrossCursor))

    def keyPressEvent(self, a0: Optional[QtGui.QKeyEvent]) -> None:
        QApplication.restoreOverrideCursor()
        self.main.show()
        self.close()

    def keyReleaseEvent(self, a0: Optional[QtGui.QKeyEvent]) -> None:
        QApplication.restoreOverrideCursor()
        self.main.show()
        self.close()

    def mousePressEvent(self, a0: Optional[QtGui.QMouseEvent]) -> None:
        assert a0 is not None

        if a0.button() == Qt.MouseButton.LeftButton:
            # Start the rubber band selection from the clicked position
            self.origin = a0.globalPosition().toPoint()
            self.selection_rect = QRect(self.origin, QSize())
            self.__update_rubber_bands()
            self.__show_rubber_bands()

    def mouseMoveEvent(self, a0: Optional[QtGui.QMouseEvent]) -> None:
        assert a0 is not None
        if not self.origin.isNull():
            # Update the selection rectangle based on mouse position
            self.selection_rect = QRect(
                self.origin, a0.globalPosition().toPoint()
            ).normalized()
            self.__update_rubber_bands()

    def mouseReleaseEvent(self, a0: Optional[QtGui.QMouseEvent]) -> None:
        assert a0 is not None

        if a0.button() == Qt.MouseButton.LeftButton:
            # Hide rubber bands to take a screenshot without them
            self.__hide_rubber_bands()

            self.__capture_combined_screen()

            QApplication.restoreOverrideCursor()
            self.main.show()
            self.close()

    def __update_rubber_bands(self) -> None:
        # Update each rubber band based on the selection rectangle
        for screen, rubber_band in self.rubber_bands.items():
            intersection = screen.geometry().intersected(self.selection_rect)
            if not intersection.isEmpty():
                rubber_band.setGeometry(intersection)
                rubber_band.show()
            else:
                rubber_band.hide()

    def __show_rubber_bands(self) -> None:
        for rubber_band in self.rubber_bands.values():
            rubber_band.show()

    def __hide_rubber_bands(self) -> None:
        for rubber_band in self.rubber_bands.values():
            rubber_band.hide()

    def __capture_combined_screen(self):
        # Create a combined pixmap for all screens
        combined_pixmap = QPixmap(self.full_geometry.size())
        combined_pixmap.fill(Qt.GlobalColor.transparent)  # Fill with transparency

        # Paint each screen’s pixmap onto the combined pixmap
        painter = QPainter(combined_pixmap)
        for screen in QApplication.screens():
            screen_geometry = screen.geometry()
            pixmap = screen.grabWindow(voidptr(0))
            painter.drawPixmap(
                screen_geometry.topLeft() - self.full_geometry.topLeft(), pixmap
            )
        painter.end()

        # Extract the selected region from the combined pixmap
        global_rect = QRect(self.selection_rect.topLeft(), self.selection_rect.size())
        selected_region = combined_pixmap.copy(
            global_rect.translated(-self.full_geometry.topLeft())
        )

        # Show the selected region
        self.main.label.setPixmap(selected_region)

    def __get_combined_screen_geometry(self) -> QRect:
        # Calculate the union of all screens' geometries
        screen_geometry = QRect()
        for screen in QApplication.screens():
            screen_geometry = screen_geometry.united(screen.geometry())
        return screen_geometry


from components.snipper_window import SnipperWindow
