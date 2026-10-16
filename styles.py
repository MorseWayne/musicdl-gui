'''
Function:
    Modern Style Sheet for MusicdlGUI
Author:
    Zhenchao Jin
WeChat Official Account (微信公众号):
    Charles的皮卡丘
'''


def get_stylesheet(is_dark=False):
    """
    Generate modern stylesheet for the application
    
    Args:
        is_dark (bool): Whether to use dark theme
        
    Returns:
        str: CSS stylesheet string
    """
    if is_dark:
        bg_color = "#1e1e1e"
        secondary_bg = "#2d2d2d"
        text_color = "#e0e0e0"
        secondary_text = "#aaaaaa"
        border_color = "#3f3f3f"
        hover_bg = "#3d3d3d"
        item_hover_bg = "#353535"
        selection_bg = "#094771"
        table_header_bg = "#252525"
        input_bg = "#2d2d2d"
        primary_button_hover = "#1085e0"
        primary_button_pressed = "#006abc"
    else:
        bg_color = "#ffffff"
        secondary_bg = "#f5f5f5"
        text_color = "#333333"
        secondary_text = "#666666"
        border_color = "#e0e0e0"
        hover_bg = "#eeeeee"
        item_hover_bg = "#f5f5f5"
        selection_bg = "#eef7ff"
        table_header_bg = "#fafafa"
        input_bg = "#ffffff"
        primary_button_hover = "#1085e0"
        primary_button_pressed = "#006abc"

    return f"""
    /* Global Styles */
    QWidget {{
        background-color: {bg_color};
        color: {text_color};
        font-family: 'Segoe UI', 'Microsoft YaHei', 'PingFang SC', sans-serif;
        font-size: 14px;
    }}
    QLabel#appTitle {{
        font-size: 28px;
        font-weight: bold;
        color: #3299ed;
    }}
    QLabel#mutedLabel {{ color: {secondary_text}; font-size: 12px; }}
    QPlainTextEdit#errorLabel {{ color: {'#ff9c95' if is_dark else '#b42318'}; font-size: 12px; }}
    QScrollArea {{ border: none; }}

    /* GroupBox */
    QGroupBox {{
        font-weight: bold;
        border: 1px solid {border_color};
        border-radius: 10px;
        margin-top: 15px;
        padding-top: 10px;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        left: 15px;
        padding: 0 5px;
        color: {secondary_text};
    }}

    /* Buttons */
    QPushButton {{
        background-color: {secondary_bg};
        border: 1px solid {border_color};
        border-radius: 8px;
        padding: 7px 12px;
        min-height: 24px;
        color: {text_color};
    }}
    QPushButton:hover {{
        background-color: {hover_bg};
    }}
    QPushButton:pressed {{
        background-color: {border_color};
    }}
    QPushButton#primaryButton, QPushButton#button_keyword {{
        background-color: #0078d4;
        color: white;
        border: none;
        font-weight: bold;
        font-size: 15px;
    }}
    QPushButton#primaryButton:hover, QPushButton#button_keyword:hover {{
        background-color: {primary_button_hover};
    }}
    QPushButton#primaryButton:pressed, QPushButton#button_keyword:pressed {{
        background-color: {primary_button_pressed};
    }}
    QPushButton:disabled, QPushButton#primaryButton:disabled, QPushButton#button_keyword:disabled {{
        background-color: {secondary_bg};
        color: {secondary_text};
        border: 1px solid {border_color};
    }}

    /* LineEdit and TextEdit */
    QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox {{
        border: 1px solid {border_color};
        border-radius: 8px;
        padding: 10px;
        background-color: {input_bg};
        selection-background-color: #0078d4;
        color: {text_color};
    }}
    QLineEdit:focus, QTextEdit:focus {{
        border: 2px solid #0078d4;
        padding: 9px;
    }}

    /* Table */
    QTableWidget {{
        border: 1px solid {border_color};
        border-radius: 10px;
        gridline-color: {border_color};
        selection-background-color: {selection_bg};
        selection-color: #0078d4;
        outline: none;
        alternate-background-color: {secondary_bg};
    }}
    QTableWidget::item {{
        padding: 6px;
        border-bottom: 1px solid {border_color};
    }}
    QHeaderView::section {{
        background-color: {table_header_bg};
        color: {text_color};
        padding: 10px 18px 10px 8px;
        border: none;
        border-bottom: 2px solid {border_color};
        font-weight: bold;
        text-align: left;
        font-size: 14px;
    }}
    QHeaderView::section:hover {{
        background-color: {hover_bg};
        color: #0078d4;
    }}
    QHeaderView::section:pressed {{
        background-color: {border_color};
    }}
    /* Progress Bar */
    QProgressBar {{
        border: none;
        border-radius: 8px;
        text-align: center;
        background-color: {secondary_bg};
        height: 16px;
        font-weight: bold;
    }}
    QProgressBar::chunk {{
        background-color: #0078d4;
        border-radius: 8px;
    }}

    /* Tab Widget */
    QTabWidget::pane {{
        border: 1px solid {border_color};
        border-top: none;
        background-color: {bg_color};
        border-bottom-left-radius: 10px;
        border-bottom-right-radius: 10px;
    }}
    QTabBar::tab {{
        background-color: {secondary_bg};
        padding: 12px 25px;
        border: 1px solid {border_color};
        border-bottom: none;
        border-top-left-radius: 10px;
        border-top-right-radius: 10px;
        margin-right: 4px;
        color: {secondary_text};
    }}
    QTabBar::tab:selected {{
        background-color: {bg_color};
        border-bottom: 2px solid {bg_color};
        color: #0078d4;
        font-weight: bold;
    }}
    QTabBar::tab:!selected {{
        margin-top: 3px;
    }}

    /* CheckBox and RadioButton */
    QCheckBox, QRadioButton {{
        spacing: 10px;
        font-size: 14px;
    }}
    QCheckBox::indicator, QRadioButton::indicator {{
        width: 20px;
        height: 20px;
    }}
    QCheckBox::indicator:unchecked, QTableView::indicator:unchecked {{
        background-color: {input_bg};
        border: 1px solid {secondary_text};
        border-radius: 3px;
    }}

    /* ScrollBar */
    QScrollBar:vertical {{
        background: transparent;
        width: 10px;
        margin: 0px;
    }}
    QScrollBar::handle:vertical {{
        background: {border_color};
        min-height: 30px;
        border-radius: 5px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {secondary_text};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    """
