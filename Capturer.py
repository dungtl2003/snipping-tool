from PyQt6.QtWidgets import QWidget, QApplication, QRubberBand
from PyQt6.QtGui import QMouseEvent, QCursor
from PyQt6.QtCore import Qt, QPoint, QRect
import time


class Capture(QWidget):

    def __init__(self, main_window):
        super().__init__()
        self.main = main_window
        self.main.hide()

        self.setMouseTracking(True)
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowOpacity(0.15)

        self.rubber_band = QRubberBand(QRubberBand.Shape.Rectangle, self)
        self.origin = QPoint()

        QApplication.setOverrideCursor(QCursor(Qt.CursorShape.CrossCursor))
        screen = QApplication.primaryScreen()
        rect = screen.geometry()

        time.sleep(0.31)
        # Lấy ảnh chụp màn hình của toàn bộ màn hình
        self.imgmap = screen.grabWindow(0, rect.x(), rect.y(), rect.width(), rect.height())



    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.origin = event.pos()
            self.rubber_band.setGeometry(QRect(self.origin, event.pos()).normalized())
            self.rubber_band.show()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if not self.origin.isNull():
            self.rubber_band.setGeometry(QRect(self.origin, event.pos()).normalized())

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.rubber_band.hide()

            # Lấy tọa độ của vùng đã chọn
            rect = self.rubber_band.geometry()

            # Chụp lại màn hình và lấy đúng vùng đã chọn
            screen = QApplication.primaryScreen()
            self.imgmap = screen.grabWindow(0, rect.x(), rect.y(), rect.width(), rect.height())

            QApplication.restoreOverrideCursor()

            # Lưu ảnh chụp vào clipboard và file
            clipboard = QApplication.clipboard()
            clipboard.setPixmap(self.imgmap)

            self.imgmap.save("TEST.png")

            self.main.label.setPixmap(self.imgmap)
            self.main.show()

            self.close()

