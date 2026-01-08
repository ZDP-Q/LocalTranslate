"""
GUI 样式定义
Catppuccin Mocha 主题
"""


class Colors:
    """颜色常量"""

    # Base colors
    BASE = "#1e1e2e"
    MANTLE = "#181825"
    CRUST = "#11111b"

    # Surface colors
    SURFACE0 = "#313244"
    SURFACE1 = "#45475a"
    SURFACE2 = "#585b70"

    # Overlay colors
    OVERLAY0 = "#6c7086"
    OVERLAY1 = "#7f849c"
    OVERLAY2 = "#9399b2"

    # Text colors
    TEXT = "#cdd6f4"
    SUBTEXT0 = "#a6adc8"
    SUBTEXT1 = "#bac2de"

    # Accent colors
    BLUE = "#89b4fa"
    LAVENDER = "#b4befe"
    SAPPHIRE = "#74c7ec"
    SKY = "#89dceb"
    TEAL = "#94e2d5"
    GREEN = "#a6e3a1"
    YELLOW = "#f9e2af"
    PEACH = "#fab387"
    MAROON = "#eba0ac"
    RED = "#f38ba8"
    MAUVE = "#cba6f7"
    PINK = "#f5c2e7"
    FLAMINGO = "#f2cdcd"
    ROSEWATER = "#f5e0dc"


DARK_STYLESHEET = f"""
QMainWindow {{
    background-color: {Colors.BASE};
}}

QWidget {{
    background-color: {Colors.BASE};
    color: {Colors.TEXT};
    font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
    font-size: 10pt;
}}

QGroupBox {{
    border: 1px solid {Colors.SURFACE1};
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 10px;
    font-weight: bold;
    background-color: {Colors.MANTLE};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 8px;
    color: {Colors.BLUE};
}}

QTextEdit {{
    background-color: {Colors.SURFACE0};
    border: 1px solid {Colors.SURFACE1};
    border-radius: 8px;
    padding: 12px;
    font-size: 11pt;
    selection-background-color: {Colors.BLUE};
    selection-color: {Colors.BASE};
}}

QTextEdit:focus {{
    border: 2px solid {Colors.BLUE};
}}

QComboBox {{
    background-color: {Colors.SURFACE0};
    border: 1px solid {Colors.SURFACE1};
    border-radius: 6px;
    padding: 8px 12px;
    min-width: 150px;
}}

QComboBox:hover {{
    border-color: {Colors.BLUE};
}}

QComboBox::drop-down {{
    border: none;
    width: 30px;
}}

QComboBox QAbstractItemView {{
    background-color: {Colors.SURFACE0};
    border: 1px solid {Colors.SURFACE1};
    border-radius: 6px;
    selection-background-color: {Colors.BLUE};
    selection-color: {Colors.BASE};
}}

QPushButton {{
    background-color: {Colors.BLUE};
    color: {Colors.BASE};
    border: none;
    border-radius: 6px;
    padding: 10px 24px;
    font-weight: bold;
    font-size: 10pt;
}}

QPushButton:hover {{
    background-color: {Colors.LAVENDER};
}}

QPushButton:pressed {{
    background-color: {Colors.SAPPHIRE};
}}

QPushButton:disabled {{
    background-color: {Colors.SURFACE1};
    color: {Colors.OVERLAY0};
}}

QPushButton#secondaryBtn {{
    background-color: {Colors.SURFACE1};
    color: {Colors.TEXT};
}}

QPushButton#secondaryBtn:hover {{
    background-color: {Colors.SURFACE2};
}}

QPushButton#successBtn {{
    background-color: {Colors.GREEN};
}}

QPushButton#dangerBtn {{
    background-color: {Colors.RED};
}}

QProgressBar {{
    background-color: {Colors.SURFACE0};
    border: none;
    border-radius: 4px;
    height: 8px;
    text-align: center;
}}

QProgressBar::chunk {{
    background-color: {Colors.GREEN};
    border-radius: 4px;
}}

QStatusBar {{
    background-color: {Colors.MANTLE};
    border-top: 1px solid {Colors.SURFACE1};
    color: {Colors.SUBTEXT0};
}}

QLabel#titleLabel {{
    font-size: 14pt;
    font-weight: bold;
    color: {Colors.BLUE};
}}

QLabel#subtitleLabel {{
    font-size: 9pt;
    color: {Colors.SUBTEXT0};
}}

QSpinBox, QLineEdit {{
    background-color: {Colors.SURFACE0};
    border: 1px solid {Colors.SURFACE1};
    border-radius: 6px;
    padding: 6px 10px;
}}

QSpinBox:focus, QLineEdit:focus {{
    border: 2px solid {Colors.BLUE};
}}

QCheckBox {{
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid {Colors.SURFACE1};
    background-color: {Colors.SURFACE0};
}}

QCheckBox::indicator:checked {{
    background-color: {Colors.BLUE};
    border-color: {Colors.BLUE};
}}

QTabWidget::pane {{
    border: 1px solid {Colors.SURFACE1};
    border-radius: 8px;
    background-color: {Colors.MANTLE};
}}

QTabBar::tab {{
    background-color: {Colors.SURFACE0};
    border: 1px solid {Colors.SURFACE1};
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 8px 16px;
    margin-right: 2px;
}}

QTabBar::tab:selected {{
    background-color: {Colors.MANTLE};
    border-bottom: 2px solid {Colors.BLUE};
}}

QTabBar::tab:hover:!selected {{
    background-color: {Colors.SURFACE1};
}}

QSplitter::handle {{
    background-color: {Colors.SURFACE1};
    height: 2px;
}}

QSplitter::handle:hover {{
    background-color: {Colors.BLUE};
}}

QScrollBar:vertical {{
    background-color: {Colors.SURFACE0};
    width: 12px;
    border-radius: 6px;
}}

QScrollBar::handle:vertical {{
    background-color: {Colors.SURFACE2};
    border-radius: 6px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {Colors.OVERLAY0};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
"""


LIGHT_STYLESHEET = """
/* TODO: 实现亮色主题 */
"""


def get_stylesheet(theme: str = "dark") -> str:
    """获取样式表"""
    if theme == "light":
        return LIGHT_STYLESHEET
    return DARK_STYLESHEET
