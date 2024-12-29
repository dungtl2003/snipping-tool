import time
from typing import Callable, List, Optional, Tuple
from PyQt6.QtCore import QRect, Qt
from PyQt6.QtGui import QIcon, QKeySequence, QPixmap, QResizeEvent, QShortcut
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from components.blur import Blur
from components.copy_btn import CopyButton
from components.save import SaveButton
from components.shortcut_blocking import ShortcutBlockable
from components.upload import ResourceType, UploadButton, UploadResource
from components.zoom import Zoom
from preload import BECAP_CLIPBOARD_MANAGER_PATH, ICON_DIR, APP_NAME
import os

from components.mouse_observer import MouseObserver
from components.color_picker import ColorPicker
from components.capture import NewCapture
from components.toolbar import MiddleToolBar, TopToolBar, BottomToolBar
from components.mode_switching import ModeSwitching
from components.video_recorder import VideoRecorder
from components.viewer import Viewer, Mode
from utils.styles import styles

APP_ICON = os.path.join(ICON_DIR, "scissors.svg")


class PixmapHistory:
    def __init__(self) -> None:
        self.__history: List[QPixmap] = []
        self.__current_index = -1

    def add(self, pixmap: QPixmap) -> None:
        self.__history = self.__history[: self.__current_index + 1]
        self.__history.append(pixmap)
        self.__current_index += 1

    def undo(self) -> QPixmap | None:
        if self.__current_index <= 0:
            return None

        self.__current_index -= 1
        return self.__history[self.__current_index]

    def redo(self) -> QPixmap | None:
        if self.__current_index >= len(self.__history) - 1:
            return None

        self.__current_index += 1
        return self.__history[self.__current_index]

    def clear(self) -> None:
        self.__history.clear()
        self.__current_index = -1

    def get_current_pixmap(self) -> QPixmap | None:
        if self.__current_index < 0 or self.__current_index >= len(self.__history):
            return None

        return self.__history[self.__current_index]

    def __len__(self) -> int:
        return len(self.__history)


class SnipperWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle(APP_NAME)
        # Not working
        icon = QIcon()
        icon.addPixmap(QPixmap(APP_ICON), QIcon.Mode.Selected, QIcon.State.On)
        self.setWindowIcon(icon)

        self.viewer = Viewer(self.__on_wheel_zoom_event)

        self.setFixedSize(450, 100)
        self.is_expand_before = False

        self.__init_functions()
        self.__set_layout()

        self.__setup_shortcut()

        self.__copy_btn.disable()
        self.__save_btn.disable()

        self.__last_copy_pixmap: QPixmap | None = None
        self.__pixmap_history: PixmapHistory = PixmapHistory()
        self.__current_mode = ModeSwitching.Mode.CAMERA
        self.__shortcut_blockable_list: List[ShortcutBlockable] = [self.__blur_btn]

    def subscribers(
        self,
    ) -> List[Tuple[Callable[..., None], MouseObserver.SubscribeEvent]]:
        """
        Return the subscribers.
        :return: the subscribers
        :rtype: List[Tuple[Callable[..., None], MouseObserver.SubscribeEvent]]
        """
        return [
            (self.__color_picker_btn.pick_color, MouseObserver.SubscribeEvent.PRESSED),
            (
                self.__color_picker_btn.handle_mouse_movement,
                MouseObserver.SubscribeEvent.MOVED,
            ),
            (
                self.__blur_btn.handle_mouse_movement,
                MouseObserver.SubscribeEvent.MOVED,
            ),
            (
                self.__blur_btn.on_mouse_press,
                MouseObserver.SubscribeEvent.PRESSED,
            ),
            (
                self.__blur_btn.on_mouse_release,
                MouseObserver.SubscribeEvent.RELEASED,
            ),
        ]

    def resizeEvent(self, a0: Optional[QResizeEvent]) -> None:
        if not self.is_expand_before:
            return

        self.__set_dynamic_size()

    def __on_wheel_zoom_event(self, zoom: float) -> None:
        self.__zoom.set_zoom(zoom)

    def __set_dynamic_size(self) -> None:
        if (
            self.viewer.mode == Mode.IMAGE
        ):  # only in image mode we need to toggle the middle section
            # Toggle middle section visibility based on window width
            # must hide first to remove widget from layout
            self.__middle_toolbar.show()
            if self.width() < 700:  # change this number to your desired width
                self.__toolbar_top.hide_center_section()
                self.__toolbar_bottom.show()
            else:
                self.__toolbar_bottom.hide()
                self.__toolbar_top.show_center_section()
        elif self.viewer.mode == Mode.VIDEO:
            self.__toolbar_bottom.hide()
            self.__toolbar_top.hide_center_section()
            self.__middle_toolbar.hide()

    def __show_with_expand(self) -> None:
        if not self.is_expand_before:
            self.__copy_btn.enable()
            self.__save_btn.enable()

            self.__toolbar_top.show_right_section()
            self.is_expand_before = True
            self.setMinimumSize(450, 500)
            self.setMaximumSize(16777215, 16777215)
            self.resize(450, 500)
        else:
            self.__set_dynamic_size()

        if self.viewer.mode == Mode.VIDEO:
            self.__copy_btn.disable()
        elif self.viewer.mode == Mode.IMAGE:
            self.__copy_btn.enable()

        self.show()

    def __set_layout(self) -> None:
        """
        Set the layout.
        :return: None
        """
        # Main central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Main layout
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.__middle_toolbar = MiddleToolBar(
            self.__color_picker_btn, self.__blur_btn, self.__zoom
        )

        # Toolbar (at the top)
        self.__toolbar_top = TopToolBar(
            self.__new_capture_btn,
            self.__mode_switching,
            self.__middle_toolbar,
            self.__save_btn,
            self.__copy_btn,
            self.__upload_btn,
        )
        # Main section
        self.viewer.setVisible(True)
        # Toolbar (at the bottom)
        self.__toolbar_bottom = BottomToolBar(self.__middle_toolbar)

        # Create a QScrollArea and set the QLabel as its widget
        self.main_layout.addWidget(
            self.__toolbar_top, alignment=Qt.AlignmentFlag.AlignTop
        )
        self.main_layout.addWidget(self.viewer)
        self.main_layout.addWidget(
            self.__toolbar_bottom, alignment=Qt.AlignmentFlag.AlignBottom
        )

    def __init_functions(self) -> None:
        """
        Init the functions.
        :return: None
        """
        self.__new_capture_btn = NewCapture(
            self.__on_pre_capture_event, self.__on_post_capture_event
        )
        self.__mode_switching = ModeSwitching()
        self.__color_picker_btn = ColorPicker(self.viewer)
        self.__blur_btn = Blur(
            self.viewer.get_pixmap,
            self.viewer.is_in_pixmap_bound,
            self.viewer.set_pixmap,
            self.viewer.get_original_pixmap_coords_from_global,
            self.__add_to_pixmap_history,
        )
        self.__zoom = Zoom(
            self.__on_zoom_in_event, self.__on_zoom_out_event, self.__on_reset_event
        )
        self.__save_btn = SaveButton(self.__on_save_event)
        self.__copy_btn = CopyButton(self.__on_copy_event)
        self.__upload_btn = UploadButton(self.__on_upload_event, self)

    def __on_zoom_in_event(self) -> float:
        return self.viewer.zoom_pixmap_in()

    def __on_zoom_out_event(self) -> float:
        return self.viewer.zoom_pixmap_out()

    def __on_reset_event(self) -> float:
        return self.viewer.reset_zoom()

    def __on_save_event(self) -> None:
        if not self.__save_btn.isEnabled():
            return

        self.viewer.save()

    def __on_copy_event(self) -> None:
        if not self.__copy_btn.isEnabled():
            return

        pixmap = self.viewer.get_pixmap()
        if pixmap is None:
            return

        image = pixmap.toImage()
        assert image is not None and not image.isNull()

        clipboard = QApplication.clipboard()
        if clipboard is not None:
            clipboard.setImage(image)

        # avoid saving the same image to clipboard db multiple times
        if self.__last_copy_pixmap is None or pixmap != self.__last_copy_pixmap:
            saved_time_str = time.strftime("%Y%m%d%H%M%S")
            new_file_path = os.path.join(
                BECAP_CLIPBOARD_MANAGER_PATH, f"becap_clipboard_{saved_time_str}.png"
            )

            image.save(new_file_path, "PNG")
            self.__last_copy_pixmap = pixmap

    def __on_pre_capture_event(self) -> None:
        self.hide()
        self.__deactivate_utilities()

        if self.is_expand_before and self.__current_mode == ModeSwitching.Mode.CAMERA:
            current_pixmap = self.__pixmap_history.get_current_pixmap()
            if current_pixmap is not None:
                self.viewer.set_pixmap(current_pixmap)

        time.sleep(0.2)  # wait for main screen to hide

    def __on_post_capture_event(
        self,
        capture_result: Tuple[QRect, QPixmap] | None,
    ) -> None:
        if capture_result is None:
            self.show()
            return

        self.__pixmap_history.clear()
        capture_area, capture_pixmap = capture_result

        if self.__mode_switching.mode() == ModeSwitching.Mode.CAMERA:
            self.__current_mode = ModeSwitching.Mode.CAMERA
            self.viewer.set_mode(Mode.IMAGE)
            self.viewer.set_pixmap(capture_pixmap)
            self.__add_to_pixmap_history(capture_pixmap)
            self.__show_with_expand()
        elif self.__mode_switching.mode() == ModeSwitching.Mode.VIDEO:
            self.__current_mode = ModeSwitching.Mode.VIDEO
            self.viewer.set_mode(Mode.VIDEO)

            self.__video_recorder = VideoRecorder(
                capture_area, self.__on_post_video_recording_event
            )
            self.__video_recorder.start_recording()

    def __on_post_video_recording_event(self) -> None:
        self.viewer.set_video(self.__video_recorder.video_file_path)
        self.__show_with_expand()

    def __setup_shortcut(self):
        # Can be used whenever the main window is focused
        shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        shortcut.activated.connect(self.__new_capture_btn.capture)
        shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        shortcut.activated.connect(self.close)
        shortcut = QShortcut(QKeySequence("Tab"), self)
        shortcut.activated.connect(self.__on_switch_mode_shortcut_action)

        # Cannot be used when being blocked
        shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        shortcut.activated.connect(self.__on_save_action)
        shortcut = QShortcut(QKeySequence("Ctrl+C"), self)
        shortcut.activated.connect(self.__on_copy_action)
        shortcut = QShortcut(QKeySequence("Ctrl+Z"), self)
        shortcut.activated.connect(self.__on_undo_action)
        shortcut = QShortcut(QKeySequence("Ctrl+Y"), self)
        shortcut.activated.connect(self.__on_redo_action)
        shortcut = QShortcut(QKeySequence("Ctrl+P"), self)
        shortcut.activated.connect(self.__on_pick_color_action)
        shortcut = QShortcut(QKeySequence("Ctrl+B"), self)
        shortcut.activated.connect(self.__on_blur_action)
        shortcut = QShortcut(QKeySequence("Ctrl+U"), self)
        shortcut.activated.connect(self.__on_upload_action)

    def __can_shortcut(self) -> bool:
        return all(
            not shortcut.is_blocking() for shortcut in self.__shortcut_blockable_list
        )

    def __on_upload_action(self) -> None:
        if not self.__can_shortcut():
            return

        self.__upload_btn.click()

    def __on_blur_action(self) -> None:
        if not self.__can_shortcut():
            return

        self.__blur_btn.toggle()

    def __on_pick_color_action(self) -> None:
        if not self.__can_shortcut():
            return

        self.__color_picker_btn.toggle()

    def __on_save_action(self) -> None:
        if not self.__can_shortcut():
            return

        self.__save_btn.click()

    def __on_copy_action(self) -> None:
        if not self.__can_shortcut():
            return

        self.__copy_btn.click()

    def __on_switch_mode_shortcut_action(self) -> None:
        if self.__mode_switching.mode() == ModeSwitching.Mode.CAMERA:
            self.__mode_switching.video_mode_btn.click()
        elif self.__mode_switching.mode() == ModeSwitching.Mode.VIDEO:
            self.__mode_switching.camera_mode_btn.click()

    def __on_undo_action(self) -> None:
        if not self.__can_shortcut():
            return

        pixmap = self.__pixmap_history.undo()
        if pixmap is not None:
            self.viewer.set_pixmap(pixmap)

    def __on_redo_action(self) -> None:
        if not self.__can_shortcut():
            return

        pixmap = self.__pixmap_history.redo()
        if pixmap is not None:
            self.viewer.set_pixmap(pixmap)

    def __on_upload_event(self) -> UploadResource:
        self.__deactivate_utilities()
        if self.viewer.mode == Mode.IMAGE:
            image = self.viewer.get_pixmap()
            assert image is not None
            image = image.toImage()
            return UploadResource(ResourceType.IMAGE, image=image)
        elif self.viewer.mode == Mode.VIDEO:
            video_path = self.viewer.get_video_path()
            return UploadResource(ResourceType.VIDEO, video_url=video_path)

        raise ValueError("Invalid mode")

    def __add_to_pixmap_history(self, pixmap: QPixmap) -> None:
        self.__pixmap_history.add(pixmap)

    def __deactivate_utilities(self) -> None:
        self.__blur_btn.deactivate()
        self.__color_picker_btn.deactivate()
        self.__blur_btn.unblock()


def run_snipper_window():
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    app.setStyleSheet(styles)
    w = SnipperWindow()
    w.show()

    window = w.window()
    assert window is not None

    window_handle = window.windowHandle()
    assert window_handle is not None

    mouse_observer = MouseObserver(window_handle)
    mouse_observer.subcribe(w.subscribers())

    app.exec()
