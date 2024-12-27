from PIL import Image
from PyQt6.QtCore import QRect, QSize, Qt
from PyQt6.QtGui import QColor, QCursor, QImage, QPainter, QPen, QPixmap
from PyQt6.QtWidgets import QApplication
from PyQt6.sip import voidptr
import cv2
from cv2.typing import MatLike
import mss
import mss.tools
import numpy as np


def set_normal_cursor() -> None:
    """Set the cursor to normal."""
    QApplication.setOverrideCursor(Qt.CursorShape.ArrowCursor)


def set_cross_cursor(
    size: int = 20, color: QColor | Qt.GlobalColor = Qt.GlobalColor.white
) -> None:
    """Set the cursor to white cross."""
    pixmap = QPixmap(QSize(size, size))
    pixmap.fill(Qt.GlobalColor.transparent)  # Transparent background

    painter = QPainter(pixmap)
    pen = QPen(color)
    pen.setWidth(2)  # Adjust the line width
    painter.setPen(pen)

    # Draw the cross
    center = size // 2
    painter.drawLine(center, 0, center, size)  # Vertical line
    painter.drawLine(0, center, size, center)  # Horizontal line

    painter.end()
    QApplication.setOverrideCursor(QCursor(pixmap))


def capture(rect: QRect) -> QPixmap | None:

    # Get the available screens (monitors)
    screens = QApplication.screens()

    # List to store QPixmaps for each monitor
    pixmaps = []

    for screen in screens:
        screen_geometry = screen.geometry()

        # Check if the rect intersects with the screen geometry
        if screen_geometry.intersects(rect):
            # Calculate the intersection of the QRect with the screen's geometry
            intersection_rect = rect.intersected(screen_geometry)

            # Grab the screen content for the intersection area
            pixmap = screen.grabWindow(
                voidptr(0),
                intersection_rect.x(),
                intersection_rect.y(),
                intersection_rect.width(),
                intersection_rect.height(),
            )
            pixmaps.append(pixmap)

    # Now, combine the captured pixmaps from multiple monitors
    if pixmaps:
        # Create a final combined QPixmap (we will assume rect is large enough to cover all the screens)
        combined_pixmap = QPixmap(rect.size())
        painter = QPainter(combined_pixmap)

        # Paste each captured pixmap into the final combined pixmap
        for pixmap in pixmaps:
            painter.drawPixmap(pixmap.rect(), pixmap)

        painter.end()
        return combined_pixmap
    return None


def get_combined_screen_geometry_mss() -> QRect:
    with mss.mss() as sct:
        combined_monitor = sct.monitors[0]
        return QRect(
            combined_monitor["left"],
            combined_monitor["top"],
            combined_monitor["width"],
            combined_monitor["height"],
        )


def capture_all_screens_mss() -> QPixmap:
    with mss.mss() as sct:
        combined_monitor = sct.monitors[0]

        screenshot = sct.grab(
            (
                combined_monitor["left"],
                combined_monitor["top"],
                combined_monitor["width"],
                combined_monitor["height"],
            )
        )

        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        img = img.convert("RGBA")
        img = QImage(
            img.tobytes("raw", "RGBA"),
            img.size[0],
            img.size[1],
            QImage.Format.Format_RGBA8888,
        )

        pixmap = QPixmap.fromImage(img)
        return pixmap


def capture_mss(rect: QRect) -> QPixmap | None:
    with mss.mss() as sct:
        # List of monitors
        combined_monitor = sct.monitors[0]

        # Check if the rect intersects with the screen geometry
        screen_geometry = QRect(
            combined_monitor["left"],
            combined_monitor["top"],
            combined_monitor["width"],
            combined_monitor["height"],
        )

        if not screen_geometry.intersects(rect):
            return None

        # Calculate the intersection of the QRect with the screen's geometry
        intersection_rect = rect.intersected(screen_geometry)

        # Capture the screen content for the intersection area
        screenshot = sct.grab(
            (
                intersection_rect.x(),
                intersection_rect.y(),
                intersection_rect.width()
                + intersection_rect.x(),  # idk why but this is needed
                intersection_rect.height() + intersection_rect.y(),
            )
        )

        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        img = img.convert("RGBA")
        img = QImage(
            img.tobytes("raw", "RGBA"),
            img.size[0],
            img.size[1],
            QImage.Format.Format_RGBA8888,
        )

        pixmap = QPixmap.fromImage(img)
        return pixmap


def capture_mss_2(rect: QRect) -> MatLike | None:
    with mss.mss() as sct:
        # List of monitors
        combined_monitor = sct.monitors[0]

        # Check if the rect intersects with the screen geometry
        screen_geometry = QRect(
            combined_monitor["left"],
            combined_monitor["top"],
            combined_monitor["width"],
            combined_monitor["height"],
        )

        if not screen_geometry.intersects(rect):
            return None

        # Calculate the intersection of the QRect with the screen's geometry
        intersection_rect = rect.intersected(screen_geometry)

        # Capture the screen content for the intersection area
        screenshot = sct.grab(
            (
                intersection_rect.x(),
                intersection_rect.y(),
                intersection_rect.width()
                + intersection_rect.x(),  # idk why but this is needed
                intersection_rect.height() + intersection_rect.y(),
            )
        )  # BGRA

        frame_bgr = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGRA2BGR)
        return frame_bgr


def get_focus_screen_geometry() -> QRect:
    """
    Get the geometry of the screen where the cursor is currently located. If the cursor is not on any screen, the
    primary screen's geometry is returned as a fallback.

    :return: The geometry of the screen where the cursor is located.
    :rtype: QRect
    """
    cursor_pos = QCursor.pos()
    screen = QApplication.screenAt(cursor_pos)
    if not screen:
        screen = QApplication.primaryScreen()  # Fallback to primary screen
        assert screen is not None

    return screen.geometry()
