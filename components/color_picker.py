from PyQt6.QtGui import QMouseEvent
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget


class ColorPicker(QWidget):
    def __init__(self, main_window: "SnipperWindow") -> None:
        super().__init__()

        self.__main = main_window
        self.__is_active = False
        self.__is_last_in_bound: bool | None = None

        self.setMouseTracking(True)

    def toggle(self) -> None:
        """
        Toggle the color picker.
        :return: None
        """
        self.__is_active = not self.__is_active

    def pick_color(self, a0: QMouseEvent) -> None:
        """
        Pick the color from the image.
        :param a0: the mouse event
        :type a0: QtGui.QMouseEvent
        :return: None
        """
        if not self.__is_active:
            return

        point = self.__main.label.get_original_pixmap_coords_from_global(
            a0.globalPosition()
        )
        if point is None:
            print("No image found or out of bounds.")
            return
        (x, y) = point

        image = self.__main.label.get_image()
        assert image is not None

        color = image.pixelColor(int(x), int(y)).getRgb()

        (r, g, b, _) = color
        assert r is not None and g is not None and b is not None
        hex_color = self.__rgb_to_hex(r, g, b)

        print(f"Color: {hex_color}")

    def handle_mouse_movement(self, a0: QMouseEvent) -> None:
        """
        Handle the mouse movement.
        :param a0: the mouse event
        :type a0: QtGui.QMouseEvent
        :return: None
        """
        if not self.__is_active:
            return

        assert a0 is not None
        if not self.__main.label.is_in_bound(a0.globalPosition()):
            if self.__is_last_in_bound is not False:
                self.__is_last_in_bound = False
                QApplication.restoreOverrideCursor()
        else:
            if self.__is_last_in_bound is not True:
                self.__is_last_in_bound = True
                QApplication.setOverrideCursor(Qt.CursorShape.CrossCursor)

    def __rgb_to_hex(self, r: int, g: int, b: int) -> str:
        return "#{:02x}{:02x}{:02x}".format(r, g, b)


from components.snipper_window import SnipperWindow
