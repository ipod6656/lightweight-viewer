"""
Lightweight Photo Viewer - 초경량 로컬 사진 뷰어
백그라운드 상주 없이 1초 안에 사진을 보여주는 가장 가벼운 뷰어
"""
import sys
import os

print("=" * 50)
print("Lightweight Viewer 시작")
print("=" * 50)

# PyInstaller 실행 시 경로 설정
if getattr(sys, 'frozen', False):
    # PyInstaller로 빌드된 exe 실행 시
    BASE_DIR = sys._MEIPASS
    print(f"[INFO] PyInstaller 모드")
else:
    # 개발 환경에서 실행 시
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    print(f"[INFO] 개발 모드")

print(f"[INFO] BASE_DIR: {BASE_DIR}")
print(f"[INFO] sys.path[0]: {sys.path[0] if sys.path else 'empty'}")

# src 디렉토리를 모듈 검색 경로에 추가
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
    print(f"[INFO] Added to sys.path: {BASE_DIR}")

# 빠른 시작을 위한 환경 변수 설정
os.environ['QT_ENABLE_HIGHDPI_SCALING'] = '1'

print("[INFO] PySide6 import 시도...")
try:
    from PySide6.QtWidgets import QApplication, QMessageBox
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QIcon
    print("[OK] PySide6 import 성공")
except Exception as e:
    print(f"[ERROR] PySide6 import 실패: {e}")
    input("Enter 키를 눌러 종료...")
    sys.exit(1)

print("[INFO] viewer/utils 모듈 import 시도...")
try:
    from viewer.main_window import MainWindow
    from utils.theme import ThemeManager
    print("[OK] 모듈 import 성공")
except ImportError as e:
    print(f"[ERROR] 모듈 import 실패: {e}")
    print(f"[DEBUG] sys.path: {sys.path}")
    print(f"[DEBUG] BASE_DIR 내용:")
    try:
        for item in os.listdir(BASE_DIR):
            print(f"  - {item}")
    except Exception as e2:
        print(f"  디렉토리 읽기 실패: {e2}")
    input("Enter 키를 눌러 종료...")
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
    try:
        main()
    except Exception as e:
        print(f"[FATAL ERROR] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        input("Enter 키를 눌러 종료...")
        sys.exit(1)
