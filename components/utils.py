from typing import cast
from PyQt6.QtCore import QRect, QSize, Qt
from PyQt6.QtGui import QCursor, QPainter, QPen, QPixmap
from PyQt6.QtWidgets import QApplication
from PyQt6.sip import voidptr


def capture_all_screens() -> QPixmap:
    # Create a combined pixmap for all screens
    full_geometry = get_combined_screen_geometry()
    combined_pixmap = QPixmap(full_geometry.size())
    combined_pixmap.fill(Qt.GlobalColor.transparent)  # Fill with transparency

    # Paint each screen’s pixmap onto the combined pixmap
    painter = QPainter(combined_pixmap)
    for screen in QApplication.screens():
        screen_geometry = screen.geometry()
        pixmap = screen.grabWindow(cast(voidptr, 0))
        painter.drawPixmap(screen_geometry.topLeft() - full_geometry.topLeft(), pixmap)
    painter.end()

    return combined_pixmap


def create_white_cross_cursor() -> QCursor:
    """Create a white cross cursor."""
    size = 32  # Cursor size
    pixmap = QPixmap(QSize(size, size))
    pixmap.fill(Qt.GlobalColor.transparent)  # Transparent background

    painter = QPainter(pixmap)
    pen = QPen(Qt.GlobalColor.white)
    pen.setWidth(2)  # Adjust the line width
    painter.setPen(pen)

    # Draw the cross
    center = size // 2
    painter.drawLine(center, 0, center, size)  # Vertical line
    painter.drawLine(0, center, size, center)  # Horizontal line

    painter.end()
    return QCursor(pixmap)


def get_combined_screen_geometry() -> QRect:
    """Calculate the union of all screens' geometries."""
    # Calculate the union of all screens' geometries
    screen_geometry = QRect()
    for screen in QApplication.screens():
        screen_geometry = screen_geometry.united(screen.geometry())
    return screen_geometry
