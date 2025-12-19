"""
Lightweight Photo Viewer - 초경량 로컬 사진 뷰어
백그라운드 상주 없이 1초 안에 사진을 보여주는 가장 가벼운 뷰어
"""
import sys
import os

# 빠른 시작을 위한 환경 변수 설정
os.environ['QT_ENABLE_HIGHDPI_SCALING'] = '1'

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from viewer.main_window import MainWindow
from utils.theme import ThemeManager


def main():
    # High DPI 설정
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("Lightweight Viewer")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("LightweightViewer")

    # 테마 적용
    theme_manager = ThemeManager()
    theme_manager.apply_theme(app)

    # 메인 윈도우 생성
    window = MainWindow()

    # 명령줄 인자로 파일이 전달되면 열기
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if os.path.isfile(file_path):
            window.open_file(file_path)

    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
