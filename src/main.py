"""
Lightweight Photo Viewer - 초경량 로컬 사진 뷰어
백그라운드 상주 없이 1초 안에 사진을 보여주는 가장 가벼운 뷰어
"""
import sys
import os

# PyInstaller 실행 시 경로 설정
if getattr(sys, 'frozen', False):
    # PyInstaller로 빌드된 exe 실행 시
    BASE_DIR = sys._MEIPASS
else:
    # 개발 환경에서 실행 시
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# src 디렉토리를 모듈 검색 경로에 추가
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# 빠른 시작을 위한 환경 변수 설정
os.environ['QT_ENABLE_HIGHDPI_SCALING'] = '1'

try:
    from PySide6.QtWidgets import QApplication, QMessageBox
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QIcon

    from viewer.main_window import MainWindow
    from utils.theme import ThemeManager
except ImportError as e:
    # 오류 발생 시 메시지 박스로 표시
    from PySide6.QtWidgets import QApplication, QMessageBox
    app = QApplication(sys.argv)
    QMessageBox.critical(None, "Import Error", f"모듈 로드 실패:\n{e}\n\nPath: {sys.path}")
    sys.exit(1)


def main():
    print(f"[DEBUG] Starting Lightweight Viewer...")
    print(f"[DEBUG] Python: {sys.version}")
    print(f"[DEBUG] BASE_DIR: {BASE_DIR}")
    print(f"[DEBUG] sys.path: {sys.path[:3]}...")

    try:
        # High DPI 설정
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )

        app = QApplication(sys.argv)
        app.setApplicationName("Lightweight Viewer")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("LightweightViewer")

        print("[DEBUG] QApplication created")

        # 테마 적용
        theme_manager = ThemeManager()
        theme_manager.apply_theme(app)

        print("[DEBUG] Theme applied")

        # 메인 윈도우 생성
        window = MainWindow()

        print("[DEBUG] MainWindow created")

        # 명령줄 인자로 파일이 전달되면 열기
        if len(sys.argv) > 1:
            file_path = sys.argv[1]
            if os.path.isfile(file_path):
                window.open_file(file_path)

        window.show()
        print("[DEBUG] Window shown, entering event loop...")

        sys.exit(app.exec())
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
        sys.exit(1)


if __name__ == '__main__':
    main()
