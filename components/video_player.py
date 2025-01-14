import time
from typing import Optional
from PyQt6 import QtWidgets
from PyQt6 import QtCore
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtGui import QIcon, QMouseEvent, QPixmap, QTransform
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSlider,
    QVBoxLayout,
    QWidget,
)
import os
from preload import ICON_DIR, BECAP_VIDEO_PATH
import shutil

PLAY_ICON = os.path.join(ICON_DIR, "play.svg")
PAUSE_ICON = os.path.join(ICON_DIR, "pause.svg")
FORWARD_ICON = os.path.join(ICON_DIR, "forward.svg")
BACKWARD_ICON = os.path.join(ICON_DIR, "backward-5.svg")


class QJumpSlider(QSlider):
    sliderPressWithValue = QtCore.pyqtSignal(int)

    def __init__(self, *args, **kwargs):
        self.is_released = True
        super().__init__(*args, **kwargs)

    def mousePressEvent(self, ev: Optional[QMouseEvent]) -> None:
        assert ev is not None
        if ev.button() == Qt.MouseButton.LeftButton:
            self.is_released = False
            val = self.__pixel_pos_to_range_value(ev.pos())
            self.setValue(val)

        super(QJumpSlider, self).mousePressEvent(ev)
        self.sliderPressWithValue.emit(self.value())

    def mouseReleaseEvent(self, ev: Optional[QMouseEvent]) -> None:
        self.is_released = True
        return super().mouseReleaseEvent(ev)

    def __pixel_pos_to_range_value(self, pos):
        opt = QtWidgets.QStyleOptionSlider()
        self.initStyleOption(opt)
        style = self.style()
        assert style is not None
        gr = style.subControlRect(
            QtWidgets.QStyle.ComplexControl.CC_Slider,
            opt,
            QtWidgets.QStyle.SubControl.SC_SliderGroove,
            self,
        )
        sr = style.subControlRect(
            QtWidgets.QStyle.ComplexControl.CC_Slider,
            opt,
            QtWidgets.QStyle.SubControl.SC_SliderHandle,
            self,
        )

        if self.orientation() == QtCore.Qt.Orientation.Horizontal:
            sliderLength = sr.width()
            sliderMin = gr.x()
            sliderMax = gr.right() - sliderLength + 1
        else:
            sliderLength = sr.height()
            sliderMin = gr.y()
            sliderMax = gr.bottom() - sliderLength + 1
        pr = pos - sr.center() + sr.topLeft()
        p = pr.x() if self.orientation() == QtCore.Qt.Orientation.Horizontal else pr.y()
        return QtWidgets.QStyle.sliderValueFromPosition(
            self.minimum(),
            self.maximum(),
            p - sliderMin,
            sliderMax - sliderMin,
            opt.upsideDown,
        )


class VideoPlayer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.video_path = ""

        # Media Player
        self.__audio_output = QAudioOutput()
        self.__audio_output.setVolume(1)  # Set volume to 100%
        self.__media_player = QMediaPlayer(self)
        self.__media_player.setAudioOutput(self.__audio_output)
        self.__video_widget = QVideoWidget(self)
        self.__video_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.__video_path = ""

        # Controls
        self.__play_pause_button = QPushButton(QIcon(PLAY_ICON), "")
        self.__is_playing = False
        self.__force_pause = False
        self.__slider = QJumpSlider(Qt.Orientation.Horizontal)
        self.__forward_button = QPushButton(QIcon(FORWARD_ICON), "")
        original_pixmap = QPixmap(FORWARD_ICON)
        transform = QTransform().scale(-1, 1)  # Flip horizontally
        flipped_pixmap = original_pixmap.transformed(transform)
        self.__backward_button = QPushButton(QIcon(flipped_pixmap), "")
        control_layout = QHBoxLayout()
        control_layout.addWidget(self.__backward_button)
        control_layout.addWidget(self.__play_pause_button)
        control_layout.addWidget(self.__forward_button)

        # Time Labels
        self.__current_time_label = QLabel("00:00")
        self.__total_time_label = QLabel("00:00")

        # Time layout
        time_layout = QHBoxLayout()
        time_layout.addWidget(self.__current_time_label)
        time_layout.addStretch()
        time_layout.addWidget(self.__total_time_label)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.__video_widget)
        layout.addLayout(time_layout)
        layout.addWidget(self.__slider)
        layout.addLayout(control_layout)
        self.setLayout(layout)

        # Connect Media Player
        self.__media_player.setVideoOutput(self.__video_widget)
        self.__media_player.setSource(QUrl())

        # Connect Controls
        self.__play_pause_button.clicked.connect(self.__toggle_play_pause)
        self.__forward_button.clicked.connect(self.__forward_5_seconds)
        self.__backward_button.clicked.connect(self.__backward_5_seconds)

        # Update video position when the slider is moved
        self.__slider.sliderMoved.connect(self.__set_position)
        self.__slider.sliderPressWithValue.connect(self.__set_position)
        self.__slider.sliderReleased.connect(self.__on_slider_released)

        # Sync slider with video position
        self.__media_player.positionChanged.connect(self.__update_slider_and_time)
        self.__media_player.durationChanged.connect(
            self.__update_slider_range_and_total_time
        )
        self.__media_player.mediaStatusChanged.connect(self.__on_media_status_changed)

    def save(self):
        """
        Save the video.
        :return: None
        """

        saved_time = time.strftime("%Y%m%d%H%M%S")
        video_path = os.path.join(BECAP_VIDEO_PATH, f"becap_video_{saved_time}.mp4")
        shutil.copy(self.__video_path, video_path)

    def set_video(self, video_path: str) -> None:
        """
        Set the video to be played.

        :param str video_path: Path to the video file.
        :return: None
        """
        self.video_path = video_path
        self.__media_player.setSource(QUrl())  # Reset the media player
        self.__media_player.setSource(QUrl.fromLocalFile(video_path))
        self.__video_path = video_path

    def hide(self) -> None:
        self.__media_player.setSource(QUrl())  # Reset the media player
        return super().hide()

    def __on_media_status_changed(self, status: QMediaPlayer.MediaStatus):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.__is_playing = False
            self.__play_pause_button.setIcon(QIcon(PLAY_ICON))

    def __forward_5_seconds(self):
        if self.__media_player.duration() <= self.__media_player.position():
            return

        self.__media_player.setPosition(self.__media_player.position() + 5000)
        self.__current_time_label.setText(
            self.__format_time(self.__media_player.position())
        )
        self.__slider.setValue(self.__media_player.position())

    def __backward_5_seconds(self):
        if self.__media_player.position() <= 0:
            return

        self.__media_player.setPosition(self.__media_player.position() - 5000)
        self.__current_time_label.setText(
            self.__format_time(self.__media_player.position())
        )
        self.__slider.setValue(self.__media_player.position())

    def __on_slider_released(self):
        self.__force_pause = False
        if self.__is_playing:
            self.__media_player.play()

    def __set_position(self, position: int):
        """Set video position based on slider movement."""
        # If we are using the slider, the video should be paused
        if not self.__force_pause:
            self.__force_pause = True
            self.__media_player.pause()

        self.__media_player.setPosition(position)
        self.__current_time_label.setText(self.__format_time(position))

    def __update_slider_and_time(self, position: int):
        """Update the slider position to reflect the current video position."""
        self.__slider.setValue(position)
        self.__current_time_label.setText(self.__format_time(position))

    def __update_slider_range_and_total_time(self, duration: int):
        """Update the slider range based on the video duration."""
        self.__slider.setRange(0, duration)
        self.__total_time_label.setText(self.__format_time(duration))

    @staticmethod
    def __format_time(milliseconds):
        """Format time in milliseconds to mm:ss."""
        seconds = milliseconds // 1000
        minutes = seconds // 60
        seconds %= 60
        return f"{minutes:02}:{seconds:02}"

    def __toggle_play_pause(self):
        if self.__is_playing:
            self.__media_player.pause()
            self.__play_pause_button.setIcon(QIcon(PLAY_ICON))
        else:
            self.__media_player.play()
            self.__play_pause_button.setIcon(QIcon(PAUSE_ICON))
        self.__is_playing = not self.__is_playing
