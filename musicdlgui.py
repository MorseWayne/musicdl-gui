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


'''SettingsDialog'''
class SettingsDialog(QDialog):
    def __init__(self, parent=None, current_settings=None):
        super(SettingsDialog, self).__init__(parent)
        self.setWindowTitle('Settings - 设置')
        self.setMinimumWidth(700)
        self.setMinimumHeight(500)
        self.current_settings = current_settings or {}
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Download directory section
        dir_group = QGroupBox('Download Directory - 下载目录')
        dir_layout = QVBoxLayout()
        
        # Directory path
        path_layout = QHBoxLayout()
        self.dir_edit = QLineEdit(self.current_settings.get('work_dir', 'musicdl_outputs'))
        self.dir_button = QPushButton('Browse - 浏览')
        self.dir_button.clicked.connect(self.select_directory)
        path_layout.addWidget(QLabel('Directory - 目录:'))
        path_layout.addWidget(self.dir_edit)
        path_layout.addWidget(self.dir_button)
        dir_layout.addLayout(path_layout)
        
        # Directory structure options
        dir_layout.addWidget(QLabel('\nDirectory Structure - 目录结构:'))
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
        layout.addWidget(dir_group)
        
        # Cookies configuration section
        cookies_group = QGroupBox('Cookies Configuration - Cookies配置 (用于VIP音质)')
        cookies_layout = QVBoxLayout()
        
        # Create tabs for different platforms
        self.cookies_tabs = QTabWidget()
        
        # Music platform cookies
        self.platform_cookies = {}
        platforms = [
            ('QQMusicClient', 'QQ音乐'),
            ('NeteaseMusicClient', '网易云音乐'),
            ('KuwoMusicClient', '酷我音乐'),
            ('MiguMusicClient', '咪咕音乐'),
            ('KugouMusicClient', '酷狗音乐'),
            ('QianqianMusicClient', '千千音乐'),
        ]
        
        for platform_key, platform_name in platforms:
            tab = QWidget()
            tab_layout = QVBoxLayout()
            
            # Search cookies
            tab_layout.addWidget(QLabel(f'Search Cookies - 搜索Cookie:'))
            search_cookie_edit = QTextEdit()
            search_cookie_edit.setMaximumHeight(100)
            search_cookie_edit.setPlaceholderText('例如: uin=123456; qm_keyst=xxxxx; ...')
            search_cookie_edit.setText(self.current_settings.get('cookies', {}).get(platform_key, {}).get('search', ''))
            tab_layout.addWidget(search_cookie_edit)
            
            # Download cookies
            tab_layout.addWidget(QLabel(f'Download Cookies - 下载Cookie:'))
            download_cookie_edit = QTextEdit()
            download_cookie_edit.setMaximumHeight(100)
            download_cookie_edit.setPlaceholderText('通常与Search Cookie相同')
            download_cookie_edit.setText(self.current_settings.get('cookies', {}).get(platform_key, {}).get('download', ''))
            tab_layout.addWidget(download_cookie_edit)
            
            # Copy button
            copy_btn = QPushButton('Copy Search to Download - 复制搜索Cookie到下载')
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
        layout.addWidget(cookies_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton('Save - 保存')
        self.cancel_button = QPushButton('Cancel - 取消')
        self.save_button.clicked.connect(self.save_settings)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
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
        # initialize
        self.setWindowTitle('MusicdlGUI —— Charles的皮卡丘')
        # Remove icon if icon.ico doesn't exist
        icon_path = os.path.join(os.path.dirname(__file__), 'icon.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.setFixedSize(900, 520)
        self.load_settings()
        self.initialize()
        # search sources
        self.src_names = ['QQMusicClient', 'KuwoMusicClient', 'MiguMusicClient', 'QianqianMusicClient', 'KugouMusicClient', 'NeteaseMusicClient']
        self.label_src = QLabel('Search Engine (建议选2-3个):')
        self.check_boxes = []
        for idx, src in enumerate(self.src_names):
            cb = QCheckBox(src, self)
            # Only check first 3 sources by default for faster search
            if idx < 3:
                cb.setCheckState(QtCore.Qt.Checked)
            else:
                cb.setCheckState(QtCore.Qt.Unchecked)
            self.check_boxes.append(cb)
        # input boxes
        self.label_keyword = QLabel('Keywords:')
        self.lineedit_keyword = QLineEdit('尾戒')
        self.button_keyword = QPushButton('Search')
        self.button_settings = QPushButton('Settings - 设置')
        # search results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(7)
        self.results_table.setHorizontalHeaderLabels(['ID', 'Singers', 'Songname', 'Filesize', 'Duration', 'Album', 'Source'])
        self.results_table.horizontalHeader().setStyleSheet("QHeaderView::section{background:skyblue;color:black;}")
        self.results_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.results_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        # mouse click menu
        self.context_menu = QMenu(self)
        self.action_download = self.context_menu.addAction('Download')
        # progress bar
        self.bar_download = QProgressBar(self)
        self.label_download = QLabel('Download progress:')
        # status label
        dir_structure_text = {
            'flat': 'Flat/扁平',
            'source': 'By Source/按源',
            'date': 'By Date/按日期'
        }.get(self.settings.get('dir_structure', 'flat'), 'Flat/扁平')
        self.status_label = QLabel(f'Download directory: {self.settings.get("work_dir", "musicdl_outputs")} [{dir_structure_text}]')
        self.status_label.setStyleSheet("color: gray; font-size: 10px;")
        # grid
        grid = QGridLayout()
        grid.addWidget(self.label_src, 0, 0, 1, 1)
        for idx, cb in enumerate(self.check_boxes): grid.addWidget(cb, 0, idx+1, 1, 1)
        grid.addWidget(self.label_keyword, 1, 0, 1, 1)
        grid.addWidget(self.lineedit_keyword, 1, 1, 1, len(self.src_names)-2)
        grid.addWidget(self.button_keyword, 1, len(self.src_names)-1, 1, 1)
        grid.addWidget(self.button_settings, 1, len(self.src_names), 1, 1)
        grid.addWidget(self.label_download, 2, 0, 1, 1)
        grid.addWidget(self.bar_download, 2, 1, 1, len(self.src_names))
        grid.addWidget(self.status_label, 3, 0, 1, len(self.src_names)+1)
        grid.addWidget(self.results_table, 4, 0, len(self.src_names), len(self.src_names)+1)
        self.grid = grid
        self.setLayout(grid)
        # connect
        self.button_keyword.clicked.connect(self.search)
        self.button_settings.clicked.connect(self.open_settings)
        self.results_table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.results_table.customContextMenuRequested.connect(self.mouseclick)
        self.action_download.triggered.connect(self.download)
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
                # Update status label with directory structure info
                dir_structure_text = {
                    'flat': 'Flat/扁平',
                    'source': 'By Source/按源',
                    'date': 'By Date/按日期'
                }.get(self.settings.get('dir_structure', 'flat'), 'Flat/扁平')
                self.status_label.setText(f'Download directory: {self.settings.get("work_dir", "musicdl_outputs")} [{dir_structure_text}]')
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
        self.selected_music_idx = str(self.results_table.selectedItems()[0].row())
        song_info = self.music_records.get(self.selected_music_idx)
        
        # Determine download directory based on user settings
        custom_work_dir = self.settings.get('work_dir', 'musicdl_outputs')
        dir_structure = self.settings.get('dir_structure', 'flat')
        
        if dir_structure == 'flat':
            # Flat: all music files directly in work_dir
            download_dir = custom_work_dir
        elif dir_structure == 'source':
            # By source: work_dir/QQMusicClient/
            download_dir = os.path.join(custom_work_dir, song_info['source'])
        else:  # 'date' or old behavior
            # By date: work_dir/QQMusicClient/2026-01-11-时间戳/
            # Use the work_dir from song_info if available
            download_dir = song_info.get('work_dir', os.path.join(custom_work_dir, song_info['source']))
        
        touchdir(download_dir)
        
        # Generate filename
        if dir_structure == 'flat':
            # Include singer to avoid conflicts
            safe_singer = sanitize_filepath(song_info['singers']).replace('/', '_').replace('\\', '_')
            filename = f"{song_info['song_name']} - {safe_singer}.{song_info['ext']}"
        else:
            # Just song name when organized by folders
            filename = f"{song_info['song_name']}.{song_info['ext']}"
        
        download_music_file_path = sanitize_filepath(os.path.join(download_dir, filename))
        
        # Handle duplicate filenames
        if os.path.exists(download_music_file_path):
            base_name = os.path.splitext(filename)[0]
            ext = song_info['ext']
            counter = 1
            while os.path.exists(download_music_file_path):
                filename = f"{base_name} ({counter}).{ext}"
                download_music_file_path = sanitize_filepath(os.path.join(download_dir, filename))
                counter += 1
        
        with requests.get(song_info['download_url'], headers=self.music_client.music_clients[song_info['source']].default_download_headers, stream=True, verify=False) as resp:
            if resp.status_code == 200:
                total_size, chunk_size, download_size = int(resp.headers['content-length']), 1024, 0
                with open(download_music_file_path, 'wb') as fp:
                    for chunk in resp.iter_content(chunk_size=chunk_size):
                        if not chunk: continue
                        fp.write(chunk)
                        download_size += len(chunk)
                        self.bar_download.setValue(int(download_size / total_size * 100))
        QMessageBox().information(self, 'Successful Downloads', f"Finish downloading {song_info['song_name']} by {song_info['singers']}\n\nSaved to: {download_music_file_path}")
        self.bar_download.setValue(0)
    '''search'''
    def search(self):
        self.initialize()
        # selected music sources
        music_sources = []
        for cb in self.check_boxes:
            if cb.isChecked():
                music_sources.append(cb.text())
        
        if not music_sources:
            QMessageBox.warning(self, 'Warning - 警告', 'Please select at least one music source!\n请至少选择一个音乐源！')
            return {}
        
        # keyword
        keyword = self.lineedit_keyword.text()
        if not keyword.strip():
            QMessageBox.warning(self, 'Warning - 警告', 'Please enter a keyword!\n请输入关键词！')
            return {}
        
        # Update status
        self.status_label.setText(f'Searching "{keyword}" from {len(music_sources)} sources... 正在搜索中...')
        self.status_label.setStyleSheet("color: blue; font-size: 10px;")
        QApplication.processEvents()  # Force UI update
        
        # Build init_music_clients_cfg with cookies and aggressive optimization
        init_music_clients_cfg = {}
        
        # Configure cookies for each platform with aggressive timeout settings
        for platform_key, cookie_data in self.settings.get('cookies', {}).items():
            if platform_key in music_sources:
                search_cookie = cookie_data.get('search', '').strip()
                download_cookie = cookie_data.get('download', '').strip()
                if search_cookie or download_cookie:
                    init_music_clients_cfg[platform_key] = {
                        'work_dir': self.settings.get('work_dir', 'musicdl_outputs'),
                        'default_search_cookies': search_cookie,
                        'default_download_cookies': download_cookie or search_cookie,
                        'max_retries': 1,  # Only retry once (aggressive)
                        'search_size_per_source': 3,  # Only 3 results per source (faster)
                        'search_size_per_page': 3,  # Reduce page size
                    }
                else:
                    init_music_clients_cfg[platform_key] = {
                        'work_dir': self.settings.get('work_dir', 'musicdl_outputs'),
                        'max_retries': 1,
                        'search_size_per_source': 3,
                        'search_size_per_page': 3,
                    }
            else:
                init_music_clients_cfg[platform_key] = {
                    'work_dir': self.settings.get('work_dir', 'musicdl_outputs'),
                    'max_retries': 1,
                    'search_size_per_source': 3,
                    'search_size_per_page': 3,
                }
        
        # Configure Quark cookies for sharing sites
        quark_cookie = self.settings.get('quark_cookies', '').strip()
        quark_sites = ['MituMusicClient', 'GequbaoMusicClient', 'YinyuedaoMusicClient', 'BuguyyMusicClient', 
                       'JCPOOMusicClient', 'GequhaiMusicClient', 'LivePOOMusicClient', 'KKWSMusicClient', 'FLMP3MusicClient']
        if quark_cookie:
            for site in quark_sites:
                if site not in init_music_clients_cfg:
                    init_music_clients_cfg[site] = {}
                init_music_clients_cfg[site]['quark_parser_config'] = {'cookies': quark_cookie}
                init_music_clients_cfg[site]['work_dir'] = self.settings.get('work_dir', 'musicdl_outputs')
                init_music_clients_cfg[site]['max_retries'] = 1
                init_music_clients_cfg[site]['search_size_per_source'] = 3
                init_music_clients_cfg[site]['search_size_per_page'] = 3
        
        # Ensure all selected sources have aggressive optimized configuration
        for source in music_sources:
            if source not in init_music_clients_cfg:
                init_music_clients_cfg[source] = {
                    'work_dir': self.settings.get('work_dir', 'musicdl_outputs'),
                    'max_retries': 1,
                    'search_size_per_source': 3,
                    'search_size_per_page': 3,
                }
        
        # Configure request overrides with aggressive timeout
        requests_overrides = {}
        for source in music_sources:
            requests_overrides[source] = {
                'timeout': (3, 6)  # Aggressive: (connect 3s, read 6s)
            }
        
        # Reduce threadings for faster response (less resource contention)
        clients_threadings = {}
        for source in music_sources:
            clients_threadings[source] = 3  # Reduce from default 5 to 3
        
        # search
        self.music_client = musicdl.MusicClient(
            music_sources=music_sources, 
            init_music_clients_cfg=init_music_clients_cfg,
            requests_overrides=requests_overrides,
            clients_threadings=clients_threadings  # Add threading control
        )
        self.search_results = self.music_client.search(keyword=keyword)
        
        # Update status after search
        total_results = sum(len(results) for results in self.search_results.values())
        dir_structure_text = {
            'flat': 'Flat/扁平',
            'source': 'By Source/按源',
            'date': 'By Date/按日期'
        }.get(self.settings.get('dir_structure', 'flat'), 'Flat/扁平')
        self.status_label.setText(f'Download directory: {self.settings.get("work_dir", "musicdl_outputs")} [{dir_structure_text}] | Found {total_results} results')
        self.status_label.setStyleSheet("color: green; font-size: 10px;")
        
        # showing
        count, row = 0, 0
        for per_source_search_results in self.search_results.values():
            count += len(per_source_search_results)
        self.results_table.setRowCount(count)
        for _, (_, per_source_search_results) in enumerate(self.search_results.items()):
            for _, per_source_search_result in enumerate(per_source_search_results):
                for column, item in enumerate([str(row), per_source_search_result['singers'], per_source_search_result['song_name'], per_source_search_result['file_size'], per_source_search_result['duration'], per_source_search_result['album'], per_source_search_result['source']]):
                    self.results_table.setItem(row, column, QTableWidgetItem(item))
                    self.results_table.item(row, column).setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.music_records.update({str(row): per_source_search_result})
                row += 1
        # return
        return self.search_results


'''tests'''
if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = MusicdlGUI()
    gui.show()
    sys.exit(app.exec_())
