import os
from typing import Callable
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QWidget

from preload import ICON_DIR

ZOOM_ICON = os.path.join(ICON_DIR, "zoom.svg")
ZOOM_IN_ICON = os.path.join(ICON_DIR, "zoom-in.svg")
ZOOM_OUT_ICON = os.path.join(ICON_DIR, "zoom-out.svg")


class Zoom(QWidget):
    def __init__(
        self,
        on_zoom_in: Callable[[], float],
        on_zoom_out: Callable[[], float],
        on_reset: Callable[[], float],
    ) -> None:
        super().__init__()

        self.__on_zoom_in = on_zoom_in
        self.__on_zoom_out = on_zoom_out
        self.__on_reset = on_reset

        self.__reset_btn = QPushButton("100%")
        self.__zoom_in_btn = QPushButton(QIcon(ZOOM_IN_ICON), "")
        self.__zoom_out_btn = QPushButton(QIcon(ZOOM_OUT_ICON), "")

        self.__reset_btn.clicked.connect(self.__reset_event)
        self.__zoom_in_btn.clicked.connect(self.__zoom_in_event)
        self.__zoom_out_btn.clicked.connect(self.__zoom_out_event)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.__zoom_out_btn)
        layout.addWidget(self.__reset_btn)
        layout.addWidget(self.__zoom_in_btn)

        self.setLayout(layout)

    def set_zoom(self, zoom: float) -> None:
        """
        Set the zoom percentage.
        :param zoom: the zoom value
        :return: None
        """
        self.__calculate_zoom(zoom)

    def __zoom_in_event(self) -> None:
        """
        Handle the zoom in button clicked.
        :return: None
        """
        new_zoom = self.__on_zoom_in()
        self.__calculate_zoom(new_zoom)

    def __zoom_out_event(self) -> None:
        """
        Handle the zoom out button clicked.
        :return: None
        """
        new_zoom = self.__on_zoom_out()
        self.__calculate_zoom(new_zoom)

    def __reset_event(self) -> None:
        """
        Handle the reset button clicked.
        :return: None
        """
        new_zoom = self.__on_reset()
        self.__calculate_zoom(new_zoom)

    def __calculate_zoom(self, zoom: float) -> None:
        """
        Calculate the zoom percentage.
        :param zoom: the zoom value
        :return: None
        """
        zoom = round(round(zoom, 2) * 100)  # f**k floating point arithmetic
        self.__reset_btn.setText(str(zoom) + "%")
