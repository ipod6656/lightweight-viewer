"""
테마 관리자 - Windows 다크/라이트 모드 감지 및 적용
"""
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt


class ThemeManager:
    """Windows 시스템 테마 감지 및 앱 테마 적용"""

    # 다크 테마 색상
    DARK_COLORS = {
        'window': '#1e1e1e',
        'window_text': '#ffffff',
        'base': '#2d2d2d',
        'alternate_base': '#353535',
        'text': '#ffffff',
        'button': '#3d3d3d',
        'button_text': '#ffffff',
        'highlight': '#0078d4',
        'highlight_text': '#ffffff',
        'link': '#4fc3f7',
        'border': '#555555',
    }

    # 라이트 테마 색상
    LIGHT_COLORS = {
        'window': '#f3f3f3',
        'window_text': '#1e1e1e',
        'base': '#ffffff',
        'alternate_base': '#f5f5f5',
        'text': '#1e1e1e',
        'button': '#e1e1e1',
        'button_text': '#1e1e1e',
        'highlight': '#0078d4',
        'highlight_text': '#ffffff',
        'link': '#0066cc',
        'border': '#cccccc',
    }

    def __init__(self):
        self._is_dark = self._detect_system_theme()

    def _detect_system_theme(self) -> bool:
        """Windows 시스템 테마 감지 (다크모드 여부)"""
        if sys.platform == 'win32':
            try:
                import winreg
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
                )
                value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                winreg.CloseKey(key)
                return value == 0  # 0 = 다크모드
            except Exception:
                pass
        # 기본값: 다크 모드
        return True

    @property
    def is_dark_mode(self) -> bool:
        return self._is_dark

    def get_colors(self) -> dict:
        """현재 테마의 색상 딕셔너리 반환"""
        return self.DARK_COLORS if self._is_dark else self.LIGHT_COLORS

    def apply_theme(self, app: QApplication):
        """앱에 테마 적용"""
        colors = self.get_colors()

        palette = QPalette()

        palette.setColor(QPalette.ColorRole.Window, QColor(colors['window']))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(colors['window_text']))
        palette.setColor(QPalette.ColorRole.Base, QColor(colors['base']))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(colors['alternate_base']))
        palette.setColor(QPalette.ColorRole.Text, QColor(colors['text']))
        palette.setColor(QPalette.ColorRole.Button, QColor(colors['button']))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(colors['button_text']))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(colors['highlight']))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(colors['highlight_text']))
        palette.setColor(QPalette.ColorRole.Link, QColor(colors['link']))

        # 비활성화 색상
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText,
                        QColor('#808080'))
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text,
                        QColor('#808080'))
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText,
                        QColor('#808080'))

        app.setPalette(palette)

        # 스타일시트 적용
        app.setStyleSheet(self._get_stylesheet(colors))

    def _get_stylesheet(self, colors: dict) -> str:
        """테마에 맞는 스타일시트 반환"""
        return f"""
            QMainWindow {{
                background-color: {colors['window']};
            }}

            QScrollBar:horizontal {{
                background: {colors['base']};
                height: 12px;
                border: none;
            }}

            QScrollBar::handle:horizontal {{
                background: {colors['button']};
                min-width: 30px;
                border-radius: 6px;
            }}

            QScrollBar::handle:horizontal:hover {{
                background: {colors['highlight']};
            }}

            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}

            QScrollBar:vertical {{
                background: {colors['base']};
                width: 12px;
                border: none;
            }}

            QScrollBar::handle:vertical {{
                background: {colors['button']};
                min-height: 30px;
                border-radius: 6px;
            }}

            QScrollBar::handle:vertical:hover {{
                background: {colors['highlight']};
            }}

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}

            QMenu {{
                background-color: {colors['base']};
                border: 1px solid {colors['border']};
                padding: 4px;
            }}

            QMenu::item {{
                padding: 6px 24px;
                background-color: transparent;
            }}

            QMenu::item:selected {{
                background-color: {colors['highlight']};
                color: {colors['highlight_text']};
            }}

            QMenu::separator {{
                height: 1px;
                background-color: {colors['border']};
                margin: 4px 8px;
            }}

            QToolTip {{
                background-color: {colors['base']};
                color: {colors['text']};
                border: 1px solid {colors['border']};
                padding: 4px;
            }}

            QDialog {{
                background-color: {colors['window']};
            }}

            QPushButton {{
                background-color: {colors['button']};
                color: {colors['button_text']};
                border: 1px solid {colors['border']};
                padding: 6px 16px;
                border-radius: 4px;
            }}

            QPushButton:hover {{
                background-color: {colors['highlight']};
                color: {colors['highlight_text']};
            }}

            QPushButton:pressed {{
                background-color: {colors['highlight']};
            }}

            QSlider::groove:horizontal {{
                background: {colors['base']};
                height: 6px;
                border-radius: 3px;
            }}

            QSlider::handle:horizontal {{
                background: {colors['highlight']};
                width: 14px;
                height: 14px;
                margin: -4px 0;
                border-radius: 7px;
            }}

            QComboBox {{
                background-color: {colors['button']};
                color: {colors['button_text']};
                border: 1px solid {colors['border']};
                padding: 4px 8px;
                border-radius: 4px;
            }}

            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}

            QComboBox QAbstractItemView {{
                background-color: {colors['base']};
                color: {colors['text']};
                selection-background-color: {colors['highlight']};
            }}
        """

    def get_viewer_background(self) -> str:
        """이미지 뷰어 배경색 반환"""
        return '#000000' if self._is_dark else '#1a1a1a'
