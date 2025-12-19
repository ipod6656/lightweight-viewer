"""
이미지 로딩 유틸리티 - HEIC 포함 다양한 포맷 지원
"""
import os
from pathlib import Path
from typing import Optional, Tuple, List
from io import BytesIO

from PIL import Image, ExifTags
from PySide6.QtCore import QThread, Signal, QObject, QRunnable, QThreadPool, QMutex, QMutexLocker
from PySide6.QtGui import QImage, QPixmap

# HEIC 지원 - 설치되어 있으면 활성화
try:
    import pillow_heif
    pillow_heif.register_heif_opener()
    HEIC_SUPPORTED = True
except ImportError:
    HEIC_SUPPORTED = False

# 지원 포맷
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.webp', '.gif'}
if HEIC_SUPPORTED:
    IMAGE_EXTENSIONS.update({'.heic', '.heif'})

VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.avi', '.mov', '.webm'}
ALL_EXTENSIONS = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS


class ImageLoader:
    """이미지 로딩 및 처리 클래스"""

    @staticmethod
    def is_supported_image(file_path: str) -> bool:
        """지원되는 이미지 파일인지 확인"""
        ext = Path(file_path).suffix.lower()
        return ext in IMAGE_EXTENSIONS

    @staticmethod
    def is_supported_video(file_path: str) -> bool:
        """지원되는 동영상 파일인지 확인"""
        ext = Path(file_path).suffix.lower()
        return ext in VIDEO_EXTENSIONS

    @staticmethod
    def is_supported_file(file_path: str) -> bool:
        """지원되는 파일인지 확인"""
        ext = Path(file_path).suffix.lower()
        return ext in ALL_EXTENSIONS

    @staticmethod
    def get_files_in_folder(folder_path: str) -> List[str]:
        """폴더 내 지원되는 모든 미디어 파일 목록 반환"""
        files = []
        try:
            for entry in os.scandir(folder_path):
                if entry.is_file() and ImageLoader.is_supported_file(entry.path):
                    files.append(entry.path)
            files.sort(key=lambda x: x.lower())
        except PermissionError:
            pass
        return files

    @staticmethod
    def load_image(file_path: str, max_size: Optional[Tuple[int, int]] = None) -> Optional[QPixmap]:
        """이미지 파일을 QPixmap으로 로드

        Args:
            file_path: 이미지 파일 경로
            max_size: 최대 크기 (width, height) - 썸네일용

        Returns:
            QPixmap 또는 실패 시 None
        """
        try:
            with Image.open(file_path) as img:
                # EXIF 회전 정보 적용
                img = ImageLoader._apply_exif_rotation(img)

                # 리사이즈 (썸네일용)
                if max_size:
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)

                # RGBA로 변환 (투명도 지원)
                if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                    img = img.convert('RGBA')
                    qimage = ImageLoader._pil_to_qimage_rgba(img)
                else:
                    img = img.convert('RGB')
                    qimage = ImageLoader._pil_to_qimage_rgb(img)

                return QPixmap.fromImage(qimage)
        except Exception as e:
            print(f"이미지 로드 실패: {file_path} - {e}")
            return None

    @staticmethod
    def _apply_exif_rotation(img: Image.Image) -> Image.Image:
        """EXIF 회전 정보 적용"""
        try:
            exif = img.getexif()
            if exif:
                orientation_key = None
                for key, val in ExifTags.TAGS.items():
                    if val == 'Orientation':
                        orientation_key = key
                        break

                if orientation_key and orientation_key in exif:
                    orientation = exif[orientation_key]

                    if orientation == 2:
                        img = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
                    elif orientation == 3:
                        img = img.rotate(180)
                    elif orientation == 4:
                        img = img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
                    elif orientation == 5:
                        img = img.rotate(-90, expand=True).transpose(Image.Transpose.FLIP_LEFT_RIGHT)
                    elif orientation == 6:
                        img = img.rotate(-90, expand=True)
                    elif orientation == 7:
                        img = img.rotate(90, expand=True).transpose(Image.Transpose.FLIP_LEFT_RIGHT)
                    elif orientation == 8:
                        img = img.rotate(90, expand=True)
        except Exception:
            pass
        return img

    @staticmethod
    def _pil_to_qimage_rgb(img: Image.Image) -> QImage:
        """PIL RGB 이미지를 QImage로 변환"""
        data = img.tobytes('raw', 'RGB')
        return QImage(data, img.width, img.height, img.width * 3, QImage.Format.Format_RGB888)

    @staticmethod
    def _pil_to_qimage_rgba(img: Image.Image) -> QImage:
        """PIL RGBA 이미지를 QImage로 변환"""
        data = img.tobytes('raw', 'RGBA')
        return QImage(data, img.width, img.height, img.width * 4, QImage.Format.Format_RGBA8888)

    @staticmethod
    def get_image_info(file_path: str) -> dict:
        """이미지 파일 정보 반환"""
        info = {
            'filename': os.path.basename(file_path),
            'size_bytes': 0,
            'width': 0,
            'height': 0,
        }

        try:
            info['size_bytes'] = os.path.getsize(file_path)
            with Image.open(file_path) as img:
                # EXIF 회전 고려한 실제 표시 크기
                img = ImageLoader._apply_exif_rotation(img)
                info['width'] = img.width
                info['height'] = img.height
        except Exception:
            pass

        return info

    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """파일 크기를 읽기 쉬운 형태로 변환"""
        if size_bytes < 1024:
            return f"{size_bytes}B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f}KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f}MB"


class ThumbnailWorker(QRunnable):
    """비동기 썸네일 로딩 워커"""

    class Signals(QObject):
        finished = Signal(str, QPixmap)  # file_path, pixmap
        error = Signal(str, str)  # file_path, error_message

    def __init__(self, file_path: str, size: Tuple[int, int] = (80, 80)):
        super().__init__()
        self.file_path = file_path
        self.size = size
        self.signals = ThumbnailWorker.Signals()
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        if self._is_cancelled:
            return

        pixmap = ImageLoader.load_image(self.file_path, max_size=self.size)

        if self._is_cancelled:
            return

        if pixmap:
            self.signals.finished.emit(self.file_path, pixmap)
        else:
            self.signals.error.emit(self.file_path, "로드 실패")


class ThumbnailCache:
    """LRU 기반 썸네일 캐시"""

    def __init__(self, max_items: int = 500, max_memory_mb: int = 100):
        self._cache = {}  # {path: (pixmap, access_order)}
        self._access_order = 0
        self._max_items = max_items
        self._max_memory_bytes = max_memory_mb * 1024 * 1024
        self._current_memory = 0
        self._mutex = QMutex()

    def get(self, path: str) -> Optional[QPixmap]:
        with QMutexLocker(self._mutex):
            if path in self._cache:
                pixmap, _ = self._cache[path]
                self._access_order += 1
                self._cache[path] = (pixmap, self._access_order)
                return pixmap
            return None

    def put(self, path: str, pixmap: QPixmap):
        with QMutexLocker(self._mutex):
            # 이미 캐시에 있으면 업데이트
            if path in self._cache:
                old_pixmap, _ = self._cache[path]
                self._current_memory -= self._estimate_pixmap_memory(old_pixmap)

            # 캐시 정리
            self._evict_if_needed()

            # 새 항목 추가
            self._access_order += 1
            self._cache[path] = (pixmap, self._access_order)
            self._current_memory += self._estimate_pixmap_memory(pixmap)

    def _estimate_pixmap_memory(self, pixmap: QPixmap) -> int:
        """픽스맵 메모리 사용량 추정"""
        return pixmap.width() * pixmap.height() * 4  # RGBA 기준

    def _evict_if_needed(self):
        """캐시 정리 (LRU)"""
        while (len(self._cache) >= self._max_items or
               self._current_memory >= self._max_memory_bytes) and self._cache:
            # 가장 오래된 항목 찾기
            oldest_path = min(self._cache.keys(),
                            key=lambda k: self._cache[k][1])
            old_pixmap, _ = self._cache.pop(oldest_path)
            self._current_memory -= self._estimate_pixmap_memory(old_pixmap)

    def clear(self):
        with QMutexLocker(self._mutex):
            self._cache.clear()
            self._current_memory = 0
            self._access_order = 0
