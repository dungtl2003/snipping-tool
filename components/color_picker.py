from PyQt6.QtGui import QColor, QMouseEvent
from PyQt6.QtCore import QPoint, QPointF, Qt
from PyQt6.QtWidgets import QApplication, QLabel, QWidget


class ColorPicker(QWidget):
    def __init__(self, main_window: "SnipperWindow") -> None:
        super().__init__()

        self.__main = main_window
        self.__is_active = False
        self.__is_last_in_bound: bool | None = None

        self.setMouseTracking(True)

        # Create a color preview square label
        self.color_square = QLabel(self.__main.label)
        self.color_square.setFixedSize(30, 30)
        self.color_square.setStyleSheet(
            "background-color: #FFFFFF; border: 1px solid black;"
        )
        self.color_square.hide()  # Hide initially

    def deactivate(self) -> None:
        """
        Deactivate the color picker.
        :return: None
        """
        self.__is_active = False
        self.__is_last_in_bound = None
        self.color_square.hide()

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

        assert a0 is not None
        color = self.__get_color_at_cursor(a0.globalPosition())
        if color is None:
            return

        hex_color = color.name(QColor.NameFormat.HexArgb)
        clipboard = QApplication.clipboard()
        if clipboard is not None:
            clipboard.setText(hex_color)

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
        mouse_glob_pos = a0.globalPosition()

        if not self.__main.label.is_in_bound(mouse_glob_pos):
            if self.__is_last_in_bound is not False:
                self.__is_last_in_bound = False
                QApplication.restoreOverrideCursor()
                self.color_square.hide()
        else:
            if self.__is_last_in_bound is not True:
                self.__is_last_in_bound = True
                QApplication.setOverrideCursor(Qt.CursorShape.CrossCursor)
                self.color_square.show()

        color = self.__get_color_at_cursor(mouse_glob_pos)
        if color is None:
            return

        self.__update_color_square(a0.globalPosition().toPoint(), color)

    def __update_color_square(self, mouse_glob_pos: QPoint, color: QColor):
        self.color_square.setStyleSheet(
            f"background-color: {color.name()}; border: 1px solid black;"
        )
        moust_rel_pos = self.__main.label.mapFromGlobal(mouse_glob_pos)
        half_label_area_width = self.__main.label.width() / 2
        half_label_area_height = self.__main.label.height() / 2

        offset = 15
        if moust_rel_pos.x() > half_label_area_width:
            if moust_rel_pos.y() > half_label_area_height:  # bottom right
                offset = QPoint(
                    -self.color_square.width() - offset,
                    -self.color_square.height() - offset,
                )
            else:  # top right
                offset = QPoint(-self.color_square.width() - offset, offset)
        else:
            if moust_rel_pos.y() > half_label_area_height:  # bottom left
                offset = QPoint(offset, -self.color_square.height() - offset)
            else:  # top left
                offset = QPoint(offset, offset)

        self.color_square.move(moust_rel_pos + offset)
        self.color_square.show()

    def __get_color_at_cursor(self, mouse_glob_pos: QPoint | QPointF) -> QColor | None:
        # Get the color at the cursor's position
        point = self.__main.label.get_original_pixmap_coords_from_global(mouse_glob_pos)
        if point is None:
            return None
        (x, y) = point

        image = self.__main.label.get_image()
        assert image is not None

        return image.pixelColor(int(x), int(y))


from components.snipper_window import SnipperWindow
