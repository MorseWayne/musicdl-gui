'''
Function:
    Implementation of MusicdlGUI
Author:
    Zhenchao Jin
WeChat Official Account (微信公众号):
    Charles的皮卡丘
'''
import os
import sys
import json
import requests
from PyQt5 import *
from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from musicdl import musicdl
from PyQt5.QtWidgets import *
from musicdl.modules.utils.misc import touchdir, sanitize_filepath


'''Modern Style Sheet'''
def get_stylesheet(is_dark=False):
    # SVG Icons for sort arrows
    if is_dark:
        arrow_color = "white"
        active_arrow_color = "#0078d4"
    else:
        arrow_color = "#666666"
        active_arrow_color = "#0078d4"
    
    # Simple SVG arrows as base64
    up_arrow = f"url('data:image/svg+xml;utf8,<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"12\" height=\"12\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"{arrow_color}\" stroke-width=\"3\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M18 15l-6-6-6 6\"/></svg>')"
    down_arrow = f"url('data:image/svg+xml;utf8,<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"12\" height=\"12\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"{arrow_color}\" stroke-width=\"3\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M6 9l6 6 6-6\"/></svg>')"
    
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

    /* GroupBox */
    QGroupBox {{
        font-weight: bold;
        border: 1px solid {border_color};
        border-radius: 10px;
        margin-top: 15px;
        padding-top: 20px;
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
        padding: 8px 20px;
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

    /* LineEdit and TextEdit */
    QLineEdit, QTextEdit {{
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
        padding: 12px;
        border-bottom: 1px solid {border_color};
    }}
    QHeaderView::section {{
        background-color: {table_header_bg};
        color: {text_color};
        padding: 12px 30px 12px 15px; /* Added more right padding for arrow */
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
    /* Style sort indicators */
    QHeaderView::up-arrow {{
        image: {up_arrow};
        subcontrol-origin: padding;
        subcontrol-position: center right;
        width: 12px;
        height: 12px;
        right: 10px;
    }}
    QHeaderView::down-arrow {{
        image: {down_arrow};
        subcontrol-origin: padding;
        subcontrol-position: center right;
        width: 12px;
        height: 12px;
        right: 10px;
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


'''Sortable Table Items'''
class SortableTableWidgetItem(QTableWidgetItem):
    def __init__(self, text, sort_value=None):
        super().__init__(text)
        self.sort_value = sort_value if sort_value is not None else text

    def __lt__(self, other):
        if isinstance(other, SortableTableWidgetItem):
            try:
                return self.sort_value < other.sort_value
            except TypeError:
                return super().__lt__(other)
        return super().__lt__(other)


'''Search Worker Thread'''
class SearchWorker(QThread):
    finished_sig = pyqtSignal(str, list) # source_name, results_list
    error_sig = pyqtSignal(str, str) # source_name, error_msg

    def __init__(self, music_sources, keyword, settings):
        super().__init__()
        self.music_sources = music_sources
        self.keyword = keyword
        self.settings = settings

    def run(self):
        try:
            # Build config for this specific source
            init_music_clients_cfg = {}
            for source in self.music_sources:
                cookie_data = self.settings.get('cookies', {}).get(source, {})
                init_music_clients_cfg[source] = {
                    'work_dir': self.settings.get('work_dir', 'musicdl_outputs'),
                    'default_search_cookies': cookie_data.get('search', '').strip(),
                    'default_download_cookies': cookie_data.get('download', '').strip() or cookie_data.get('search', '').strip(),
                    'max_retries': 1,
                    'search_size_per_source': 5,
                    'search_size_per_page': 5,
                }
            
            # Handle Quark sites
            quark_cookie = self.settings.get('quark_cookies', '').strip()
            if quark_cookie:
                quark_sites = ['MituMusicClient', 'GequbaoMusicClient', 'YinyuedaoMusicClient', 'BuguyyMusicClient', 
                               'JCPOOMusicClient', 'GequhaiMusicClient', 'LivePOOMusicClient', 'KKWSMusicClient', 'FLMP3MusicClient']
                for site in quark_sites:
                    if site in self.music_sources:
                        init_music_clients_cfg[site]['quark_parser_config'] = {'cookies': quark_cookie}

            client = musicdl.MusicClient(
                music_sources=self.music_sources, 
                init_music_clients_cfg=init_music_clients_cfg,
                requests_overrides={s: {'timeout': (4, 8)} for s in self.music_sources},
                clients_threadings={s: 3 for s in self.music_sources}
            )
            
            results = client.search(keyword=self.keyword)
            
            for source_name, source_results in results.items():
                self.finished_sig.emit(source_name, source_results)
            
            # If some sources didn't return any results (even empty list), they might have failed
            for source in self.music_sources:
                if source not in results:
                    self.error_sig.emit(source, "No response")
                    
        except Exception as e:
            for source in self.music_sources:
                self.error_sig.emit(source, str(e))


'''Download Worker Thread'''
class DownloadWorker(QThread):
    progress_sig = pyqtSignal(int, str) # percentage, detailed_text
    finished_sig = pyqtSignal(bool, str, str) # success, msg, file_path

    def __init__(self, song_info, download_dir, filename, music_client):
        super().__init__()
        self.song_info = song_info
        self.download_dir = download_dir
        self.filename = filename
        self.music_client = music_client

    def run(self):
        try:
            download_music_file_path = sanitize_filepath(os.path.join(self.download_dir, self.filename))
            
            # Handle duplicate filenames
            if os.path.exists(download_music_file_path):
                base_name = os.path.splitext(self.filename)[0]
                ext = self.song_info['ext']
                counter = 1
                while os.path.exists(download_music_file_path):
                    self.filename = f"{base_name} ({counter}).{ext}"
                    download_music_file_path = sanitize_filepath(os.path.join(self.download_dir, self.filename))
                    counter += 1

            headers = self.music_client.music_clients[self.song_info['source']].default_download_headers
            with requests.get(self.song_info['download_url'], headers=headers, stream=True, verify=False, timeout=60) as resp:
                if resp.status_code == 200:
                    total_size = int(resp.headers.get('content-length', 0))
                    chunk_size = 1024 * 16 # 16KB chunks
                    download_size = 0
                    
                    with open(download_music_file_path, 'wb') as fp:
                        for chunk in resp.iter_content(chunk_size=chunk_size):
                            if not chunk: continue
                            fp.write(chunk)
                            download_size += len(chunk)
                            
                            if total_size > 0:
                                percent = int(download_size / total_size * 100)
                                detail = f"{download_size/1024/1024:.1f}MB / {total_size/1024/1024:.1f}MB"
                                self.progress_sig.emit(percent, detail)
                            else:
                                detail = f"{download_size/1024/1024:.1f}MB / Unknown"
                                self.progress_sig.emit(0, detail)
                    
                    self.finished_sig.emit(True, f"Finished downloading {self.song_info['song_name']}", download_music_file_path)
                else:
                    self.finished_sig.emit(False, f"Download failed with status code: {resp.status_code}", "")
        except Exception as e:
            self.finished_sig.emit(False, f"Download error: {str(e)}", "")


'''SettingsDialog'''
class SettingsDialog(QDialog):
    def __init__(self, parent=None, current_settings=None):
        super(SettingsDialog, self).__init__(parent)
        self.setWindowTitle('Settings - 设置')
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        self.current_settings = current_settings or {}
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Appearance section
        appearance_group = QGroupBox('Appearance - 外观设置')
        appearance_layout = QVBoxLayout()
        appearance_layout.setContentsMargins(15, 20, 15, 15)
        
        self.theme_group = QButtonGroup()
        self.light_theme_radio = QRadioButton('Light Mode - 浅色模式')
        self.dark_theme_radio = QRadioButton('Dark Mode - 深色模式')
        self.theme_group.addButton(self.light_theme_radio, 0)
        self.theme_group.addButton(self.dark_theme_radio, 1)
        
        is_dark = self.current_settings.get('is_dark', False)
        if is_dark:
            self.dark_theme_radio.setChecked(True)
        else:
            self.light_theme_radio.setChecked(True)
            
        appearance_layout.addWidget(self.light_theme_radio)
        appearance_layout.addWidget(self.dark_theme_radio)
        appearance_group.setLayout(appearance_layout)
        main_layout.addWidget(appearance_group)
        
        # Download directory section
        dir_group = QGroupBox('Download Directory - 下载目录')
        dir_layout = QVBoxLayout()
        dir_layout.setContentsMargins(15, 20, 15, 15)
        dir_layout.setSpacing(10)
        
        # Directory path
        path_layout = QHBoxLayout()
        path_layout.setSpacing(10)
        self.dir_edit = QLineEdit(self.current_settings.get('work_dir', 'musicdl_outputs'))
        self.dir_button = QPushButton('Browse - 浏览')
        self.dir_button.setMinimumWidth(100)
        self.dir_button.setCursor(Qt.PointingHandCursor)
        self.dir_button.clicked.connect(self.select_directory)
        path_layout.addWidget(QLabel('Directory - 目录:'))
        path_layout.addWidget(self.dir_edit)
        path_layout.addWidget(self.dir_button)
        dir_layout.addLayout(path_layout)
        
        # Directory structure options
        dir_layout.addWidget(QLabel('Directory Structure - 目录结构:'))
        self.dir_structure_group = QButtonGroup()
        
        self.flat_radio = QRadioButton('Flat - 扁平结构 (所有音乐直接保存到设置目录)')
        self.source_radio = QRadioButton('By Source - 按音乐源分类 (在设置目录下按音乐源创建子文件夹)')
        self.date_radio = QRadioButton('By Date - 按日期分类 (原有结构: 音乐源/日期-关键词/)')
        
        self.dir_structure_group.addButton(self.flat_radio, 0)
        self.dir_structure_group.addButton(self.source_radio, 1)
        self.dir_structure_group.addButton(self.date_radio, 2)
        
        # Set default selection
        dir_structure = self.current_settings.get('dir_structure', 'flat')
        if dir_structure == 'flat':
            self.flat_radio.setChecked(True)
        elif dir_structure == 'source':
            self.source_radio.setChecked(True)
        else:
            self.date_radio.setChecked(True)
        
        dir_layout.addWidget(self.flat_radio)
        dir_layout.addWidget(self.source_radio)
        dir_layout.addWidget(self.date_radio)
        
        dir_group.setLayout(dir_layout)
        main_layout.addWidget(dir_group)
        
        # Cookies configuration section
        cookies_group = QGroupBox('Cookies Configuration - Cookies配置 (用于VIP音质)')
        cookies_layout = QVBoxLayout()
        cookies_layout.setContentsMargins(15, 20, 15, 15)
        
        # Create tabs for different platforms
        self.cookies_tabs = QTabWidget()
        
        # Music platform cookies
        self.platform_cookies = {}
        platforms = [
            ('QQMusicClient', 'QQ音乐'),
            ('NeteaseMusicClient', '网易云'),
            ('KuwoMusicClient', '酷我'),
            ('MiguMusicClient', '咪咕'),
            ('KugouMusicClient', '酷狗'),
            ('QianqianMusicClient', '千千'),
        ]
        
        for platform_key, platform_name in platforms:
            tab = QWidget()
            tab_layout = QVBoxLayout()
            tab_layout.setSpacing(8)
            
            # Search cookies
            tab_layout.addWidget(QLabel(f'Search Cookies - 搜索Cookie:'))
            search_cookie_edit = QTextEdit()
            search_cookie_edit.setMaximumHeight(80)
            search_cookie_edit.setPlaceholderText('例如: uin=123456; qm_keyst=xxxxx; ...')
            search_cookie_edit.setText(self.current_settings.get('cookies', {}).get(platform_key, {}).get('search', ''))
            tab_layout.addWidget(search_cookie_edit)
            
            # Download cookies
            tab_layout.addWidget(QLabel(f'Download Cookies - 下载Cookie:'))
            download_cookie_edit = QTextEdit()
            download_cookie_edit.setMaximumHeight(80)
            download_cookie_edit.setPlaceholderText('通常与Search Cookie相同')
            download_cookie_edit.setText(self.current_settings.get('cookies', {}).get(platform_key, {}).get('download', ''))
            tab_layout.addWidget(download_cookie_edit)
            
            # Copy button
            copy_btn = QPushButton('Copy Search to Download - 复制搜索Cookie到下载')
            copy_btn.setCursor(Qt.PointingHandCursor)
            copy_btn.clicked.connect(lambda checked, s=search_cookie_edit, d=download_cookie_edit: d.setText(s.toPlainText()))
            tab_layout.addWidget(copy_btn)
            
            tab_layout.addStretch()
            tab.setLayout(tab_layout)
            self.cookies_tabs.addTab(tab, platform_name)
            
            self.platform_cookies[platform_key] = {
                'search': search_cookie_edit,
                'download': download_cookie_edit
            }
        
        # Quark cookies tab
        quark_tab = QWidget()
        quark_layout = QVBoxLayout()
        quark_layout.setSpacing(10)
        quark_layout.addWidget(QLabel('夸克网盘Cookie (用于下载分享网站的无损音乐):'))
        self.quark_cookie_edit = QTextEdit()
        self.quark_cookie_edit.setPlaceholderText('登录 https://pan.quark.cn/ 后，从浏览器开发者工具获取Cookie')
        self.quark_cookie_edit.setText(self.current_settings.get('quark_cookies', ''))
        quark_layout.addWidget(self.quark_cookie_edit)
        quark_layout.addWidget(QLabel('适用于: 米兔音乐、歌曲宝、音乐岛、布谷音乐等分享网站'))
        quark_layout.addStretch()
        quark_tab.setLayout(quark_layout)
        self.cookies_tabs.addTab(quark_tab, '夸克网盘')
        
        cookies_layout.addWidget(self.cookies_tabs)
        cookies_group.setLayout(cookies_layout)
        main_layout.addWidget(cookies_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        self.save_button = QPushButton('Save - 保存')
        self.save_button.setObjectName('primaryButton')
        self.save_button.setMinimumWidth(120)
        self.cancel_button = QPushButton('Cancel - 取消')
        self.cancel_button.setMinimumWidth(120)
        self.save_button.setCursor(Qt.PointingHandCursor)
        self.cancel_button.setCursor(Qt.PointingHandCursor)
        self.save_button.clicked.connect(self.save_settings)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
    
    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, 'Select Download Directory - 选择下载目录', self.dir_edit.text())
        if directory:
            self.dir_edit.setText(directory)
    
    def save_settings(self):
        # Determine directory structure
        if self.flat_radio.isChecked():
            dir_structure = 'flat'
        elif self.source_radio.isChecked():
            dir_structure = 'source'
        else:
            dir_structure = 'date'
        
        self.settings_result = {
            'work_dir': self.dir_edit.text(),
            'dir_structure': dir_structure,
            'is_dark': self.dark_theme_radio.isChecked(),
            'cookies': {},
            'quark_cookies': self.quark_cookie_edit.toPlainText().strip()
        }
        
        for platform_key, edits in self.platform_cookies.items():
            search_cookie = edits['search'].toPlainText().strip()
            download_cookie = edits['download'].toPlainText().strip()
            if search_cookie or download_cookie:
                self.settings_result['cookies'][platform_key] = {
                    'search': search_cookie,
                    'download': download_cookie
                }
        
        self.accept()
    
    def get_settings(self):
        return getattr(self, 'settings_result', None)


'''MusicdlGUI'''
class MusicdlGUI(QWidget):
    def __init__(self):
        super(MusicdlGUI, self).__init__()
        # Load settings first
        self.load_settings()
        
        # Apply modern style
        self.is_dark = self.settings.get('is_dark', False)
        self.setStyleSheet(get_stylesheet(self.is_dark))
        
        # initialize
        self.setWindowTitle('MusicdlGUI —— Charles的皮卡丘')
        icon_path = os.path.join(os.path.dirname(__file__), 'icon.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        self.setMinimumSize(1100, 750)
        self.initialize()
        
        # UI Elements
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)
        
        # Header / Title and Settings
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)
        title_label = QLabel('MusicdlGUI')
        title_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #0078d4;")
        
        self.button_theme = QPushButton('Theme - 切换主题')
        self.button_theme.setCursor(Qt.PointingHandCursor)
        self.button_theme.setMinimumWidth(150)
        self.button_theme.clicked.connect(self.toggle_theme)
        
        self.button_settings = QPushButton('Settings - 设置')
        self.button_settings.setCursor(Qt.PointingHandCursor)
        self.button_settings.setMinimumWidth(130)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.button_theme)
        header_layout.addWidget(self.button_settings)
        main_layout.addLayout(header_layout)
        
        # Search Engine Section
        engine_group = QGroupBox('Search Engine - 搜索源选择 (建议选2-3个)')
        engine_layout = QHBoxLayout()
        engine_layout.setContentsMargins(15, 20, 15, 15)
        
        self.src_names = ['QQMusicClient', 'KuwoMusicClient', 'MiguMusicClient', 'QianqianMusicClient', 'KugouMusicClient', 'NeteaseMusicClient']
        self.check_boxes = []
        for idx, src in enumerate(self.src_names):
            display_name = src.replace('Client', '')
            cb = QCheckBox(display_name)
            cb.setProperty('client_name', src) # Store the real client name
            cb.setCursor(Qt.PointingHandCursor)
            if idx < 3:
                cb.setCheckState(QtCore.Qt.Checked)
            else:
                cb.setCheckState(QtCore.Qt.Unchecked)
            self.check_boxes.append(cb)
            engine_layout.addWidget(cb)
        engine_group.setLayout(engine_layout)
        main_layout.addWidget(engine_group)
        
        # Search Status Checklist Section (New)
        self.status_group = QGroupBox('Search Status - 各源搜索状态')
        self.status_group.setVisible(False) # Hidden by default
        self.status_grid = QGridLayout()
        self.status_grid.setContentsMargins(15, 15, 15, 15)
        self.status_group.setLayout(self.status_grid)
        self.source_status_labels = {}
        main_layout.addWidget(self.status_group)
        
        # Keyword Search Section
        search_layout = QHBoxLayout()
        search_layout.setSpacing(15)
        self.lineedit_keyword = QLineEdit('尾戒')
        self.lineedit_keyword.setPlaceholderText('Enter song name or singer...')
        self.lineedit_keyword.setFixedHeight(45) # Slightly taller
        self.button_keyword = QPushButton('Search - 搜索')
        self.button_keyword.setObjectName('button_keyword')
        self.button_keyword.setCursor(Qt.PointingHandCursor)
        self.button_keyword.setMinimumWidth(140) # More width
        self.button_keyword.setFixedHeight(45) # Slightly taller
        search_layout.addWidget(QLabel('Keywords:'))
        search_layout.addWidget(self.lineedit_keyword)
        search_layout.addWidget(self.button_keyword)
        main_layout.addLayout(search_layout)
        
        # Table Section
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(7)
        self.results_table.setHorizontalHeaderLabels(['ID', 'Singers', 'Songname', 'Filesize', 'Duration', 'Album', 'Source'])
        
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter) # Align text to left
        header.setSortIndicatorShown(True) # Ensure indicator is always shown when sorting
        header.setSectionsClickable(True)
        # Fix: Ensure arrows are visible by setting a fixed size for the indicator
        header.setStyleSheet("QHeaderView::section { padding-right: 30px; }") # Reserve space for arrow
        
        self.results_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.results_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.verticalHeader().setVisible(False)
        self.results_table.setShowGrid(False)
        self.results_table.setSortingEnabled(True) # Enable sorting
        main_layout.addWidget(self.results_table)
        
        # Progress and Status Section
        bottom_layout = QVBoxLayout()
        bottom_layout.setSpacing(10)
        
        # Detailed task info
        self.label_task_info = QLabel('Ready - 就绪')
        self.label_task_info.setStyleSheet("color: #0078d4; font-weight: bold;")
        bottom_layout.addWidget(self.label_task_info)
        
        progress_layout = QHBoxLayout()
        progress_layout.setSpacing(15)
        self.label_download = QLabel('Download progress:')
        self.bar_download = QProgressBar()
        self.bar_download.setValue(0)
        self.label_progress_detail = QLabel('0.0MB / 0.0MB')
        self.label_progress_detail.setMinimumWidth(120)
        self.label_progress_detail.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        progress_layout.addWidget(self.label_download)
        progress_layout.addWidget(self.bar_download)
        progress_layout.addWidget(self.label_progress_detail)
        bottom_layout.addLayout(progress_layout)
        
        dir_structure_text = {
            'flat': 'Flat/扁平',
            'source': 'By Source/按源',
            'date': 'By Date/按日期'
        }.get(self.settings.get('dir_structure', 'flat'), 'Flat/扁平')
        self.status_label = QLabel(f'Download directory: {self.settings.get("work_dir", "musicdl_outputs")} [{dir_structure_text}]')
        self.status_label.setStyleSheet("color: #888888; font-size: 11px;")
        bottom_layout.addWidget(self.status_label)
        
        main_layout.addLayout(bottom_layout)
        
        self.setLayout(main_layout)
        
        # context menu
        self.context_menu = QMenu(self)
        self.action_download = self.context_menu.addAction('Download')
        
        # connect
        self.button_keyword.clicked.connect(self.search)
        self.button_settings.clicked.connect(self.open_settings)
        self.results_table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.results_table.customContextMenuRequested.connect(self.mouseclick)
        self.action_download.triggered.connect(self.download)
        self.lineedit_keyword.returnPressed.connect(self.search)

    '''toggle_theme'''
    def toggle_theme(self):
        self.is_dark = not self.is_dark
        self.settings['is_dark'] = self.is_dark
        self.save_settings()
        self.setStyleSheet(get_stylesheet(self.is_dark))
    
    '''load_settings'''
    def load_settings(self):
        self.settings_file = os.path.join(os.path.dirname(__file__), 'settings.json')
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
            else:
                self.settings = {
                    'work_dir': 'musicdl_outputs', 
                    'dir_structure': 'flat',  # Default to flat structure
                    'cookies': {}, 
                    'quark_cookies': ''
                }
        except:
            self.settings = {
                'work_dir': 'musicdl_outputs', 
                'dir_structure': 'flat',
                'cookies': {}, 
                'quark_cookies': ''
            }
    
    '''save_settings'''
    def save_settings(self):
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            QMessageBox.warning(self, 'Warning - 警告', f'Failed to save settings: {str(e)}')
    
    '''open_settings'''
    def open_settings(self):
        dialog = SettingsDialog(self, self.settings)
        if dialog.exec_() == QDialog.Accepted:
            new_settings = dialog.get_settings()
            if new_settings:
                self.settings = new_settings
                self.save_settings()
                # Update theme if changed
                self.is_dark = self.settings.get('is_dark', False)
                self.setStyleSheet(get_stylesheet(self.is_dark))
                # Update status label with directory structure info
                dir_structure_text = {
                    'flat': 'Flat/扁平',
                    'source': 'By Source/按源',
                    'date': 'By Date/按日期'
                }.get(self.settings.get('dir_structure', 'flat'), 'Flat/扁平')
                self.status_label.setText(f'Download directory: {self.settings.get("work_dir", "musicdl_outputs")} [{dir_structure_text}]')
                self.status_label.setStyleSheet("color: #888888; font-size: 11px;")
                QMessageBox.information(self, 'Success - 成功', 'Settings saved successfully! - 设置保存成功！\n\n请重新搜索以应用新的Cookie设置。')
    
    '''initialize'''
    def initialize(self):
        self.search_results = {}
        self.music_records = {}
        self.selected_music_idx = -10000
        self.music_client = None
    '''mouseclick'''
    def mouseclick(self):
        self.context_menu.move(QCursor().pos())
        self.context_menu.show()
    '''download'''
    def download(self):
        if hasattr(self, 'download_worker') and self.download_worker.isRunning():
            QMessageBox.warning(self, 'Warning - 警告', 'A download is already in progress!\n正在下载中，请稍候！')
            return

        self.selected_music_idx = str(self.results_table.selectedItems()[0].row())
        song_info = self.music_records.get(self.selected_music_idx)
        
        # Determine download directory based on user settings
        custom_work_dir = self.settings.get('work_dir', 'musicdl_outputs')
        dir_structure = self.settings.get('dir_structure', 'flat')
        
        if dir_structure == 'flat':
            download_dir = custom_work_dir
        elif dir_structure == 'source':
            download_dir = os.path.join(custom_work_dir, song_info['source'])
        else:
            download_dir = song_info.get('work_dir', os.path.join(custom_work_dir, song_info['source']))
        
        touchdir(download_dir)
        
        # Generate filename
        if dir_structure == 'flat':
            safe_singer = sanitize_filepath(song_info['singers']).replace('/', '_').replace('\\', '_')
            filename = f"{song_info['song_name']} - {safe_singer}.{song_info['ext']}"
        else:
            filename = f"{song_info['song_name']}.{song_info['ext']}"
        
        # UI updates
        self.label_task_info.setText(f'Downloading: {song_info["song_name"]} - {song_info["singers"]}')
        self.button_keyword.setEnabled(False)
        self.bar_download.setValue(0)
        self.label_progress_detail.setText('Initializing...')

        # Start background download
        self.download_worker = DownloadWorker(song_info, download_dir, filename, self.music_client)
        self.download_worker.progress_sig.connect(self.update_download_progress)
        self.download_worker.finished_sig.connect(self.download_finished)
        self.download_worker.start()

    def update_download_progress(self, percent, detail):
        self.bar_download.setValue(percent)
        self.label_progress_detail.setText(detail)

    def download_finished(self, success, msg, file_path):
        self.button_keyword.setEnabled(True)
        self.label_task_info.setText('Ready - 就绪')
        if success:
            QMessageBox.information(self, 'Success - 成功', f"{msg}\n\nSaved to: {file_path}")
        else:
            QMessageBox.critical(self, 'Error - 错误', msg)
        self.bar_download.setValue(0)
        self.label_progress_detail.setText('0.0MB / 0.0MB')
    '''search'''
    def search(self):
        if hasattr(self, 'search_worker') and self.search_worker.isRunning():
            return

        # selected music sources
        music_sources = []
        for cb in self.check_boxes:
            if cb.isChecked():
                music_sources.append(cb.property('client_name'))
        
        if not music_sources:
            QMessageBox.warning(self, 'Warning - 警告', 'Please select at least one music source!\n请至少选择一个音乐源！')
            return
        
        # keyword
        keyword = self.lineedit_keyword.text().strip()
        if not keyword:
            QMessageBox.warning(self, 'Warning - 警告', 'Please enter a keyword!\n请输入关键词！')
            return
        
        # UI Setup for Checklist
        self.label_task_info.setText(f'Searching "{keyword}"...')
        self.button_keyword.setEnabled(False)
        self.results_table.setRowCount(0)
        self.music_records = {}
        self.all_aggregated_results = {}
        self.completed_sources_count = 0
        self.total_sources_to_search = len(music_sources)
        
        # Reset and show status checklist
        # Clear old status widgets
        while self.status_grid.count():
            child = self.status_grid.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        self.source_status_labels = {}
        row, col = 0, 0
        for source in music_sources:
            display_name = source.replace('Client', '')
            label = QLabel(f"⏳ {display_name}: Searching...")
            label.setStyleSheet("color: #0078d4;")
            self.source_status_labels[source] = label
            self.status_grid.addWidget(label, row, col)
            col += 1
            if col > 2: # 3 columns
                col = 0
                row += 1
        
        self.status_group.setVisible(True)
        
        # Start search worker
        self.search_worker = SearchWorker(music_sources, keyword, self.settings)
        self.search_worker.finished_sig.connect(self.handle_source_success)
        self.search_worker.error_sig.connect(self.handle_source_error)
        self.search_worker.finished.connect(self.handle_all_finished)
        self.search_worker.start()

    def handle_source_success(self, source_name, results):
        self.all_aggregated_results[source_name] = results
        display_name = source_name.replace('Client', '')
        count = len(results)
        label = self.source_status_labels.get(source_name)
        if label:
            label.setText(f"✅ {display_name}: Found {count}")
            label.setStyleSheet("color: #28a745; font-weight: bold;")
        self.completed_sources_count += 1

    def handle_source_error(self, source_name, error_msg):
        display_name = source_name.replace('Client', '')
        label = self.source_status_labels.get(source_name)
        if label:
            label.setText(f"❌ {display_name}: Error")
            label.setToolTip(error_msg)
            label.setStyleSheet("color: #dc3545;")
        self.completed_sources_count += 1

    def handle_all_finished(self):
        self.button_keyword.setEnabled(True)
        self.label_task_info.setText('Ready - 就绪')
        self.display_search_results(self.all_aggregated_results)
        
        # Auto-hide status group after 5 seconds
        QTimer.singleShot(5000, lambda: self.status_group.setVisible(False))

    def display_search_results(self, search_results):
        self.search_results = search_results
        
        # Update status after search
        total_results = sum(len(results) for results in self.search_results.values())
        dir_structure_text = {
            'flat': 'Flat/扁平',
            'source': 'By Source/按源',
            'date': 'By Date/按日期'
        }.get(self.settings.get('dir_structure', 'flat'), 'Flat/扁平')
        self.status_label.setText(f'Download directory: {self.settings.get("work_dir", "musicdl_outputs")} [{dir_structure_text}] | Found {total_results} results')
        self.status_label.setStyleSheet("color: #28a745; font-size: 11px;")
        
        # showing
        self.results_table.setSortingEnabled(False)
        self.results_table.horizontalHeader().setSortIndicatorShown(False)
        count, row = 0, 0
        for per_source_search_results in self.search_results.values():
            count += len(per_source_search_results)
        self.results_table.setRowCount(count)
        
        self.music_records = {} # Clear old records
        for _, (_, per_source_search_results) in enumerate(self.search_results.items()):
            for _, per_source_search_result in enumerate(per_source_search_results):
                # Prepare data for sorting
                fs_str = per_source_search_result['file_size']
                fs_val = 0
                try:
                    parts = fs_str.split()
                    num = float(parts[0])
                    unit = parts[1].upper()
                    if unit == 'GB': fs_val = num * 1024 * 1024 * 1024
                    elif unit == 'MB': fs_val = num * 1024 * 1024
                    elif unit == 'KB': fs_val = num * 1024
                    else: fs_val = num
                except: fs_val = 0
                
                dur_str = per_source_search_result['duration']
                dur_val = 0
                try:
                    parts = dur_str.split(':')
                    if len(parts) == 2: dur_val = int(parts[0]) * 60 + int(parts[1])
                    elif len(parts) == 3: dur_val = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
                except: dur_val = 0

                items = [
                    (str(row), row),
                    (per_source_search_result['singers'], per_source_search_result['singers']),
                    (per_source_search_result['song_name'], per_source_search_result['song_name']),
                    (fs_str, fs_val),
                    (dur_str, dur_val),
                    (per_source_search_result['album'], per_source_search_result['album']),
                    (per_source_search_result['source'], per_source_search_result['source'])
                ]

                for column, (text, sort_val) in enumerate(items):
                    table_item = SortableTableWidgetItem(text, sort_val)
                    table_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                    self.results_table.setItem(row, column, table_item)
                
                self.music_records.update({str(row): per_source_search_result})
                row += 1
        
        self.results_table.setSortingEnabled(True)
        self.results_table.horizontalHeader().setSortIndicatorShown(True)


'''tests'''
if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = MusicdlGUI()
    gui.show()
    sys.exit(app.exec_())
