@echo off
echo ========================================
echo Lightweight Viewer Debug Runner
echo ========================================
echo.

REM exe 파일 찾기
for %%f in (LightweightViewer*.exe) do (
    echo Running: %%f
    echo.
    "%%f"
    echo.
    echo ========================================
    echo Exit Code: %ERRORLEVEL%
    echo ========================================
)

echo.
pause
