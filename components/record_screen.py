import sys
import os
from datetime import datetime
import time
from enum import Enum, auto

import cv2
import pyautogui
import numpy as np

import pyaudio      
import wave         
import threading    
from moviepy.editor import VideoFileClip, AudioFileClip

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, 
    QHBoxLayout, QWidget, QLabel, QFileDialog, QComboBox,
    QMessageBox, QRubberBand, QDialog
)
from PyQt6.QtCore import Qt, QTimer, QSize, QRect
from PyQt6.QtGui import (
    QScreen, QGuiApplication, QPixmap, QImage, 
    QMouseEvent, QCursor
)

class RecordingStatus(Enum):
    """Enum representing different recording states."""
    IDLE = auto()
    RECORDING = auto()
    PAUSED = auto()

class RegionSelectorDialog(QDialog):
    def __init__(self, parent=None):
        """
        Initialize region selector dialog.
        
        :param parent: Parent widget
        :type parent: Optional[QWidget]
        """
        super().__init__(parent, Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        
        # Make dialog cover all screens
        screens = QGuiApplication.screens()
        total_width = sum(screen.geometry().width() for screen in screens)
        total_height = max(screen.geometry().height() for screen in screens)
        
        self.setGeometry(0, 0, total_width, total_height)
        self.setWindowOpacity(0.3)
        self.setStyleSheet("background-color:black;")
        
        self.__origin = None
        self.__rubber_band = QRubberBand(QRubberBand.Shape.Rectangle, self)
        
        # Add instruction label
        self.__instruction_label = QLabel("Click and drag to select recording area\nPress ESC to cancel", self)
        self.__instruction_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 20px;
                background-color: rgba(0, 0, 0, 0.7);
                padding: 10px;
                border-radius: 5px;
            }
        """)
        self.__instruction_label.move(50, 50)
        self.__instruction_label.show()

    def keyPressEvent(self, event):
        """
        Handle key press events.
        
        :param event: Key press event
        :type event: QKeyEvent
        """
        if event.key() == Qt.Key.Key_Escape:
            self.reject()  # Close dialog without selection

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        Handle mouse press event for region selection.
        
        :param event: Mouse press event
        :type event: QMouseEvent
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.__origin = event.pos()
            self.__rubber_band.setGeometry(QRect(self.__origin, QSize()))
            self.__rubber_band.show()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """
        Handle mouse move event while selecting region.
        
        :param event: Mouse move event
        :type event: QMouseEvent
        """
        if self.__origin is None:
            return
        
        self.__rubber_band.setGeometry(QRect(self.__origin, event.pos()).normalized())

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """
        Handle mouse release event to finalize region selection.
        
        :param event: Mouse release event
        :type event: QMouseEvent
        """
        if event.button() == Qt.MouseButton.LeftButton and self.__origin is not None:
            final_rect = QRect(self.__origin, event.pos()).normalized()
            
            # Ensure minimum size
            if final_rect.width() < 300 or final_rect.height() < 200:
                QMessageBox.warning(self, "Invalid Region", "Selected region is too small. Please select a larger area.")
                return
            
            # Store selected region and accept dialog
            self.selected_region = (
                final_rect.x(), 
                final_rect.y(), 
                final_rect.width(), 
                final_rect.height()
            )
            self.accept()

class AudioRecorder:
    def __init__(self, filename="temp_audio.wav", rate=44100, fpb=1024, channels=2):
        """
        Initialize an audio recorder.
        
        :param str filename: Path to save the audio file, defaults to "temp_audio.wav"
        :param int rate: Audio sample rate, defaults to 44100 Hz
        :param int fpb: Frames per buffer, defaults to 1024
        :param int channels: Number of audio channels, defaults to 2
        """
        self.open = True
        self.rate = rate
        self.frames_per_buffer = fpb
        self.channels = channels
        self.format = pyaudio.paInt16
        self.audio_filename = filename
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=self.format,
                                      channels=self.channels,
                                      rate=self.rate,
                                      input=True,
                                      frames_per_buffer=self.frames_per_buffer)
        self.audio_frames = []

    def record(self):
        """
        Start continuous audio recording.
        
        Reads audio data from input stream and appends to audio frames.
        Continues recording until stopped.
        """
        self.stream.start_stream()
        while self.open:
            data = self.stream.read(self.frames_per_buffer) 
            self.audio_frames.append(data)
            if not self.open:
                break

    def stop(self):
        """
        Stop audio recording and save to wave file.
        
        :raises IOError: If unable to write audio file
        """
        if self.open:
            self.open = False
            self.stream.stop_stream()
            self.stream.close()
            self.audio.terminate()
            waveFile = wave.open(self.audio_filename, 'wb')
            waveFile.setnchannels(self.channels)
            waveFile.setsampwidth(self.audio.get_sample_size(self.format))
            waveFile.setframerate(self.rate)
            waveFile.writeframes(b''.join(self.audio_frames))
            waveFile.close()

    def start(self):
        """
        Launch audio recording in a separate thread.
        
        Creates and starts a new thread to run the record method.
        """
        audio_thread = threading.Thread(target=self.record)
        audio_thread.start()

class ScreenRecorderApp(QMainWindow):
    def __init__(self):
        """Initialize the Screen Recorder application."""
        super().__init__()
        self.__init_ui()
        self.__recording_status: RecordingStatus = RecordingStatus.IDLE
        self.__video_writer: Optional[cv2.VideoWriter] = None
        self.__timer: Optional[QTimer] = None
        self.__screen_region: Optional[Tuple[int, int, int, int]] = None
        self.__last_capture_time = None
        self.__frame_times = []
        self.__audio_recorder: Optional[AudioRecorder] = None

    def __init_ui(self) -> None:
        """Set up the user interface components."""
        self.setWindowTitle("Screen Recorder")
        self.setGeometry(100, 100, 500, 400)

        central_widget = QWidget()
        layout = QVBoxLayout()

        # Preview Area - Initially empty
        self.__preview_label = QLabel()
        self.__preview_label.setFixedSize(480, 270)
        self.__preview_label.setStyleSheet("background-color: black;")
        layout.addWidget(self.__preview_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Select Region Button
        select_region_btn = QPushButton("Select Recording Region")
        select_region_btn.clicked.connect(self.__show_region_selector)
        layout.addWidget(select_region_btn)

        # Video Format Dropdown
        format_layout = QHBoxLayout()
        format_label = QLabel("Video Format:")
        self.__format_combo = QComboBox()
        self.__format_combo.addItems(["MP4", "AVI"])
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.__format_combo)
        layout.addLayout(format_layout)

        # Recording Buttons
        button_layout = QHBoxLayout()
        self.__start_btn = QPushButton("Start Recording")
        self.__pause_btn = QPushButton("Pause")
        self.__stop_btn = QPushButton("Stop")

        self.__start_btn.clicked.connect(self.__start_recording)
        self.__pause_btn.clicked.connect(self.__toggle_pause)
        self.__stop_btn.clicked.connect(self.__stop_recording)

        # Initially disable pause and stop buttons
        self.__pause_btn.setEnabled(False)
        self.__stop_btn.setEnabled(False)

        button_layout.addWidget(self.__start_btn)
        button_layout.addWidget(self.__pause_btn)
        button_layout.addWidget(self.__stop_btn)

        layout.addLayout(button_layout)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def __show_region_selector(self) -> None:
        """
        Display screen region selection dialog.
        
        Allows user to select a specific area of the screen for recording.
        
        :raises QMessageBox: If selected region is too small
        :return: None
        """
        selector = RegionSelectorDialog(self)
        selector.setCursor(QCursor(Qt.CursorShape.CrossCursor))
        
        # Make current window stay in background
        self.setWindowOpacity(0.8)
        
        result = selector.exec()
        
        # Restore window opacity
        self.setWindowOpacity(1.0)
        
        if result == QDialog.DialogCode.Accepted:
            # Region selected successfully
            self.__screen_region = selector.selected_region
            
            # Show selected region info
            x, y, width, height = self.__screen_region
            QMessageBox.information(
                self, 
                "Region Selected", 
                f"Selected Region:\nX: {x}, Y: {y}\nWidth: {width}, Height: {height}"
            )
        
        # Ensure main window is visible and active
        self.raise_()
        self.activateWindow()

    def __start_recording(self) -> None:
        """
        Start screen recording process.
        
        Initializes video and audio recording.
        
        :raises QMessageBox: If no recording region is selected
        :return: None
        """
        if not self.__screen_region:
            QMessageBox.warning(self, "Warning", "Please select a recording region first!")
            return

        # Reset preview label
        self.__preview_label.clear()
        self.__preview_label.setStyleSheet("background-color: black;")

        # Prepare video recording
        codec_map = {'MP4': 'mp4v', 'AVI': 'XVID'}
        fourcc = cv2.VideoWriter_fourcc(*codec_map[self.__format_combo.currentText()])
        x, y, width, height = self.__screen_region
        
        # Unique filenames for temp files
        pid = os.getpid()
        video_filename = f"temp_screen_recording_{pid}.{self.__format_combo.currentText().lower()}"
        audio_filename = f"temp_audio_{pid}.wav"
        
        # Initialize video writer with initial frame rate
        self.__video_writer = cv2.VideoWriter(
            video_filename, 
            fourcc, 
            20.0,  # Initial default frame rate
            (width, height)
        )

        self.__audio_recorder = AudioRecorder(filename=audio_filename)
        
        # Start audio recording in parallel thread
        self.__audio_recorder.start()

        # Reset frame timing tracking
        self.__last_capture_time = None
        self.__frame_times = []

        # Start recording timers
        self.__timer = QTimer()
        self.__timer.timeout.connect(self.__capture_frame)
        self.__timer.start(16)  # Approximately 60 FPS, more precise timing

        self.__recording_status = RecordingStatus.RECORDING
        self.__start_btn.setEnabled(False)
        self.__pause_btn.setEnabled(True)
        self.__stop_btn.setEnabled(True)

    def __capture_frame(self) -> None:
        """
        Capture a single frame from selected screen region.
        
        Takes screenshot, updates preview, and writes frame to video file.
        
        :return: None
        """
        if self.__recording_status != RecordingStatus.RECORDING:
            return

        # Calculate time between frames
        current_time = time.time()
        
        # Handle first frame
        if self.__last_capture_time is None:
            self.__last_capture_time = current_time

        # Capture screenshot
        x, y, width, height = self.__screen_region
        screenshot = pyautogui.screenshot(region=(x, y, width, height))
        frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
        # Convert frame for preview
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image).scaled(
            self.__preview_label.width(), 
            self.__preview_label.height(), 
            Qt.AspectRatioMode.KeepAspectRatio
        )
        
        self.__preview_label.setPixmap(pixmap)
        
        # Write frame to video
        if self.__video_writer:
            self.__video_writer.write(frame)

        # Track frame timing
        frame_interval = current_time - self.__last_capture_time
        self.__frame_times.append(frame_interval)
        
        # Keep only last 100 frame times for potential future use
        if len(self.__frame_times) > 100:
            self.__frame_times.pop(0)

        # Update last capture time
        self.__last_capture_time = current_time

    def __toggle_pause(self) -> None:
        """
        Toggle between pausing and resuming screen recording.
        
        Manages both video and audio recording state.
        
        :return: None
        """
        if self.__recording_status == RecordingStatus.RECORDING:
            self.__recording_status = RecordingStatus.PAUSED
            self.__pause_btn.setText("Resume")
            if self.__timer:
                self.__timer.stop()
            if self.__audio_recorder:
                self.__audio_recorder.stop()
        elif self.__recording_status == RecordingStatus.PAUSED:
            self.__recording_status = RecordingStatus.RECORDING
            self.__pause_btn.setText("Pause")
            
            # Restart audio recorder
            pid = os.getpid()
            audio_filename = f"temp_audio_{pid}.wav"
            self.__audio_recorder = AudioRecorder(filename=audio_filename)
            self.__audio_recorder.start()
            
            if self.__timer:
                self.__timer.start()

    def __stop_recording(self) -> None:
        """
        Stop screen recording and manage file saving.
        
        Stops recording, prompts user to save file, and merges video/audio.
        
        :raises QMessageBox: If unable to save or process recording
        :return: None
        """
        if self.__recording_status == RecordingStatus.IDLE:
            return

        # Stop recording threads
        if self.__timer:
            self.__timer.stop()
        
        if self.__video_writer:
            self.__video_writer.release()
        
        if self.__audio_recorder:
            self.__audio_recorder.stop()

        # Reset UI state
        self.__recording_status = RecordingStatus.IDLE
        self.__start_btn.setEnabled(True)
        self.__pause_btn.setEnabled(False)
        self.__stop_btn.setEnabled(False)

        # Prompt for save location
        pid = os.getpid()
        default_filename = f"screen_recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{self.__format_combo.currentText().lower()}"
        save_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Save Recording", 
            default_filename, 
            f"Video Files (*.{self.__format_combo.currentText().lower()})"
        )

        if save_path:
            # Merge audio and video 
            try:
                video_temp = f"temp_screen_recording_{pid}.{self.__format_combo.currentText().lower()}"
                audio_temp = f"temp_audio_{pid}.wav"

                # Use MoviePy to merge
                video_clip = VideoFileClip(video_temp)
                audio_clip = AudioFileClip(audio_temp)
                
                
                # audio_clip = audio_clip.set_duration(video_clip.duration)
                
                final_clip = video_clip.set_audio(audio_clip)
                final_clip.write_videofile(save_path)
                
                # Close clips to free up resources
                video_clip.close()
                audio_clip.close()
                final_clip.close()

                # Clean up temporary files
                os.remove(video_temp)
                os.remove(audio_temp)

                # Notification after saving sucessfully
                QMessageBox.information(
                    self, 
                    "Recording Saved", 
                    f"Screen recording successfully saved to:\n{save_path}",
                    QMessageBox.StandardButton.Ok
                )

            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not save recording: {str(e)}")

        # Clear preview
        self.__preview_label.clear()
        self.__preview_label.setStyleSheet("background-color: black;")

def main():
    app = QApplication(sys.argv)
    screen_recorder = ScreenRecorderApp()
    screen_recorder.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()