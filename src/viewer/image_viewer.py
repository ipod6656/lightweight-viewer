"""
이미지 뷰어 위젯 - 확대/축소, 드래그, 전체화면 지원
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from PySide6.QtCore import Qt, Signal, QPoint, QSize, QRectF
from PySide6.QtGui import QPixmap, QPainter, QWheelEvent, QMouseEvent, QKeyEvent


class ImageViewer(QWidget):
    """이미지 뷰어 위젯"""

    # 시그널
    next_requested = Signal()      # 다음 이미지 요청
    prev_requested = Signal()      # 이전 이미지 요청
    fullscreen_toggled = Signal()  # 전체화면 토글

    # 줌 설정
    MIN_ZOOM = 0.1   # 10%
    MAX_ZOOM = 10.0  # 1000%
    ZOOM_STEP = 1.15  # 15% 단위

    def __init__(self, parent=None):
        super().__init__(parent)
        self._pixmap: QPixmap = None
        self._zoom = 1.0
        self._pan_offset = QPoint(0, 0)
        self._is_panning = False
        self._pan_start = QPoint(0, 0)
        self._fit_mode = True  # True: 창에 맞춤, False: 실제 크기/줌

        self._setup_ui()

    def _setup_ui(self):
        self.setMinimumSize(200, 200)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # 배경색 설정
        self.setStyleSheet("background-color: #000000;")

    def set_image(self, pixmap: QPixmap):
        """이미지 설정"""
        self._pixmap = pixmap
        self._zoom = 1.0
        self._pan_offset = QPoint(0, 0)
        self._fit_mode = True
        self.update()

    def clear(self):
        """이미지 제거"""
        self._pixmap = None
        self.update()

    def get_zoom_percent(self) -> int:
        """현재 줌 레벨 (퍼센트)"""
        if self._fit_mode and self._pixmap:
            return int(self._calculate_fit_zoom() * 100)
        return int(self._zoom * 100)

    def _calculate_fit_zoom(self) -> float:
        """창에 맞추는 줌 레벨 계산"""
        if not self._pixmap:
            return 1.0

        widget_size = self.size()
        pixmap_size = self._pixmap.size()

        width_ratio = widget_size.width() / pixmap_size.width()
        height_ratio = widget_size.height() / pixmap_size.height()

        return min(width_ratio, height_ratio, 1.0)  # 원본보다 크게 확대하지 않음

    def _get_effective_zoom(self) -> float:
        """현재 적용되는 줌 레벨"""
        if self._fit_mode:
            return self._calculate_fit_zoom()
        return self._zoom

    def zoom_in(self):
        """확대"""
        if self._fit_mode:
            # fit 모드에서 첫 확대 시 현재 fit_zoom을 기준으로 시작
            self._zoom = self._calculate_fit_zoom()
            self._fit_mode = False
        self._zoom = min(self._zoom * self.ZOOM_STEP, self.MAX_ZOOM)
        self.update()

    def zoom_out(self):
        """축소"""
        if self._fit_mode:
            # fit 모드에서 첫 축소 시 현재 fit_zoom을 기준으로 시작
            self._zoom = self._calculate_fit_zoom()
            self._fit_mode = False
        self._zoom = max(self._zoom / self.ZOOM_STEP, self.MIN_ZOOM)
        self.update()

    def zoom_fit(self):
        """창에 맞춤"""
        self._fit_mode = True
        self._pan_offset = QPoint(0, 0)
        self.update()

    def zoom_actual(self):
        """실제 크기 (100%)"""
        self._fit_mode = False
        self._zoom = 1.0
        self._pan_offset = QPoint(0, 0)
        self.update()

    def paintEvent(self, event):
        """이미지 그리기"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        # 배경
        painter.fillRect(self.rect(), Qt.GlobalColor.black)

        if not self._pixmap:
            return

        # 줌 적용된 크기
        zoom = self._get_effective_zoom()
        scaled_width = int(self._pixmap.width() * zoom)
        scaled_height = int(self._pixmap.height() * zoom)

        # 중앙 정렬 + 팬 오프셋
        x = (self.width() - scaled_width) // 2 + self._pan_offset.x()
        y = (self.height() - scaled_height) // 2 + self._pan_offset.y()

        # 대상 영역
        target_rect = QRectF(x, y, scaled_width, scaled_height)
        source_rect = QRectF(0, 0, self._pixmap.width(), self._pixmap.height())

        painter.drawPixmap(target_rect, self._pixmap, source_rect)

    def wheelEvent(self, event: QWheelEvent):
        """마우스 휠 - 줌"""
        if not self._pixmap:
            return

        # 휠 방향에 따라 줌
        delta = event.angleDelta().y()
        if delta > 0:
            self.zoom_in()
        elif delta < 0:
            self.zoom_out()

    def mousePressEvent(self, event: QMouseEvent):
        """마우스 클릭 - 드래그 시작"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_panning = True
            self._pan_start = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        """마우스 이동 - 드래그"""
        if self._is_panning:
            delta = event.pos() - self._pan_start
            self._pan_offset += delta
            self._pan_start = event.pos()
            self._fit_mode = False
            self.update()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """마우스 릴리즈 - 드래그 종료"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """더블클릭 - 전체화면 토글"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.fullscreen_toggled.emit()
        super().mouseDoubleClickEvent(event)

    def keyPressEvent(self, event: QKeyEvent):
        """키보드 이벤트"""
        key = event.key()

        if key == Qt.Key.Key_Left:
            self.prev_requested.emit()
        elif key == Qt.Key.Key_Right:
            self.next_requested.emit()
        elif key == Qt.Key.Key_F11:
            self.fullscreen_toggled.emit()
        elif key == Qt.Key.Key_Escape:
            self.fullscreen_toggled.emit()  # ESC로 전체화면 해제
        elif key == Qt.Key.Key_Plus or key == Qt.Key.Key_Equal:
            self.zoom_in()
        elif key == Qt.Key.Key_Minus:
            self.zoom_out()
        elif key == Qt.Key.Key_0:
            self.zoom_fit()
        elif key == Qt.Key.Key_1:
            self.zoom_actual()
        else:
            super().keyPressEvent(event)

    def resizeEvent(self, event):
        """창 크기 변경 시 업데이트"""
        super().resizeEvent(event)
        self.update()
