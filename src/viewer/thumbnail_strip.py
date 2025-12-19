"""
썸네일 스트립 - 비동기 로딩, 가상 스크롤 지원, 높이 조절 가능
"""
from typing import List, Optional
from PySide6.QtWidgets import (
    QWidget, QScrollArea, QHBoxLayout, QLabel, QFrame,
    QSizePolicy, QVBoxLayout
)
from PySide6.QtCore import Qt, Signal, QSize, QThreadPool, QTimer
from PySide6.QtGui import QPixmap, QPainter, QColor, QPen, QFont, QMouseEvent

from utils.image_loader import ImageLoader, ThumbnailWorker, ThumbnailCache


class ResizeHandle(QWidget):
    """썸네일 스트립 상단 리사이즈 핸들"""

    HEIGHT = 6

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(self.HEIGHT)
        self.setCursor(Qt.CursorShape.SplitVCursor)
        self._dragging = False
        self._start_y = 0
        self._start_height = 0
        self.setStyleSheet("""
            ResizeHandle {
                background-color: #0a0a0a;
            }
            ResizeHandle:hover {
                background-color: #1a1a1a;
            }
        """)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 그립 라인 그리기 (중앙에 3개의 점선)
        center_x = self.width() // 2
        y = self.HEIGHT // 2

        painter.setPen(QPen(QColor('#404040'), 1))
        for offset in [-20, 0, 20]:
            painter.drawLine(center_x + offset - 8, y, center_x + offset + 8, y)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._start_y = event.globalPosition().y()
            self._start_height = self.parent().height()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._dragging:
            delta = self._start_y - event.globalPosition().y()
            new_height = int(self._start_height + delta)
            parent = self.parent()
            if parent and hasattr(parent, 'set_strip_height'):
                parent.set_strip_height(new_height)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False
            event.accept()


class ThumbnailItem(QFrame):
    """개별 썸네일 아이템"""

    clicked = Signal(int)  # index

    THUMB_SIZE = 80
    SELECTED_BORDER = 3

    def __init__(self, index: int, file_path: str, parent=None):
        super().__init__(parent)
        self.index = index
        self.file_path = file_path
        self._pixmap: Optional[QPixmap] = None
        self._is_selected = False
        self._is_loading = False
        self._is_video = ImageLoader.is_supported_video(file_path)

        self._setup_ui()

    def _setup_ui(self):
        self.setFixedSize(self.THUMB_SIZE + 8, self.THUMB_SIZE + 8)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._update_style()

    def _update_style(self):
        if self._is_selected:
            self.setStyleSheet(f"""
                ThumbnailItem {{
                    background-color: #0078d4;
                    border: {self.SELECTED_BORDER}px solid #0078d4;
                    border-radius: 4px;
                }}
            """)
        else:
            self.setStyleSheet("""
                ThumbnailItem {
                    background-color: #1a1a1a;
                    border: 2px solid transparent;
                    border-radius: 4px;
                }
                ThumbnailItem:hover {
                    border: 2px solid #404040;
                }
            """)

    def set_selected(self, selected: bool):
        self._is_selected = selected
        self._update_style()
        self.update()

    def set_pixmap(self, pixmap: QPixmap):
        self._pixmap = pixmap
        self._is_loading = False
        self.update()

    def set_loading(self):
        self._is_loading = True
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        # 컨텐츠 영역
        margin = 4 if not self._is_selected else self.SELECTED_BORDER + 1
        content_rect = self.rect().adjusted(margin, margin, -margin, -margin)

        if self._pixmap:
            # 썸네일 그리기 (중앙 정렬)
            scaled = self._pixmap.scaled(
                content_rect.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            x = content_rect.x() + (content_rect.width() - scaled.width()) // 2
            y = content_rect.y() + (content_rect.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)

            # 동영상 아이콘
            if self._is_video:
                self._draw_video_icon(painter, content_rect)
        elif self._is_loading:
            # 로딩 중 표시
            painter.setPen(QColor('#888888'))
            painter.drawText(content_rect, Qt.AlignmentFlag.AlignCenter, "...")
        else:
            # 빈 상태
            painter.fillRect(content_rect, QColor('#1a1a1a'))

    def _draw_video_icon(self, painter: QPainter, rect):
        """동영상 아이콘 (재생 버튼)"""
        icon_size = 20
        x = rect.right() - icon_size - 4
        y = rect.bottom() - icon_size - 4

        # 반투명 원
        painter.setBrush(QColor(0, 0, 0, 180))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(x, y, icon_size, icon_size)

        # 재생 삼각형
        painter.setBrush(QColor('#ffffff'))
        points = [
            (x + 7, y + 5),
            (x + 7, y + 15),
            (x + 16, y + 10),
        ]
        from PySide6.QtGui import QPolygon
        from PySide6.QtCore import QPoint
        polygon = QPolygon([QPoint(px, py) for px, py in points])
        painter.drawPolygon(polygon)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.index)
        super().mousePressEvent(event)


class ThumbnailStrip(QWidget):
    """썸네일 스트립 위젯"""

    item_selected = Signal(int, str)  # index, file_path

    VISIBLE_BUFFER = 5  # 화면 밖 버퍼 (가상 스크롤용)
    MIN_HEIGHT = 80
    MAX_HEIGHT = 300
    DEFAULT_HEIGHT = ThumbnailItem.THUMB_SIZE + 24 + ResizeHandle.HEIGHT

    def __init__(self, parent=None):
        super().__init__(parent)
        self._files: List[str] = []
        self._items: List[ThumbnailItem] = []
        self._current_index = -1
        self._cache = ThumbnailCache(max_items=500, max_memory_mb=100)
        self._thread_pool = QThreadPool.globalInstance()
        self._pending_workers: dict = {}  # {path: worker}
        self._current_height = self.DEFAULT_HEIGHT

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 리사이즈 핸들 (상단)
        self._resize_handle = ResizeHandle(self)
        layout.addWidget(self._resize_handle)

        # 스크롤 영역
        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #0a0a0a;
                border: none;
            }
        """)

        # 최소/최대 높이 설정 (fixedHeight 대신)
        self.setMinimumHeight(self.MIN_HEIGHT)
        self.setMaximumHeight(self.MAX_HEIGHT)
        self.setFixedHeight(self.DEFAULT_HEIGHT)

        # 컨테이너
        self._container = QWidget()
        self._container_layout = QHBoxLayout(self._container)
        self._container_layout.setContentsMargins(8, 8, 8, 8)
        self._container_layout.setSpacing(4)
        self._container_layout.addStretch()

        self._scroll_area.setWidget(self._container)
        layout.addWidget(self._scroll_area)

        # 가시성 체크 타이머 (가상 스크롤)
        self._visibility_timer = QTimer()
        self._visibility_timer.timeout.connect(self._load_visible_thumbnails)
        self._visibility_timer.setInterval(100)

        # 스크롤 이벤트 연결
        self._scroll_area.horizontalScrollBar().valueChanged.connect(
            self._on_scroll_changed
        )

    def set_files(self, files: List[str]):
        """파일 목록 설정"""
        self._clear_items()
        self._files = files
        self._current_index = -1

        # 아이템 생성 (썸네일은 아직 로드하지 않음)
        for i, file_path in enumerate(files):
            item = ThumbnailItem(i, file_path)
            item.clicked.connect(self._on_item_clicked)
            self._items.append(item)
            self._container_layout.insertWidget(i, item)

        # 가시 영역 썸네일 로드 시작
        self._visibility_timer.start()

    def _clear_items(self):
        """모든 아이템 제거"""
        self._visibility_timer.stop()

        # 진행 중인 워커 취소
        for worker in self._pending_workers.values():
            worker.cancel()
        self._pending_workers.clear()

        # 아이템 제거
        for item in self._items:
            self._container_layout.removeWidget(item)
            item.deleteLater()
        self._items.clear()

    def select_index(self, index: int):
        """인덱스 선택"""
        if index < 0 or index >= len(self._items):
            return

        # 이전 선택 해제
        if 0 <= self._current_index < len(self._items):
            self._items[self._current_index].set_selected(False)

        # 새 선택
        self._current_index = index
        self._items[index].set_selected(True)

        # 선택된 아이템으로 스크롤
        self._scroll_to_item(index)

    def _scroll_to_item(self, index: int):
        """아이템이 보이도록 스크롤"""
        if index < 0 or index >= len(self._items):
            return

        item = self._items[index]
        self._scroll_area.ensureWidgetVisible(item, 50, 0)

    def _on_item_clicked(self, index: int):
        """아이템 클릭 처리"""
        if 0 <= index < len(self._files):
            self.select_index(index)
            self.item_selected.emit(index, self._files[index])

    def _on_scroll_changed(self):
        """스크롤 변경 시 가시 영역 썸네일 로드"""
        self._load_visible_thumbnails()

    def _load_visible_thumbnails(self):
        """화면에 보이는 썸네일만 로드 (가상 스크롤)"""
        if not self._items:
            return

        viewport = self._scroll_area.viewport()
        scroll_x = self._scroll_area.horizontalScrollBar().value()
        visible_width = viewport.width()

        # 가시 범위 계산
        item_width = ThumbnailItem.THUMB_SIZE + 12
        start_idx = max(0, scroll_x // item_width - self.VISIBLE_BUFFER)
        end_idx = min(
            len(self._items),
            (scroll_x + visible_width) // item_width + self.VISIBLE_BUFFER + 1
        )

        # 가시 영역 아이템 로드
        for i in range(start_idx, end_idx):
            self._load_thumbnail(i)

    def _load_thumbnail(self, index: int):
        """개별 썸네일 로드"""
        if index < 0 or index >= len(self._items):
            return

        item = self._items[index]
        file_path = self._files[index]

        # 이미 로드됨
        if item._pixmap is not None:
            return

        # 캐시 확인
        cached = self._cache.get(file_path)
        if cached:
            item.set_pixmap(cached)
            return

        # 이미 로딩 중
        if file_path in self._pending_workers:
            return

        # 동영상은 기본 아이콘 (썸네일 추출 없음)
        if ImageLoader.is_supported_video(file_path):
            # TODO: 동영상 썸네일 추출 구현
            item.set_loading()
            return

        # 비동기 로드 시작
        item.set_loading()
        worker = ThumbnailWorker(file_path, size=(ThumbnailItem.THUMB_SIZE, ThumbnailItem.THUMB_SIZE))
        worker.signals.finished.connect(self._on_thumbnail_loaded)
        worker.signals.error.connect(self._on_thumbnail_error)
        self._pending_workers[file_path] = worker
        self._thread_pool.start(worker)

    def _on_thumbnail_loaded(self, file_path: str, pixmap: QPixmap):
        """썸네일 로드 완료"""
        # 캐시에 저장
        self._cache.put(file_path, pixmap)

        # 아이템 업데이트
        if file_path in self._pending_workers:
            del self._pending_workers[file_path]

        for i, f in enumerate(self._files):
            if f == file_path and i < len(self._items):
                self._items[i].set_pixmap(pixmap)
                break

    def _on_thumbnail_error(self, file_path: str, error: str):
        """썸네일 로드 실패"""
        if file_path in self._pending_workers:
            del self._pending_workers[file_path]

    def get_current_index(self) -> int:
        return self._current_index

    def get_file_count(self) -> int:
        return len(self._files)

    def set_strip_height(self, height: int):
        """높이 설정 (드래그 리사이즈용)"""
        height = max(self.MIN_HEIGHT, min(self.MAX_HEIGHT, height))
        self._current_height = height
        self.setFixedHeight(height)
