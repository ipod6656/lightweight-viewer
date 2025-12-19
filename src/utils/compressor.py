"""
이미지 압축 유틸리티
"""
import os
from pathlib import Path
from typing import Optional, Tuple
from dataclasses import dataclass

from PIL import Image

from .image_loader import ImageLoader


@dataclass
class CompressionResult:
    """압축 결과"""
    success: bool
    original_path: str
    output_path: str
    original_size: int
    compressed_size: int
    error_message: str = ""

    @property
    def size_reduction(self) -> float:
        """압축률 (0-100%)"""
        if self.original_size == 0:
            return 0
        return (1 - self.compressed_size / self.original_size) * 100

    @property
    def original_size_str(self) -> str:
        return ImageLoader.format_file_size(self.original_size)

    @property
    def compressed_size_str(self) -> str:
        return ImageLoader.format_file_size(self.compressed_size)


class ImageCompressor:
    """이미지 압축 클래스"""

    # 품질 프리셋
    QUALITY_PRESETS = {
        'high': 90,      # 고품질
        'medium': 80,    # 중간
        'low': 70,       # 저품질 (작은 파일)
    }

    # 해상도 프리셋 (최대 너비 기준, 비율 유지)
    RESOLUTION_PRESETS = {
        'original': None,    # 원본 유지
        '4k': 3840,
        '2k': 2560,
        'fhd': 1920,         # Full HD
        'hd': 1280,          # HD
    }

    @staticmethod
    def compress(
        input_path: str,
        quality: int = 80,
        max_width: Optional[int] = None,
        output_format: str = 'JPEG',
        output_suffix: str = '_compressed'
    ) -> CompressionResult:
        """이미지 압축

        Args:
            input_path: 입력 파일 경로
            quality: JPEG 품질 (1-100)
            max_width: 최대 너비 (None이면 원본 유지)
            output_format: 출력 포맷 (JPEG, PNG, WEBP)
            output_suffix: 출력 파일 접미사

        Returns:
            CompressionResult 객체
        """
        original_size = 0

        try:
            original_size = os.path.getsize(input_path)

            # 출력 경로 생성
            input_path_obj = Path(input_path)
            ext_map = {'JPEG': '.jpg', 'PNG': '.png', 'WEBP': '.webp'}
            output_ext = ext_map.get(output_format, '.jpg')
            output_path = str(
                input_path_obj.parent /
                f"{input_path_obj.stem}{output_suffix}{output_ext}"
            )

            # 이미지 로드
            with Image.open(input_path) as img:
                # EXIF 회전 적용
                img = ImageLoader._apply_exif_rotation(img)

                # 리사이즈
                if max_width and img.width > max_width:
                    ratio = max_width / img.width
                    new_height = int(img.height * ratio)
                    img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

                # RGB로 변환 (JPEG는 RGBA 미지원)
                if output_format == 'JPEG' and img.mode in ('RGBA', 'P'):
                    # 투명 배경을 흰색으로
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[3] if len(img.split()) == 4 else None)
                    img = background
                elif img.mode not in ('RGB', 'RGBA'):
                    img = img.convert('RGB')

                # 저장 옵션
                save_kwargs = {'quality': quality, 'optimize': True}

                if output_format == 'JPEG':
                    save_kwargs['progressive'] = True
                elif output_format == 'WEBP':
                    save_kwargs['method'] = 4  # 압축 품질 (0-6)
                elif output_format == 'PNG':
                    save_kwargs = {'optimize': True, 'compress_level': 9}

                # 저장
                img.save(output_path, output_format, **save_kwargs)

            compressed_size = os.path.getsize(output_path)

            return CompressionResult(
                success=True,
                original_path=input_path,
                output_path=output_path,
                original_size=original_size,
                compressed_size=compressed_size
            )

        except Exception as e:
            return CompressionResult(
                success=False,
                original_path=input_path,
                output_path="",
                original_size=original_size,
                compressed_size=0,
                error_message=str(e)
            )

    @staticmethod
    def convert_heic_to_jpeg(
        input_path: str,
        quality: int = 90,
        output_suffix: str = ''
    ) -> CompressionResult:
        """HEIC를 JPEG로 변환

        Args:
            input_path: HEIC 파일 경로
            quality: JPEG 품질
            output_suffix: 출력 파일 접미사 (기본: 빈 문자열 = 확장자만 변경)
        """
        input_path_obj = Path(input_path)

        if output_suffix:
            output_path = str(input_path_obj.parent / f"{input_path_obj.stem}{output_suffix}.jpg")
        else:
            output_path = str(input_path_obj.parent / f"{input_path_obj.stem}.jpg")

        return ImageCompressor.compress(
            input_path=input_path,
            quality=quality,
            output_format='JPEG',
            output_suffix=output_suffix if output_suffix else ''
        )

    @staticmethod
    def estimate_compressed_size(
        input_path: str,
        quality: int = 80,
        max_width: Optional[int] = None
    ) -> int:
        """압축 후 예상 파일 크기 추정 (대략적)"""
        try:
            original_size = os.path.getsize(input_path)

            # 품질에 따른 대략적인 압축률
            quality_factor = quality / 100

            # 리사이즈 비율
            resize_factor = 1.0
            if max_width:
                with Image.open(input_path) as img:
                    if img.width > max_width:
                        resize_factor = (max_width / img.width) ** 2  # 면적 비율

            # 추정 크기 (실제와 다를 수 있음)
            estimated = int(original_size * quality_factor * 0.5 * resize_factor)
            return max(estimated, 1024)  # 최소 1KB

        except Exception:
            return 0
