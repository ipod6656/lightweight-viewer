"""
메인 윈도우 - 전체 앱 구성
"""
import os
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QMenu, QFileDialog, QMessageBox, QDialog, QComboBox,
    QPushButton, QGroupBox, QFormLayout, QSpinBox, QDialogButtonBox
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QKeySequence, QDragEnterEvent, QDropEvent

from .image_viewer import ImageViewer
from .thumbnail_strip import ThumbnailStrip
from utils.image_loader import ImageLoader
from utils.compressor import ImageCompressor


class CompressionDialog(QDialog):
    """이미지 압축 대화상자"""

    def __init__(self, file_path: str, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.result = None

        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle("이미지 압축")
        self.setFixedWidth(350)

        layout = QVBoxLayout(self)

        # 파일 정보
        info = ImageLoader.get_image_info(self.file_path)
        info_label = QLabel(
            f"파일: {info['filename']}\n"
            f"크기: {ImageLoader.format_file_size(info['size_bytes'])}\n"
            f"해상도: {info['width']} x {info['height']}"
        )
        layout.addWidget(info_label)

        # 품질 설정
        quality_group = QGroupBox("품질")
        quality_layout = QFormLayout(quality_group)

        self._quality_combo = QComboBox()
        self._quality_combo.addItem("고품질 (90%)", 90)
        self._quality_combo.addItem("중간 (80%)", 80)
        self._quality_combo.addItem("저품질 (70%)", 70)
        self._quality_combo.setCurrentIndex(1)
        quality_layout.addRow("품질:", self._quality_combo)

        layout.addWidget(quality_group)

        # 해상도 설정
        resolution_group = QGroupBox("해상도")
        resolution_layout = QFormLayout(resolution_group)

        self._resolution_combo = QComboBox()
        self._resolution_combo.addItem("원본 유지", None)
        self._resolution_combo.addItem("4K (3840px)", 3840)
        self._resolution_combo.addItem("2K (2560px)", 2560)
        self._resolution_combo.addItem("Full HD (1920px)", 1920)
        self._resolution_combo.addItem("HD (1280px)", 1280)
        resolution_layout.addRow("최대 너비:", self._resolution_combo)

        layout.addWidget(resolution_group)

        # 포맷 설정
        format_group = QGroupBox("출력 포맷")
        format_layout = QFormLayout(format_group)

        self._format_combo = QComboBox()
        self._format_combo.addItem("JPEG", "JPEG")
        self._format_combo.addItem("WebP", "WEBP")
        self._format_combo.addItem("PNG", "PNG")
        format_layout.addRow("포맷:", self._format_combo)

        layout.addWidget(format_group)

        # 버튼
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _on_accept(self):
        quality = self._quality_combo.currentData()
        max_width = self._resolution_combo.currentData()
        output_format = self._format_combo.currentData()

        self.result = ImageCompressor.compress(
            input_path=self.file_path,
            quality=quality,
            max_width=max_width,
            output_format=output_format
        )
        self.accept()


class MainWindow(QMainWindow):
    """메인 윈도우"""

    def __init__(self):
        super().__init__()
        self._current_file: Optional[str] = None
        self._current_folder: Optional[str] = None
        self._files: list = []
        self._current_index = -1
        self._was_maximized = False

        self._setup_ui()
        self._setup_menu()
        self._setup_shortcuts()

    def _setup_ui(self):
        self.setWindowTitle("Lightweight Viewer")
        self.setMinimumSize(800, 600)
        self.resize(1200, 800)

        # 드래그 앤 드롭 활성화
        self.setAcceptDrops(True)

        # 중앙 위젯
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 상단 정보 바
        self._info_bar = QWidget()
        self._info_bar.setFixedHeight(32)
        self._info_bar.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                border-bottom: 1px solid #3d3d3d;
            }
            QLabel {
                color: #cccccc;
                padding: 0 8px;
            }
        """)

        info_layout = QHBoxLayout(self._info_bar)
        info_layout.setContentsMargins(8, 0, 8, 0)

        self._filename_label = QLabel("")
        self._resolution_label = QLabel("")
        self._filesize_label = QLabel("")
        self._index_label = QLabel("")

        info_layout.addWidget(self._filename_label)
        info_layout.addStretch()
        info_layout.addWidget(self._resolution_label)
        info_layout.addWidget(self._filesize_label)
        info_layout.addWidget(self._index_label)

        layout.addWidget(self._info_bar)

        # 이미지 뷰어
        self._viewer = ImageViewer()
        self._viewer.next_requested.connect(self._next_image)
        self._viewer.prev_requested.connect(self._prev_image)
        self._viewer.fullscreen_toggled.connect(self._toggle_fullscreen)
        layout.addWidget(self._viewer, 1)

        # 썸네일 스트립
        self._thumbnail_strip = ThumbnailStrip()
        self._thumbnail_strip.item_selected.connect(self._on_thumbnail_selected)
        layout.addWidget(self._thumbnail_strip)

    def _setup_menu(self):
        menubar = self.menuBar()

        # 파일 메뉴
        file_menu = menubar.addMenu("파일(&F)")

        open_action = QAction("열기(&O)...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._open_file_dialog)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        exit_action = QAction("종료(&X)", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 보기 메뉴
        view_menu = menubar.addMenu("보기(&V)")

        zoom_in_action = QAction("확대(&I)", self)
        zoom_in_action.setShortcut(QKeySequence.StandardKey.ZoomIn)
        zoom_in_action.triggered.connect(self._viewer.zoom_in)
        view_menu.addAction(zoom_in_action)

        zoom_out_action = QAction("축소(&O)", self)
        zoom_out_action.setShortcut(QKeySequence.StandardKey.ZoomOut)
        zoom_out_action.triggered.connect(self._viewer.zoom_out)
        view_menu.addAction(zoom_out_action)

        zoom_fit_action = QAction("창에 맞춤(&F)", self)
        zoom_fit_action.setShortcut("0")
        zoom_fit_action.triggered.connect(self._viewer.zoom_fit)
        view_menu.addAction(zoom_fit_action)

        zoom_actual_action = QAction("실제 크기(&A)", self)
        zoom_actual_action.setShortcut("1")
        zoom_actual_action.triggered.connect(self._viewer.zoom_actual)
        view_menu.addAction(zoom_actual_action)

        view_menu.addSeparator()

        fullscreen_action = QAction("전체 화면(&U)", self)
        fullscreen_action.setShortcut("F11")
        fullscreen_action.triggered.connect(self._toggle_fullscreen)
        view_menu.addAction(fullscreen_action)

        # 도구 메뉴
        tools_menu = menubar.addMenu("도구(&T)")

        compress_action = QAction("이미지 압축(&C)...", self)
        compress_action.setShortcut("Ctrl+Shift+S")
        compress_action.triggered.connect(self._show_compress_dialog)
        tools_menu.addAction(compress_action)

    def _setup_shortcuts(self):
        """추가 단축키 설정"""
        pass  # 키보드 이벤트는 ImageViewer에서 처리

    def _setup_context_menu(self):
        """컨텍스트 메뉴 설정"""
        self._viewer.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._viewer.customContextMenuRequested.connect(self._show_context_menu)

    def _show_context_menu(self, pos):
        if not self._current_file:
            return

        menu = QMenu(self)

        compress_action = menu.addAction("이미지 압축...")
        compress_action.triggered.connect(self._show_compress_dialog)

        menu.addSeparator()

        open_folder_action = menu.addAction("폴더에서 열기")
        open_folder_action.triggered.connect(self._open_containing_folder)

        menu.exec(self._viewer.mapToGlobal(pos))

    def _open_containing_folder(self):
        """탐색기에서 폴더 열기"""
        if self._current_file:
            import subprocess
            folder = os.path.dirname(self._current_file)
            if os.name == 'nt':
                subprocess.run(['explorer', '/select,', self._current_file])
            else:
                subprocess.run(['open', '-R', self._current_file])

    def open_file(self, file_path: str):
        """파일 열기"""
        if not os.path.isfile(file_path):
            return

        self._current_file = file_path
        self._current_folder = os.path.dirname(file_path)

        # 폴더 내 파일 목록 가져오기
        self._files = ImageLoader.get_files_in_folder(self._current_folder)

        # 현재 파일 인덱스 찾기
        try:
            self._current_index = self._files.index(file_path)
        except ValueError:
            self._current_index = 0

        # 썸네일 스트립 업데이트
        self._thumbnail_strip.set_files(self._files)
        self._thumbnail_strip.select_index(self._current_index)

        # 이미지 로드
        self._load_current_image()

    def _load_current_image(self):
        """현재 이미지 로드"""
        if not self._current_file:
            return

        if ImageLoader.is_supported_image(self._current_file):
            pixmap = ImageLoader.load_image(self._current_file)
            if pixmap:
                self._viewer.set_image(pixmap)
            else:
                self._viewer.clear()
        else:
            # 동영상은 아직 미지원
            self._viewer.clear()

        self._update_info_bar()

    def _update_info_bar(self):
        """정보 바 업데이트"""
        if not self._current_file:
            self._filename_label.setText("")
            self._resolution_label.setText("")
            self._filesize_label.setText("")
            self._index_label.setText("")
            return

        info = ImageLoader.get_image_info(self._current_file)

        self._filename_label.setText(info['filename'])
        self._resolution_label.setText(f"{info['width']} x {info['height']}")
        self._filesize_label.setText(ImageLoader.format_file_size(info['size_bytes']))
        self._index_label.setText(f"{self._current_index + 1} / {len(self._files)}")

        self.setWindowTitle(f"{info['filename']} - Lightweight Viewer")

    def _next_image(self):
        """다음 이미지"""
        if self._current_index < len(self._files) - 1:
            self._current_index += 1
            self._current_file = self._files[self._current_index]
            self._thumbnail_strip.select_index(self._current_index)
            self._load_current_image()

    def _prev_image(self):
        """이전 이미지"""
        if self._current_index > 0:
            self._current_index -= 1
            self._current_file = self._files[self._current_index]
            self._thumbnail_strip.select_index(self._current_index)
            self._load_current_image()

    def _on_thumbnail_selected(self, index: int, file_path: str):
        """썸네일 선택"""
        self._current_index = index
        self._current_file = file_path
        self._load_current_image()

    def _toggle_fullscreen(self):
        """전체 화면 토글"""
        if self.isFullScreen():
            # 전체 화면 해제
            if self._was_maximized:
                self.showMaximized()
            else:
                self.showNormal()
            self._info_bar.show()
            self._thumbnail_strip.show()
            self.menuBar().show()
        else:
            # 전체 화면
            self._was_maximized = self.isMaximized()
            self._info_bar.hide()
            self._thumbnail_strip.hide()
            self.menuBar().hide()
            self.showFullScreen()

    def _open_file_dialog(self):
        """파일 열기 대화상자"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "이미지 열기",
            "",
            "이미지 파일 (*.jpg *.jpeg *.png *.bmp *.webp *.gif *.heic *.heif);;모든 파일 (*.*)"
        )
        if file_path:
            self.open_file(file_path)

    def _show_compress_dialog(self):
        """압축 대화상자 표시"""
        if not self._current_file or not ImageLoader.is_supported_image(self._current_file):
            QMessageBox.warning(self, "압축 불가", "이미지 파일을 먼저 열어주세요.")
            return

        dialog = CompressionDialog(self._current_file, self)
        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.result:
            result = dialog.result
            if result.success:
                QMessageBox.information(
                    self, "압축 완료",
                    f"압축이 완료되었습니다.\n\n"
                    f"원본: {result.original_size_str}\n"
                    f"압축: {result.compressed_size_str}\n"
                    f"절감: {result.size_reduction:.1f}%\n\n"
                    f"저장 위치: {result.output_path}"
                )
                # 폴더 새로고침
                self.open_file(self._current_file)
            else:
                QMessageBox.warning(
                    self, "압축 실패",
                    f"압축 중 오류가 발생했습니다.\n{result.error_message}"
                )

    def dragEnterEvent(self, event: QDragEnterEvent):
        """드래그 진입"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        """드롭"""
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if ImageLoader.is_supported_file(file_path):
                self.open_file(file_path)

    def keyPressEvent(self, event):
        """키 이벤트 (뷰어로 전달)"""
        self._viewer.keyPressEvent(event)
