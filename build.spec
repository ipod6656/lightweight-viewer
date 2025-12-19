# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller 빌드 설정 (최적화 버전)
사용법: pyinstaller build.spec
목표: 100MB 이하
"""

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# pillow-heif 데이터 파일 수집
heif_datas = []
try:
    heif_datas = collect_data_files('pillow_heif')
except Exception:
    pass

# PySide6 데이터 파일 수집 (필수 플러그인만)
# 전체 수집 대신 필요한 것만 선별적으로 포함
pyside6_datas = []

a = Analysis(
    ['src/main.py'],
    pathex=['src'],
    binaries=[],
    datas=heif_datas + [
        ('src/viewer', 'viewer'),
        ('src/utils', 'utils'),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'PIL',
        'PIL.Image',
        'pillow_heif',
        'viewer',
        'viewer.main_window',
        'viewer.image_viewer',
        'viewer.thumbnail_strip',
        'utils',
        'utils.image_loader',
        'utils.compressor',
        'utils.theme',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # ===== Python 표준 라이브러리 (불필요) =====
        'tkinter', '_tkinter',
        'unittest', 'test',
        'email', 'html', 'http', 'xml', 'xmlrpc',
        'pydoc', 'doctest', 'difflib',
        'calendar', 'pdb', 'profile', 'cProfile',
        'distutils', 'setuptools', 'pkg_resources', 'pip',
        'ensurepip', 'venv', 'lib2to3',
        'asyncio', 'concurrent', 'multiprocessing',
        'ctypes.test', 'sqlite3', 'bz2', 'lzma',
        'ftplib', 'imaplib', 'nntplib', 'poplib', 'smtplib', 'telnetlib',
        'ssl', 'hashlib', 'hmac', 'secrets',
        'curses', 'tty', 'pty', 'termios',

        # ===== 데이터 과학 라이브러리 =====
        'numpy', 'scipy', 'matplotlib', 'pandas', 'pytest',
        'sklearn', 'tensorflow', 'torch', 'cv2',

        # ===== PySide6 불필요 모듈 (대폭 확대) =====
        # 네트워크/웹
        'PySide6.QtNetwork', 'PySide6.QtNetworkAuth',
        'PySide6.QtWebChannel', 'PySide6.QtWebEngineCore',
        'PySide6.QtWebEngineQuick', 'PySide6.QtWebEngineWidgets',
        'PySide6.QtWebSockets', 'PySide6.QtHttpServer',

        # QML/Quick
        'PySide6.QtQml', 'PySide6.QtQuick', 'PySide6.QtQuickWidgets',
        'PySide6.QtQuickControls2', 'PySide6.QtQuick3D',

        # 데이터베이스/SQL
        'PySide6.QtSql',

        # 3D
        'PySide6.Qt3DCore', 'PySide6.Qt3DRender', 'PySide6.Qt3DInput',
        'PySide6.Qt3DLogic', 'PySide6.Qt3DAnimation', 'PySide6.Qt3DExtras',

        # 멀티미디어 (이미지 뷰어에 불필요)
        'PySide6.QtMultimedia', 'PySide6.QtMultimediaWidgets',
        'PySide6.QtSpatialAudio',

        # 기타 불필요 모듈
        'PySide6.QtBluetooth', 'PySide6.QtNfc',
        'PySide6.QtCharts', 'PySide6.QtDataVisualization',
        'PySide6.QtDesigner', 'PySide6.QtHelp', 'PySide6.QtUiTools',
        'PySide6.QtLocation', 'PySide6.QtPositioning',
        'PySide6.QtPrintSupport',
        'PySide6.QtRemoteObjects', 'PySide6.QtScxml',
        'PySide6.QtSensors', 'PySide6.QtSerialPort', 'PySide6.QtSerialBus',
        'PySide6.QtStateMachine',
        'PySide6.QtSvg', 'PySide6.QtSvgWidgets',
        'PySide6.QtTest', 'PySide6.QtXml',
        'PySide6.QtTextToSpeech',
        'PySide6.QtPdf', 'PySide6.QtPdfWidgets',
        'PySide6.QtOpenGL', 'PySide6.QtOpenGLWidgets',
        'PySide6.QtDBus', 'PySide6.QtVirtualKeyboard',

        # shiboken 디버그/불필요
        'shiboken6.Shiboken',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# ===== 바이너리 필터링 (Qt 플러그인 최적화) =====
# 불필요한 Qt 플러그인 제거
exclude_binaries = [
    'qsqlite', 'qsqlodbc', 'qsqlpsql',  # SQL 드라이버
    'qgif', 'qicns', 'qico', 'qtga', 'qtiff', 'qwbmp',  # 일부 이미지 포맷 (필요시 유지)
    'qtvirtualkeyboard', 'qtuiotouchplugin',  # 가상 키보드
    'qtwebengine',  # 웹엔진
    'qt3d', 'qtquick', 'qml',  # 3D/QML
    'designer',  # 디자이너
    'multimedia', 'audio',  # 멀티미디어
    'texttospeech',  # TTS
    'pdf', 'printsupport',  # PDF/프린트
]

filtered_binaries = []
for binary in a.binaries:
    name = binary[0].lower()
    should_exclude = False
    for pattern in exclude_binaries:
        if pattern in name:
            should_exclude = True
            break
    if not should_exclude:
        filtered_binaries.append(binary)

a.binaries = filtered_binaries

# ===== 데이터 필터링 (translations/locales 제거) =====
exclude_datas = [
    'translations', 'qtwebengine', 'resources',
    'qml', 'Qt/qml', 'PySide6/qml',
]

filtered_datas = []
for data in a.datas:
    name = data[0].lower()
    should_exclude = False
    for pattern in exclude_datas:
        if pattern in name:
            should_exclude = True
            break
    if not should_exclude:
        filtered_datas.append(data)

a.datas = filtered_datas

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='LightweightViewer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,  # 심볼 제거 (용량 감소)
    upx=True,  # UPX 압축 활성화
    upx_exclude=['Qt*.dll', 'PySide6*.pyd'],  # Qt DLL은 UPX 제외 (안정성)
    runtime_tmpdir=None,
    console=False,  # 콘솔 창 숨김 (릴리스 모드)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
    version=None,
)
