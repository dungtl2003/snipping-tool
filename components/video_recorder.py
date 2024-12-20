import qimage2ndarray
import time
from typing import Callable, Optional
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QImage,
    QMouseEvent,
    QPaintEvent,
    QPainter,
    QPixmap,
    QRegion,
)
import cv2
import pyaudio
import numpy as np
import subprocess
import wave
from Xlib import X, display
from Xlib.protocol import request
import threading

from PyQt6.QtCore import QElapsedTimer, QPoint, QPointF, QRect, QTimer, Qt
from PyQt6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget

from components import utils


class VideoRecorder(QWidget):
    def __init__(self, capture_area: QRect, on_finish: Callable[[], None]) -> None:
        super().__init__()

        # self.set_on_all_desktops()
        self.__capture_area = capture_area
        self.__on_finish = on_finish

        # UI setup
        self.setWindowFlags(
            self.windowFlags()
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.X11BypassWindowManagerHint  # Fking multi-monitor
            | Qt.WindowType.WindowTransparentForInput
            | Qt.WindowType.Tool
            | Qt.WindowType.MaximizeUsingFullscreenGeometryHint
        )
        # self.setAttribute(Qt.WidgetAttribute.WA_InputMethodTransparent, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        # self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        # self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        full_geometry = utils.get_combined_screen_geometry()
        self.setGeometry(full_geometry)

        # Capture settings
        self.__recording = False
        self.__elapsed_time = QElapsedTimer()

        # OpenCV setup
        self.fourcc = cv2.VideoWriter.fourcc(*"mp4v")
        self.video_out = None
        self.video_timer = QTimer(self)
        self.video_timer.timeout.connect(self.record_video_frame)
        self.video_timer.setSingleShot(False)

        # Audio setup
        # self.audio_out = "audio.wav"
        # self.__audio_stream = None
        # self.audio_frames = []
        # self.audio_format = pyaudio.paInt16
        # self.channels = 1
        # self.rate = 44100
        # self.chunk = 1024
        # self.p = pyaudio.PyAudio()

        self.hide()
        self.stop_button_wrapper = StopBtnWrapper(self.stop_recording)
        self.stop_button_wrapper.raise_()
        self.stop_button_wrapper.hide()

    #
    # def mousePressEvent(self, a0: Optional[QMouseEvent]) -> None:
    #     """Handle mouse press events."""
    #     assert a0 is not None
    #     print("Mouse press")
    #
    #     # Check if the mouse click is inside the button's geometry
    #     if self.stop_button.geometry().contains(a0.pos()):
    #         # Forward the event to the button
    #         self.stop_button.click()
    #     else:
    #         # Ignore other mouse events
    #         pass

    def start_recording(self):
        """Start recording video and audio."""
        self.__recording = True
        self.__elapsed_time.start()

        self.showFullScreen()
        self.stop_button_wrapper.show()

        # Start video recording
        self.video_out = cv2.VideoWriter(
            "video.mp4",
            self.fourcc,
            60.0,
            (self.__capture_area.width(), self.__capture_area.height()),
        )
        self.video_timer.start(16)  # Record every ~16ms for 60 FPS

        # Start audio recording
        # self.__audio_stream = self.p.open(
        #     format=self.audio_format,
        #     channels=self.channels,
        #     rate=self.rate,
        #     input=True,
        #     frames_per_buffer=self.chunk,
        # )
        # self.audio_frames = []

    def record_video_frame(self):
        """Capture the current video frame."""
        if not self.__recording:
            return

        combine_pixmap = utils.capture_all_screens()
        capture_pixmap = combine_pixmap.copy(self.__capture_area)
        frame_rgb = qimage2ndarray.rgb_view(capture_pixmap.toImage())
        frame_rgb = cv2.cvtColor(frame_rgb, cv2.COLOR_BGR2RGB)
        assert self.video_out is not None
        self.video_out.write(frame_rgb)

        elapsed = self.__elapsed_time.elapsed() // 1000
        self.stop_button_wrapper.stop_button.setText(
            f"● {elapsed // 60:02}:{elapsed % 60:02}"
        )

    def stop_recording(self):
        """Stop recording and merge audio and video."""
        self.__recording = False
        self.video_timer.stop()

        # Stop video recording
        if self.video_out:
            self.video_out.release()

        # Stop audio recording
        # assert self.__audio_stream is not None
        # self.__audio_stream.stop_stream()
        # self.__audio_stream.close()
        # self.p.terminate()

        # Save audio
        # with wave.open(self.audio_out, "wb") as wf:
        #     wf.setnchannels(self.channels)
        #     wf.setsampwidth(self.p.get_sample_size(self.audio_format))
        #     wf.setframerate(self.rate)
        #     wf.writeframes(b"".join(self.audio_frames))

        # Merge audio and video
        # self.merge_audio_video("video.avi", self.audio_out, "output_with_audio.avi")
        self.close()
        self.stop_button_wrapper.close()
        cv2.destroyAllWindows()

        self.format_video()

        self.__on_finish()

    def format_video(self):
        # TODO: temp fix, remove this in the future
        command = [
            "ffmpeg",
            "-y",
            "-i",
            "video.mp4",
            "-c:v",
            "libx264",
            "output.mp4",
        ]
        subprocess.run(command)

        command = [
            "rm",
            "video.mp4",
        ]
        subprocess.run(command)

    def merge_audio_video(self, video_file, audio_file, output_file):
        """Merge video and audio using ffmpeg."""
        command = [
            "ffmpeg",
            "-y",
            "-i",
            video_file,
            "-i",
            audio_file,
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-strict",
            "experimental",
            output_file,
        ]
        subprocess.run(command)

    # def qimage_to_cv2(self, qimage: QImage) -> np.ndarray:
    #     """Convert QImage to OpenCV format."""
    #     incoming_image = qimage.convertToFormat(QImage.Format.Format_RGBA8888)
    #
    #     width = incoming_image.width()
    #     height = incoming_image.height()
    #
    #     ptr = incoming_image.bits()
    #     assert ptr is not None
    #     ptr.setsize(height * width * 4)
    #     arr = np.frombuffer(ptr, np.uint8).reshape((height, width, 4))
    #     return arr

    def paintEvent(self, a0: Optional[QPaintEvent]) -> None:
        """Darken the screen and highlight the selected area."""
        painter = QPainter(self)
        painter.setBrush(QBrush(QColor(0, 0, 0, 150)))  # Dark overlay
        painter.setPen(Qt.PenStyle.NoPen)

        # Use QRegion to exclude the selected area
        screen_region = QRegion(self.rect())  # Full widget region
        selected_region = QRegion(self.__capture_area)  # Selected area

        # Subtract the selected region from the screen region
        overlay_region = screen_region.subtracted(selected_region)
        painter.setClipRegion(overlay_region)

        painter.drawRect(self.rect())


class StopBtnWrapper(QWidget):
    def __init__(self, stop_event: Callable[[], None]):
        super().__init__()

        # UI setup
        self.setWindowFlags(
            self.windowFlags()
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.X11BypassWindowManagerHint  # Fking multi-monitor
            # | Qt.WindowType.Tool
        )

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)

        # Floating button for stopping recording
        self.stop_button = QPushButton("● 00:00", self)
        self.stop_button.setStyleSheet(
            """
            QPushButton {
                background-color: red;
                color: white;
                font-size: 12px;
                border-radius: 12px;
            }
        """
        )

        self.stop_button.setGeometry(5, 25, 70, 25)
        self.stop_button.clicked.connect(stop_event)
        self.stop_button.raise_()
        self.stop_button.show()

    def mousePressEvent(self, a0: Optional[QMouseEvent]) -> None:
        assert a0 is not None
        self.__mouse_move_pos = None

        if a0.button() == Qt.MouseButton.RightButton:
            self.__mouse_move_pos = a0.globalPosition()

    def mouseMoveEvent(self, a0: Optional[QMouseEvent]) -> None:
        assert a0 is not None

        if (
            a0.buttons() == Qt.MouseButton.RightButton
            and self.__mouse_move_pos is not None
        ):
            glob_pos = a0.globalPosition()
            # Calculate the global difference only once
            diff = glob_pos - self.__mouse_move_pos

            # Only move the widget if there is significant movement
            if abs(diff.x()) > 0.3 or abs(diff.y()) > 0.3:
                self.move(self.x() + int(diff.x()), self.y() + int(diff.y()))
                self.__mouse_move_pos = glob_pos
