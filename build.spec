# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller 빌드 설정
사용법: pyinstaller build.spec
"""

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# PySide6 데이터 파일 수집 (Qt 플러그인 포함)
pyside6_datas = []
try:
    pyside6_datas = collect_data_files('PySide6', include_py_files=False)
except Exception as e:
    print(f"Warning: Could not collect PySide6 data files: {e}")

# pillow-heif 데이터 파일 수집
heif_datas = []
try:
    heif_datas = collect_data_files('pillow_heif')
except Exception:
    pass

a = Analysis(
    ['src/main.py'],
    pathex=['src'],  # src 디렉토리를 모듈 검색 경로에 추가
    binaries=[],
    datas=pyside6_datas + heif_datas + [
        ('src/viewer', 'viewer'),  # viewer 패키지 포함
        ('src/utils', 'utils'),    # utils 패키지 포함
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'PIL',
        'PIL.Image',
        'pillow_heif',
        # 앱 내부 모듈
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
        # 불필요한 모듈 제외 (용량 최적화)
        'tkinter',
        'unittest',
        'email',
        'html',
        'http',
        'xml',
        'pydoc',
        'doctest',
        # 'argparse',  # PySide6/shibokensupport에서 필요함 - 제외하지 않음
        'difflib',
        # 'inspect',  # PySide6/shiboken에서 필요함 - 제외하지 않음
        'calendar',
        'distutils',
        'setuptools',
        'pkg_resources',
        'numpy',
        'scipy',
        'matplotlib',
        'pandas',
        'pytest',
        # PySide6 불필요 모듈
        'PySide6.QtNetwork',
        'PySide6.QtQml',
        'PySide6.QtQuick',
        'PySide6.QtSql',
        'PySide6.QtTest',
        'PySide6.QtXml',
        'PySide6.Qt3DCore',
        'PySide6.Qt3DRender',
        'PySide6.Qt3DInput',
        'PySide6.Qt3DLogic',
        'PySide6.Qt3DAnimation',
        'PySide6.Qt3DExtras',
        'PySide6.QtBluetooth',
        'PySide6.QtCharts',
        'PySide6.QtDataVisualization',
        'PySide6.QtDesigner',
        'PySide6.QtHelp',
        'PySide6.QtLocation',
        'PySide6.QtMultimediaWidgets',
        'PySide6.QtNetworkAuth',
        'PySide6.QtNfc',
        'PySide6.QtPositioning',
        'PySide6.QtPrintSupport',
        'PySide6.QtRemoteObjects',
        'PySide6.QtScxml',
        'PySide6.QtSensors',
        'PySide6.QtSerialPort',
        'PySide6.QtStateMachine',
        'PySide6.QtSvg',
        'PySide6.QtSvgWidgets',
        'PySide6.QtTextToSpeech',
        'PySide6.QtUiTools',
        'PySide6.QtWebChannel',
        'PySide6.QtWebEngineCore',
        'PySide6.QtWebEngineQuick',
        'PySide6.QtWebEngineWidgets',
        'PySide6.QtWebSockets',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

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
    strip=False,
    upx=True,  # UPX 압축 활성화 (용량 감소)
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # 디버깅용 콘솔 활성화 (문제 해결 후 False로 변경)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Windows 설정
    icon=None,  # 아이콘 파일이 있으면 'resources/icon.ico'
    version=None,  # 버전 정보 파일
)
