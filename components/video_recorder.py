from enum import Enum
import threading
import platform
import time
from numpy.lib import math
from typing import Callable, Optional
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QMouseEvent,
    QPaintEvent,
    QPainter,
    QRegion,
)
import cv2
import pyaudio
import wave
import asyncio
from multiprocessing import Process, Manager
from multiprocessing.synchronize import Event
from multiprocessing.managers import DictProxy
import multiprocessing

from globals import processes

from PyQt6.QtCore import QElapsedTimer, QRect, QTimer, Qt
from PyQt6.QtWidgets import QPushButton, QWidget

from components import utils
from functionalities.video_processing import (
    process_video_and_audio_ffmpeg_python,
    process_video_and_audio_ffmpeg_raw_command,
)


def find_default_device(p: pyaudio.PyAudio) -> tuple[int, str] | None:
    assert p is not None

    os_name = platform.system()
    best_device: tuple[int, str] | None = None

    print(f"Detected OS: {os_name}")
    print("Searching for the best input device...")

    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        # print(f"Device {i}: {device_info}")
        max_input_channels: float = float(device_info["maxInputChannels"])
        device_name: str = str(device_info["name"]).lower()

        if max_input_channels > 0:
            if os_name == "Windows":
                # On Windows, prefer devices with "Microphone" in their name
                if "microphone" in device_name:
                    best_device = (i, device_name)
                    break
            elif os_name == "Linux":
                # On Linux, prefer devices associated with PulseAudio or PipeWire
                if "pipewire" in device_name or "pulse" in device_name:
                    best_device = (i, device_name)
                    break
            elif best_device is None:
                best_device = (i, device_name)

    if best_device is not None:
        index, device_name = best_device
        print(f"Selected audio device: {device_name} (index: {index})")

    return best_device


def record_audio_task(
    is_recording: Event,
    filename: str,
    channels: int,
    rate: int,
    chunk: int,
) -> None:
    if not is_recording.is_set():
        return

    p = pyaudio.PyAudio()
    default_device = find_default_device(p)
    if default_device is None:
        print("No default audio device found")
        return

    index, _ = default_device
    stream = p.open(
        format=pyaudio.paInt16,
        channels=channels,
        rate=rate,
        input=True,
        frames_per_buffer=chunk,
        input_device_index=index,
    )

    frames = []

    print("Recording audio...")
    while is_recording.is_set():
        data = stream.read(chunk)
        frames.append(data)

    stream.stop_stream()
    stream.close()

    p.terminate()
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(rate)
        wf.writeframes(b"".join(frames))

    print("Audio saved")


def save_frame_task(
    is_recording: Event,
    frame_queue: multiprocessing.Queue,
    shared_memory: DictProxy,
    filename: str,
    fourcc: int,
    fps: float,
    width: int,
    height: int,
) -> None:
    if not is_recording.is_set():
        return

    video_out = cv2.VideoWriter(
        filename,
        fourcc,
        fps,
        (width, height),
    )

    while is_recording.is_set():
        if not frame_queue.empty():
            frame = frame_queue.get()
            video_out.write(frame)
            shared_memory["total_frames"] += 1

    while not frame_queue.empty():
        frame = frame_queue.get()
        video_out.write(frame)
        shared_memory["total_frames"] += 1

    video_out.release()
    cv2.destroyAllWindows()
    print("Video saved")


def calculate_frame_task(
    is_recording: Event, shared_memory: DictProxy, capture_area: QRect
) -> None:
    while is_recording.is_set():
        frame_bgr = utils.capture_mss_2(capture_area)
        shared_memory["latest_frame"] = frame_bgr


class VideoType(Enum):
    MP4 = 1
    AVI = 2


class VideoRecorder(QWidget):
    def __init__(
        self,
        capture_area: QRect,
        on_finish: Callable[[], None],
        video_type: VideoType = VideoType.MP4,
    ) -> None:
        super().__init__()

        self.__capture_area = capture_area
        self.__on_finish = on_finish
        self.__temp_video_file_name = "video.avi"
        self.__temp_audio_file_name = "audio.wav"
        self.__video_type = video_type
        self.__fps = 30.0

        # UI setup
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(
            self.windowFlags()
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.X11BypassWindowManagerHint  # Fking multi-monitor
            | Qt.WindowType.WindowTransparentForInput
            | Qt.WindowType.Tool
            | Qt.WindowType.MaximizeUsingFullscreenGeometryHint
        )

        full_geometry = utils.get_combined_screen_geometry_mss()
        self.setGeometry(full_geometry)

        self.hide()
        self.__stop_button_wrapper = StopBtnWrapper(self.stop_recording)
        self.__stop_button_wrapper.raise_()
        self.__stop_button_wrapper.hide()

        self.__elapsed_time = QElapsedTimer()
        self.__timer = QTimer(self)
        self.__timer.timeout.connect(self.__update_button_text)
        self.__timer.start(100)

    def start_recording(self):
        """Start recording video and audio."""
        self.__elapsed_time.start()

        # Setup visual
        self.showFullScreen()
        self.__stop_button_wrapper.show()

        self.__audio_recorder = AudioRecorder(self.__temp_audio_file_name)
        self.__screen_recorder = ScreenRecorder(
            self.__capture_area, self.__temp_video_file_name, self.__fps
        )

        asyncio.run(self.__start_tasks())

    def stop_recording(self):
        """Stop recording and merge audio and video."""
        asyncio.run(self.__stop_tasks())

        self.close()
        self.__stop_button_wrapper.close()

        # Merge audio and video
        print("Merging audio and video")
        extension = "mp4" if self.__video_type == VideoType.MP4 else "avi"
        output_file = f"output_with_audio.{extension}"
        actual_duration = self.__elapsed_time.elapsed() / 1000
        os_name = platform.system()

        if os_name == "Windows":
            process_video_and_audio_ffmpeg_raw_command(
                self.__temp_video_file_name,
                self.__temp_audio_file_name,
                output_file,
                self.__fps,
                actual_duration,
            )
        elif os_name == "Linux":
            process_video_and_audio_ffmpeg_python(
                self.__temp_video_file_name,
                self.__temp_audio_file_name,
                output_file,
                self.__fps,
                actual_duration,
            )

        self.__on_finish()

    async def __stop_tasks(self):
        audio_task = asyncio.create_task(self.__audio_recorder.stop())
        screen_task = asyncio.create_task(self.__screen_recorder.stop())

        await asyncio.gather(audio_task, screen_task)

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

    def __update_button_text(self):
        elapsed = self.__elapsed_time.elapsed() // 1000
        self.__stop_button_wrapper.stop_button.setText(
            f"● {elapsed // 60:02}:{elapsed % 60:02}"
        )

    async def __start_tasks(self):
        screen_task = asyncio.create_task(self.__screen_recorder.start())
        audio_task = asyncio.create_task(self.__audio_recorder.start())

        await asyncio.gather(audio_task, screen_task)


class ScreenRecorder:
    def __init__(
        self,
        capture_area: QRect,
        filename: str,
        fps: float,
    ) -> None:
        self.__capture_area = capture_area
        self.__fps = fps
        self.__width, self.__height = capture_area.width(), capture_area.height()
        self.__fourcc = cv2.VideoWriter.fourcc(*"XVID")
        self.__filename = filename

        # Shared memory
        self.__is_recording = multiprocessing.Event()
        self.__manager = Manager()
        self.__shared_memory = self.__manager.dict()
        self.__frame_queue = self.__manager.Queue(maxsize=-1)
        processes.append(self.__manager)

    async def start(self) -> None:
        if self.__is_recording.is_set():
            return
        self.__is_recording.set()

        self.__record_thread = threading.Thread(
            target=self.__record,
            daemon=True,
        )
        self.__record_thread.start()

    async def stop(self) -> None:
        if not self.__is_recording.is_set():
            return

        self.__is_recording.clear()

        while self.__record_thread and self.__record_thread.is_alive():
            self.__record_thread.join()

        self.__manager.shutdown()
        processes.remove(self.__manager)

        print("Recording process stopped")

    def __record(self):
        if not self.__is_recording.is_set():
            return

        self.__shared_memory["total_frames"] = 0
        self.__shared_memory["latest_frame"] = None

        calc_frame_process = Process(
            target=calculate_frame_task,
            daemon=True,
            args=(
                self.__is_recording,
                self.__shared_memory,
                self.__capture_area,
            ),
        )
        save_frame_process = Process(
            target=save_frame_task,
            daemon=True,
            args=(
                self.__is_recording,
                self.__frame_queue,
                self.__shared_memory,
                self.__filename,
                self.__fourcc,
                self.__fps,
                self.__width,
                self.__height,
            ),
        )

        processes.append(calc_frame_process)
        processes.append(save_frame_process)

        calc_frame_process.start()
        save_frame_process.start()

        queue = self.__frame_queue
        interval = math.floor(1000 / self.__fps)
        previous_frame_time = math.floor(time.time() * 1000)
        new_frame_time = None

        print("Recording started")
        while self.__is_recording.is_set():
            latest_frame = self.__shared_memory.get("latest_frame")

            if latest_frame is not None and (
                new_frame_time is None
                or new_frame_time - previous_frame_time >= interval
            ):
                new_frame_time = math.floor(time.time() * 1000)
                fps = 1000 / (new_frame_time - previous_frame_time)

                # Adjust interval based on the current FPS
                if fps < self.__fps and interval > 1:
                    interval -= 1
                elif fps > self.__fps and interval < 1000:
                    interval += 1

                # print(f"FPS: {int(fps)}")
                previous_frame_time = new_frame_time
                queue.put(latest_frame)
            else:
                new_frame_time = math.floor(time.time() * 1000)

        calc_frame_process.join()
        processes.remove(calc_frame_process)
        save_frame_process.join()
        processes.remove(save_frame_process)

        print("Recording stopped")


class AudioRecorder:
    def __init__(
        self,
        filename: str,
        channels: int = 2,
        rate: int = 44100,
        chunk: int = 1024,
    ) -> None:
        self.__filename = filename
        self.__channels = channels
        self.__rate = rate
        self.__chunk = chunk
        self.__is_recording = multiprocessing.Event()

    async def start(self) -> None:
        if self.__is_recording.is_set():
            return
        self.__is_recording.set()

        self.__record_audio_process = Process(
            target=record_audio_task,
            daemon=True,
            args=(
                self.__is_recording,
                self.__filename,
                self.__channels,
                self.__rate,
                self.__chunk,
            ),
        )
        processes.append(self.__record_audio_process)
        self.__record_audio_process.start()

    async def stop(self) -> None:
        if not self.__is_recording.is_set():
            return

        self.__is_recording.clear()

        if self.__record_audio_process and self.__record_audio_process.is_alive():
            self.__record_audio_process.join()
            processes.remove(self.__record_audio_process)

        print("Audio recording stopped")


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
