@echo off
chcp 65001 >nul
echo ========================================
echo   Lightweight Viewer - Windows Build
echo ========================================
echo.

:: 현재 디렉토리를 스크립트 위치로 변경
cd /d "%~dp0"

:: Python 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo [오류] Python이 설치되어 있지 않습니다.
    echo https://www.python.org/downloads/ 에서 설치하세요.
    pause
    exit /b 1
)

:: 의존성 설치 (최초 1회)
echo [1/3] 의존성 확인 중...
pip show PySide6 >nul 2>&1
if errorlevel 1 (
    echo 의존성 설치 중... (최초 1회만 실행됩니다)
    pip install PySide6 Pillow pillow-heif pyinstaller
)

:: 빌드 실행
echo [2/3] 빌드 중... (1-2분 소요)
pyinstaller build.spec --clean --noconfirm

:: 결과 확인
if exist "dist\LightweightViewer.exe" (
    echo.
    echo ========================================
    echo   빌드 성공!
    echo ========================================
    echo 파일 위치: %cd%\dist\LightweightViewer.exe
    echo.
    echo [3/3] 앱을 실행합니다...
    start "" "dist\LightweightViewer.exe"
) else (
    echo.
    echo [오류] 빌드 실패
    echo 에러 로그를 확인하세요.
)

echo.
pause
