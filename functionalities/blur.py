from enum import Enum
from PyQt6.QtCore import QRect
from PyQt6.QtGui import QImage
import cv2
import numpy as np


class BlurMode(Enum):
    PIXELATE = 0
    MOSAIC = 1
    GAUSSIAN = 2


def __qimage_to_cv2(qimage: QImage) -> np.ndarray:
    """Convert QImage to OpenCV format"""
    width = qimage.width()
    height = qimage.height()

    # Convert QImage to byte string
    ptr = qimage.bits()
    assert ptr is not None
    ptr.setsize(height * width * 4)
    arr = np.array(ptr).reshape(height, width, 4)  # 4 for RGBA

    # Convert RGBA to BGR (OpenCV format)
    return cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)


def __cv2_to_qimage(cv_img: np.ndarray) -> QImage:
    """Convert OpenCV image to QImage"""
    height, width = cv_img.shape[:2]
    data = cv_img.data.tobytes()

    # Create QImage from numpy array
    return QImage(data, width, height, width * 3, QImage.Format.Format_RGB888)


def apply_blur_effect(
    image: QImage, rect: QRect, blur_mode: BlurMode = BlurMode.MOSAIC
) -> QImage:
    # Convert QPixmap to OpenCV format
    cv_image = __qimage_to_cv2(image)

    # Normalize rectangle and ensure it's within image bounds
    rect = rect.normalized()
    rect = QRect(
        max(0, rect.x()),
        max(0, rect.y()),
        min(rect.width(), cv_image.shape[1] - rect.x()),
        min(rect.height(), cv_image.shape[0] - rect.y()),
    )

    # Create a mask for the blur shape
    mask = np.zeros(cv_image.shape[:2], dtype=np.uint8)

    cv2.rectangle(
        mask,
        (rect.x(), rect.y()),
        (rect.x() + rect.width(), rect.y() + rect.height()),
        255,
        -1,
    )

    # Apply the selected effect only to the masked area
    if blur_mode == BlurMode.PIXELATE:
        raise NotImplementedError("Pixelate blur not implemented")
    elif blur_mode == BlurMode.MOSAIC:
        __apply_mosaic_effect(cv_image, rect)
    elif blur_mode == BlurMode.GAUSSIAN:
        raise NotImplementedError("Gaussian blur not implemented")

    # Convert back to QPixmap
    qimage = __cv2_to_qimage(cv_image)
    return qimage


def __apply_mosaic_effect(
    image: np.ndarray, rect: QRect, blur_radius: int = 10
) -> None:
    """
    Apply a mosaic effect to the image within the specified rectangle.

    :param image: The image to apply the effect to.
    :param rect: The rectangle specifying the region of interest (ROI).
    """
    x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
    if w <= 0 or h <= 0:
        return

    # Extract ROI
    x = max(0, min(x, image.shape[1] - 1))
    y = max(0, min(y, image.shape[0] - 1))
    w = min(w, image.shape[1] - x)
    h = min(h, image.shape[0] - y)

    if w <= 0 or h <= 0:
        return

    roi = image[y : y + h, x : x + w]

    # Calculate tile size
    tile_size = max(2, blur_radius * 2)

    # Create mosaic effect
    for i in range(0, h, tile_size):
        for j in range(0, w, tile_size):
            tile_h = min(tile_size, h - i)
            tile_w = min(tile_size, w - j)
            if tile_h > 0 and tile_w > 0:
                tile = roi[i : i + tile_h, j : j + tile_w]
                color = cv2.mean(tile)[:3]  # Get average color
                roi[i : i + tile_h, j : j + tile_w] = color
