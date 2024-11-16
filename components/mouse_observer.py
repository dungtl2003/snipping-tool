from enum import Enum
from typing import Callable, Optional, Tuple, cast, List
from PyQt6 import QtCore
from PyQt6.QtCore import QObject, QEvent
from PyQt6.QtGui import QWindow, QMouseEvent


class MouseObserver(QtCore.QObject):
    class SubscribeEvent(Enum):
        PRESSED = 0
        RELEASED = 1
        MOVED = 2

    pressed = QtCore.pyqtSignal(QMouseEvent)
    released = QtCore.pyqtSignal(QMouseEvent)
    moved = QtCore.pyqtSignal(QMouseEvent)

    def __init__(self, window: QWindow) -> None:
        super().__init__(window)

        self.__window = window

        self.__window.installEventFilter(self)

    def subcribe(
        self,
        subscribers: List[Tuple[Callable[..., None], SubscribeEvent]],
    ) -> None:
        """
        Subscribe to the mouse events.
        :param subscriber_handlers: the handlers to be called when the event is triggered
        :type subscriber_handlers: List[Callable[..., None]]
        :param subscriber_event: the event to subscribe to
        :type subscriber_event: MouseObserver.SubscribeEvent
        :return: None
        """
        for handler, event in subscribers:
            if event == MouseObserver.SubscribeEvent.PRESSED:
                self.pressed.connect(handler)
            elif event == MouseObserver.SubscribeEvent.RELEASED:
                self.released.connect(handler)
            elif event == MouseObserver.SubscribeEvent.MOVED:
                self.moved.connect(handler)

    def window(self) -> QWindow:
        return self.__window

    def eventFilter(self, a0: Optional["QObject"], a1: Optional["QEvent"]) -> bool:
        assert a1 is not None

        if a1.type() == QtCore.QEvent.Type.MouseButtonPress:
            self.pressed.emit(cast(QMouseEvent, a1))
        elif a1.type() == QtCore.QEvent.Type.MouseButtonRelease:
            self.released.emit(cast(QMouseEvent, a1))
        elif a1.type() == QtCore.QEvent.Type.MouseMove:
            self.moved.emit(cast(QMouseEvent, a1))

        return False
