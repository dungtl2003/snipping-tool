from enum import Enum
import sys
from typing import Optional, Tuple, List
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, 
                            QWidget, QHBoxLayout, QComboBox, QPushButton, QSpinBox)
from PyQt6.QtGui import (QPixmap, QPainter, QColor, QPen, QMouseEvent, QImage, 
                        QPainterPath)
from PyQt6.QtCore import Qt, QRect, QPoint
import cv2
import numpy as np

# Application constants
WINDOW_WIDTH: int = 800
WINDOW_HEIGHT: int = 600
INITIAL_X: int = 100
INITIAL_Y: int = 100
BORDER_WIDTH: int = 2

# Blur effect constants
DEFAULT_OPACITY: int = 128
DEFAULT_BLUR_RADIUS: int = 10
MAX_BLUR_RADIUS: int = 50

class BlurMode(Enum):
    PIXELATE = "Pixelate"
    GAUSSIAN = "Gaussian Blur"
    MOSAIC = "Mosaic"

class BlurShape(Enum):
    RECTANGLE = "Rectangle"
    ELLIPSE = "Ellipse"

class ScreenBlurEffect(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.__blur_mode: BlurMode = BlurMode.PIXELATE
        self.__blur_shape: BlurShape = BlurShape.RECTANGLE
        self.__is_blurring: bool = False
        self.__blurred_area: QRect = QRect()
        self.__blur_radius: int = DEFAULT_BLUR_RADIUS
        self.__opacity: int = DEFAULT_OPACITY
        self.__captured_pixmap: Optional[QPixmap] = None
        self.__modified_pixmap: Optional[QPixmap] = None
        self.__start_pos: Optional[QPoint] = None
        
        self.__setup_ui()
        
    def __setup_ui(self) -> None:
        self.setWindowTitle("Screen Blur Effect")
        self.setGeometry(INITIAL_X, INITIAL_Y, WINDOW_WIDTH, WINDOW_HEIGHT)

        main_layout: QVBoxLayout = QVBoxLayout()
        toolbar_layout: QHBoxLayout = QHBoxLayout()
        
        # Toolbar setup
        self.__mode_combo = QComboBox()
        self.__mode_combo.addItems([mode.value for mode in BlurMode])
        self.__mode_combo.currentTextChanged.connect(self.__on_mode_changed)
        toolbar_layout.addWidget(QLabel("Blur Mode:"))
        toolbar_layout.addWidget(self.__mode_combo)
        
        self.__shape_combo = QComboBox()
        self.__shape_combo.addItems([shape.value for shape in BlurShape])
        self.__shape_combo.currentTextChanged.connect(self.__on_shape_changed)
        toolbar_layout.addWidget(QLabel("Shape:"))
        toolbar_layout.addWidget(self.__shape_combo)
        
        self.__radius_spin = QSpinBox()
        self.__radius_spin.setRange(1, MAX_BLUR_RADIUS)
        self.__radius_spin.setValue(DEFAULT_BLUR_RADIUS)
        self.__radius_spin.valueChanged.connect(self.__on_radius_changed)
        toolbar_layout.addWidget(QLabel("Blur Radius:"))
        toolbar_layout.addWidget(self.__radius_spin)
        
        # Capture button
        capture_btn = QPushButton("Capture Screen")
        capture_btn.clicked.connect(self.__capture_screen)
        toolbar_layout.addWidget(capture_btn)
        
        main_layout.addLayout(toolbar_layout)

        self.__label = QLabel()
        self.__label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__label.setMinimumSize(WINDOW_WIDTH - 40, WINDOW_HEIGHT - 100)
        main_layout.addWidget(self.__label)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Mouse events
        self.__label.mousePressEvent = self.__on_mouse_press
        self.__label.mouseMoveEvent = self.__on_mouse_move
        self.__label.mouseReleaseEvent = self.__on_mouse_release

    def __qimage_to_cv2(self, qimage: QImage) -> np.ndarray:
        """Convert QImage to OpenCV format"""
        width = qimage.width()
        height = qimage.height()
        
        # Convert QImage to byte string
        ptr = qimage.bits()
        ptr.setsize(height * width * 4)
        arr = np.array(ptr).reshape(height, width, 4)  # 4 for RGBA
        
        # Convert RGBA to BGR (OpenCV format)
        return cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)

    def __cv2_to_qimage(self, cv_img: np.ndarray) -> QImage:
        """Convert OpenCV image to QImage"""
        height, width = cv_img.shape[:2]
        
        # Create QImage from numpy array
        return QImage(cv_img.data, width, height, width * 3, QImage.Format.Format_RGB888)

    def __capture_screen(self) -> None:
        """Capture the screen and display it in the label"""
        screen = QApplication.primaryScreen()
        self.__captured_pixmap = screen.grabWindow(0)
        self.__modified_pixmap = self.__captured_pixmap.copy()
        scaled_pixmap = self.__modified_pixmap.scaled(
            self.__label.size(), 
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.__label.setPixmap(scaled_pixmap)

    def __apply_pixelate_effect(self, image: np.ndarray, rect: QRect) -> None:
        """Apply pixelation effect using OpenCV"""
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
            
        roi = image[y:y+h, x:x+w]
        
        # Calculate pixelation size
        block_size = max(1, self.__blur_radius)
        
        # Ensure minimum dimensions for resize
        target_w = max(1, w//block_size)
        target_h = max(1, h//block_size)
        
        # Pixelate using resize down and up
        small = cv2.resize(roi, (target_w, target_h), interpolation=cv2.INTER_LINEAR)
        pixelated = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
        
        # Put back the pixelated region
        image[y:y+h, x:x+w] = pixelated

    def __apply_mosaic_effect(self, image: np.ndarray, rect: QRect) -> None:
        """Apply mosaic effect using OpenCV"""
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
            
        roi = image[y:y+h, x:x+w]
        
        # Calculate tile size
        tile_size = max(2, self.__blur_radius * 2)
        
        # Create mosaic effect
        for i in range(0, h, tile_size):
            for j in range(0, w, tile_size):
                tile_h = min(tile_size, h - i)
                tile_w = min(tile_size, w - j)
                if tile_h > 0 and tile_w > 0:
                    tile = roi[i:i+tile_h, j:j+tile_w]
                    color = cv2.mean(tile)[:3]  # Get average color
                    roi[i:i+tile_h, j:j+tile_w] = color

    def __apply_blur_effect(self) -> None:
        if self.__modified_pixmap is None or self.__blurred_area.isEmpty():
            return

        # Convert QPixmap to OpenCV format
        cv_image = self.__qimage_to_cv2(self.__modified_pixmap.toImage())
        
        # Normalize rectangle and ensure it's within image bounds
        rect = self.__blurred_area.normalized()
        rect = QRect(
            max(0, rect.x()),
            max(0, rect.y()),
            min(rect.width(), cv_image.shape[1] - rect.x()),
            min(rect.height(), cv_image.shape[0] - rect.y())
        )
        
        # Create a mask for the blur shape
        mask = np.zeros(cv_image.shape[:2], dtype=np.uint8)
        
        if self.__blur_shape == BlurShape.RECTANGLE:
            cv2.rectangle(mask, (rect.x(), rect.y()), 
                        (rect.x() + rect.width(), rect.y() + rect.height()), 
                        255, -1)
        elif self.__blur_shape == BlurShape.ELLIPSE:
            cv2.ellipse(mask, ((rect.x() + rect.width()//2, rect.y() + rect.height()//2),
                             (rect.width(), rect.height()), 0), 255, -1)
        
        # Apply the selected effect only to the masked area
        if self.__blur_mode == BlurMode.PIXELATE:
            self.__apply_pixelate_effect(cv_image, rect)
        elif self.__blur_mode == BlurMode.MOSAIC:
            self.__apply_mosaic_effect(cv_image, rect)
        elif self.__blur_mode == BlurMode.GAUSSIAN:
            kernel_size = self.__blur_radius * 2 + 1  # Must be odd
            blurred = cv2.GaussianBlur(cv_image, (kernel_size, kernel_size), 0)
            cv_image = np.where(mask[:, :, np.newaxis] == 255, blurred, cv_image)

        # Convert back to QPixmap and update display
        qimage = self.__cv2_to_qimage(cv_image)
        self.__modified_pixmap = QPixmap.fromImage(qimage)
        self.__update_display()

    def __update_display(self) -> None:
        """Update the display with the current modified image"""
        if self.__modified_pixmap:
            scaled_pixmap = self.__modified_pixmap.scaled(
                self.__label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.__label.setPixmap(scaled_pixmap)

    def __on_mouse_press(self, event: QMouseEvent) -> None:
        if not self.__modified_pixmap:
            return
            
        self.__is_blurring = True
        self.__start_pos = event.position().toPoint()
        self.__blurred_area.setTopLeft(self.__start_pos)
        self.__blurred_area.setBottomRight(self.__start_pos)

    def __on_mouse_move(self, event: QMouseEvent) -> None:
        if not self.__is_blurring or not self.__modified_pixmap:
            return
            
        current_pos = event.position().toPoint()
        
        self.__blurred_area.setBottomRight(current_pos)
            
        # Create a copy of the original pixmap
        self.__modified_pixmap = self.__captured_pixmap.copy()
        
        # Draw the selection shape
        painter = QPainter(self.__modified_pixmap)
        painter.setPen(QPen(QColor(255, 255, 255), BORDER_WIDTH))
        
        if self.__blur_shape == BlurShape.RECTANGLE:
            painter.drawRect(self.__blurred_area)
        elif self.__blur_shape == BlurShape.ELLIPSE:
            painter.drawEllipse(self.__blurred_area)
        
        painter.end()
        self.__update_display()

    def __on_mouse_release(self, event: QMouseEvent) -> None:
        if not self.__is_blurring:
            return
            
        self.__is_blurring = False
        self.__apply_blur_effect()

    def __on_mode_changed(self, mode_text: str) -> None:
        self.__blur_mode = BlurMode(mode_text)

    def __on_shape_changed(self, shape_text: str) -> None:
        self.__blur_shape = BlurShape(shape_text)

    def __on_radius_changed(self, value: int) -> None:
        self.__blur_radius = value

def main():
    app = QApplication(sys.argv)
    window = ScreenBlurEffect()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()