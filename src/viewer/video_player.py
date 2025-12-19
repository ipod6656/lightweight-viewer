"""
동영상 플레이어 위젯 - QtMultimedia 기반
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QSlider, QLabel, QStyle, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QUrl
from PySide6.QtGui import QKeyEvent
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget


class VideoPlayer(QWidget):
    """동영상 플레이어 위젯"""

    # 시그널
    next_requested = Signal()
    prev_requested = Signal()
    fullscreen_toggled = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._setup_player()
        self._connect_signals()

    def _setup_ui(self):
        self.setStyleSheet("background-color: #000000;")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 비디오 위젯
        self._video_widget = QVideoWidget()
        self._video_widget.setStyleSheet("background-color: #000000;")
        layout.addWidget(self._video_widget, 1)

        # 컨트롤 바
        self._control_bar = QWidget()
        self._control_bar.setFixedHeight(40)
        self._control_bar.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 0.7);
            }
            QPushButton {
                background-color: transparent;
                border: none;
                color: white;
                font-size: 16px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
            QSlider::groove:horizontal {
                background: #404040;
                height: 4px;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #ffffff;
                width: 12px;
                height: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }
            QSlider::sub-page:horizontal {
                background: #0078d4;
                border-radius: 2px;
            }
            QLabel {
                color: white;
                font-size: 12px;
            }
        """)

        control_layout = QHBoxLayout(self._control_bar)
        control_layout.setContentsMargins(10, 0, 10, 0)
        control_layout.setSpacing(10)

        # 재생/일시정지 버튼
        self._play_btn = QPushButton("▶")
        self._play_btn.setFixedWidth(40)
        control_layout.addWidget(self._play_btn)

        # 현재 시간
        self._time_label = QLabel("0:00")
        self._time_label.setFixedWidth(45)
        control_layout.addWidget(self._time_label)

        # 진행 슬라이더
        self._progress_slider = QSlider(Qt.Orientation.Horizontal)
        self._progress_slider.setRange(0, 1000)
        control_layout.addWidget(self._progress_slider, 1)

        # 전체 시간
        self._duration_label = QLabel("0:00")
        self._duration_label.setFixedWidth(45)
        control_layout.addWidget(self._duration_label)

        # 볼륨 슬라이더
        self._volume_slider = QSlider(Qt.Orientation.Horizontal)
        self._volume_slider.setRange(0, 100)
        self._volume_slider.setValue(100)
        self._volume_slider.setFixedWidth(80)
        control_layout.addWidget(self._volume_slider)

        layout.addWidget(self._control_bar)

    def _setup_player(self):
        self._player = QMediaPlayer()
        self._audio_output = QAudioOutput()
        self._player.setAudioOutput(self._audio_output)
        self._player.setVideoOutput(self._video_widget)
        self._audio_output.setVolume(1.0)

        self._is_seeking = False

    def _connect_signals(self):
        self._play_btn.clicked.connect(self._toggle_play)
        self._progress_slider.sliderPressed.connect(self._on_slider_pressed)
        self._progress_slider.sliderReleased.connect(self._on_slider_released)
        self._progress_slider.sliderMoved.connect(self._on_slider_moved)
        self._volume_slider.valueChanged.connect(self._on_volume_changed)

        self._player.positionChanged.connect(self._on_position_changed)
        self._player.durationChanged.connect(self._on_duration_changed)
        self._player.playbackStateChanged.connect(self._on_state_changed)

    def set_video(self, file_path: str):
        """동영상 파일 설정 및 재생"""
        self._player.setSource(QUrl.fromLocalFile(file_path))
        self._player.play()

    def clear(self):
        """플레이어 정리"""
        self._player.stop()
        self._player.setSource(QUrl())

    def _toggle_play(self):
        if self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self._player.pause()
        else:
            self._player.play()

    def _on_state_changed(self, state):
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self._play_btn.setText("⏸")
        else:
            self._play_btn.setText("▶")

    def _on_position_changed(self, position):
        if not self._is_seeking:
            duration = self._player.duration()
            if duration > 0:
                self._progress_slider.setValue(int(position * 1000 / duration))
        self._time_label.setText(self._format_time(position))

    def _on_duration_changed(self, duration):
        self._duration_label.setText(self._format_time(duration))

    def _on_slider_pressed(self):
        self._is_seeking = True

    def _on_slider_released(self):
        self._is_seeking = False
        duration = self._player.duration()
        position = int(self._progress_slider.value() * duration / 1000)
        self._player.setPosition(position)

    def _on_slider_moved(self, value):
        duration = self._player.duration()
        position = int(value * duration / 1000)
        self._time_label.setText(self._format_time(position))

    def _on_volume_changed(self, value):
        self._audio_output.setVolume(value / 100)

    def _format_time(self, ms: int) -> str:
        """밀리초를 시:분:초 형식으로 변환"""
        seconds = ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        if minutes >= 60:
            hours = minutes // 60
            minutes = minutes % 60
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        return f"{minutes}:{seconds:02d}"

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()

        if key == Qt.Key.Key_Space:
            self._toggle_play()
        elif key == Qt.Key.Key_Left:
            # 5초 뒤로
            self._player.setPosition(max(0, self._player.position() - 5000))
        elif key == Qt.Key.Key_Right:
            # 5초 앞으로
            self._player.setPosition(min(self._player.duration(), self._player.position() + 5000))
        elif key == Qt.Key.Key_Up:
            # 볼륨 증가
            self._volume_slider.setValue(min(100, self._volume_slider.value() + 5))
        elif key == Qt.Key.Key_Down:
            # 볼륨 감소
            self._volume_slider.setValue(max(0, self._volume_slider.value() - 5))
        elif key == Qt.Key.Key_F11 or key == Qt.Key.Key_Escape:
            self.fullscreen_toggled.emit()
        elif key == Qt.Key.Key_PageUp:
            self.prev_requested.emit()
        elif key == Qt.Key.Key_PageDown:
            self.next_requested.emit()
        else:
            super().keyPressEvent(event)

    def mouseDoubleClickEvent(self, event):
        """더블클릭 - 전체화면 토글"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.fullscreen_toggled.emit()
        super().mouseDoubleClickEvent(event)

    def show_controls(self, show: bool = True):
        """컨트롤 바 표시/숨김"""
        self._control_bar.setVisible(show)

    def stop(self):
        """재생 정지"""
        self._player.stop()
