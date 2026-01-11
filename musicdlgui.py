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
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon, QCursor
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QGroupBox, QLabel, QLineEdit, QPushButton, 
                             QCheckBox, QTableWidget, QProgressBar, QMenu, 
                             QMessageBox, QHeaderView, QAbstractItemView, 
                             QGridLayout, QDialog)
from musicdl.modules.utils.misc import touchdir, sanitize_filepath

# Import custom modules
from styles import get_stylesheet
from components import SortableTableWidgetItem
from workers import SearchWorker, DownloadWorker
from dialogs import SettingsDialog


class MusicdlGUI(QWidget):
    """
    Main GUI window for MusicdlGUI application
    """
    def __init__(self):
        super(MusicdlGUI, self).__init__()
        # Load settings first
        self.load_settings()
        
        # Apply modern style
        self.is_dark = self.settings.get('is_dark', False)
        self.setStyleSheet(get_stylesheet(self.is_dark))
        
        # Initialize
        self.setWindowTitle('MusicdlGUI —— Charles的皮卡丘')
        icon_path = os.path.join(os.path.dirname(__file__), 'icon.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        self.setMinimumSize(1100, 750)
        self.initialize()
        
        # UI Elements
        self.init_ui()
    
    def init_ui(self):
        """Initialize user interface"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)
        
        # Header / Title and Settings
        self._init_header(main_layout)
        
        # Search Engine Section
        self._init_search_engine_section(main_layout)
        
        # Search Status Checklist Section (New)
        self._init_status_section(main_layout)
        
        # Keyword Search Section
        self._init_keyword_section(main_layout)
        
        # Table Section
        self._init_table_section(main_layout)
        
        # Progress and Status Section
        self._init_progress_section(main_layout)
        
        self.setLayout(main_layout)
        
        # Context menu
        self.context_menu = QMenu(self)
        self.action_download = self.context_menu.addAction('Download')
        
        # Connect signals
        self.button_keyword.clicked.connect(self.search)
        self.button_settings.clicked.connect(self.open_settings)
        self.results_table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.results_table.customContextMenuRequested.connect(self.mouseclick)
        self.action_download.triggered.connect(self.download)
        self.lineedit_keyword.returnPressed.connect(self.search)

    def _init_header(self, main_layout):
        """Initialize header section with title and buttons"""
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

    def _init_search_engine_section(self, main_layout):
        """Initialize search engine selection section"""
        engine_group = QGroupBox('Search Engine - 搜索源选择 (建议选2-3个)')
        engine_layout = QHBoxLayout()
        engine_layout.setContentsMargins(15, 20, 15, 15)
        
        self.src_names = ['QQMusicClient', 'KuwoMusicClient', 'MiguMusicClient', 
                         'QianqianMusicClient', 'KugouMusicClient', 'NeteaseMusicClient']
        self.check_boxes = []
        for idx, src in enumerate(self.src_names):
            display_name = src.replace('Client', '')
            cb = QCheckBox(display_name)
            cb.setProperty('client_name', src)  # Store the real client name
            cb.setCursor(Qt.PointingHandCursor)
            if idx < 3:
                cb.setCheckState(QtCore.Qt.Checked)
            else:
                cb.setCheckState(QtCore.Qt.Unchecked)
            self.check_boxes.append(cb)
            engine_layout.addWidget(cb)
        engine_group.setLayout(engine_layout)
        main_layout.addWidget(engine_group)

    def _init_status_section(self, main_layout):
        """Initialize search status section"""
        self.status_group = QGroupBox('Search Status - 各源搜索状态')
        self.status_group.setVisible(False)  # Hidden by default
        self.status_grid = QGridLayout()
        self.status_grid.setContentsMargins(15, 15, 15, 15)
        self.status_group.setLayout(self.status_grid)
        self.source_status_labels = {}
        main_layout.addWidget(self.status_group)

    def _init_keyword_section(self, main_layout):
        """Initialize keyword search section"""
        search_layout = QHBoxLayout()
        search_layout.setSpacing(15)
        self.lineedit_keyword = QLineEdit('尾戒')
        self.lineedit_keyword.setPlaceholderText('Enter song name or singer...')
        self.lineedit_keyword.setFixedHeight(45)  # Slightly taller
        self.button_keyword = QPushButton('Search - 搜索')
        self.button_keyword.setObjectName('button_keyword')
        self.button_keyword.setCursor(Qt.PointingHandCursor)
        self.button_keyword.setMinimumWidth(140)  # More width
        self.button_keyword.setFixedHeight(45)  # Slightly taller
        search_layout.addWidget(QLabel('Keywords:'))
        search_layout.addWidget(self.lineedit_keyword)
        search_layout.addWidget(self.button_keyword)
        main_layout.addLayout(search_layout)

    def _init_table_section(self, main_layout):
        """Initialize results table section"""
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(7)
        self.results_table.setHorizontalHeaderLabels(['ID', 'Singers', 'Songname', 'Filesize', 'Duration', 'Album', 'Source'])
        
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # Align text to left
        header.setSortIndicatorShown(True)  # Ensure indicator is always shown when sorting
        header.setSectionsClickable(True)
        # Fix: Ensure arrows are visible by setting a fixed size for the indicator
        header.setStyleSheet("QHeaderView::section { padding-right: 30px; }")  # Reserve space for arrow
        
        self.results_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.results_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.verticalHeader().setVisible(False)
        self.results_table.setShowGrid(False)
        self.results_table.setSortingEnabled(True)  # Enable sorting
        main_layout.addWidget(self.results_table)

    def _init_progress_section(self, main_layout):
        """Initialize progress and status section"""
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

    def toggle_theme(self):
        """Toggle between light and dark theme"""
        self.is_dark = not self.is_dark
        self.settings['is_dark'] = self.is_dark
        self.save_settings()
        self.setStyleSheet(get_stylesheet(self.is_dark))
    
    def load_settings(self):
        """Load settings from JSON file"""
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
    
    def save_settings(self):
        """Save settings to JSON file"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            QMessageBox.warning(self, 'Warning - 警告', f'Failed to save settings: {str(e)}')
    
    def open_settings(self):
        """Open settings dialog"""
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
    
    def initialize(self):
        """Initialize application state"""
        self.search_results = {}
        self.music_records = {}
        self.selected_music_idx = -10000
        self.music_client = None
    
    def mouseclick(self):
        """Show context menu on right click"""
        self.context_menu.move(QCursor().pos())
        self.context_menu.show()
    
    def download(self):
        """Handle download action"""
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
        """Update download progress bar"""
        self.bar_download.setValue(percent)
        self.label_progress_detail.setText(detail)

    def download_finished(self, success, msg, file_path):
        """Handle download completion"""
        self.button_keyword.setEnabled(True)
        self.label_task_info.setText('Ready - 就绪')
        if success:
            QMessageBox.information(self, 'Success - 成功', f"{msg}\n\nSaved to: {file_path}")
        else:
            QMessageBox.critical(self, 'Error - 错误', msg)
        self.bar_download.setValue(0)
        self.label_progress_detail.setText('0.0MB / 0.0MB')
    
    def search(self):
        """Handle search action"""
        if hasattr(self, 'search_worker') and self.search_worker.isRunning():
            return

        # Selected music sources
        music_sources = []
        for cb in self.check_boxes:
            if cb.isChecked():
                music_sources.append(cb.property('client_name'))
        
        if not music_sources:
            QMessageBox.warning(self, 'Warning - 警告', 'Please select at least one music source!\n请至少选择一个音乐源！')
            return
        
        # Keyword
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
            if col > 2:  # 3 columns
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
        """Handle successful search from a source"""
        self.all_aggregated_results[source_name] = results
        display_name = source_name.replace('Client', '')
        count = len(results)
        label = self.source_status_labels.get(source_name)
        if label:
            label.setText(f"✅ {display_name}: Found {count}")
            label.setStyleSheet("color: #28a745; font-weight: bold;")
        self.completed_sources_count += 1

    def handle_source_error(self, source_name, error_msg):
        """Handle search error from a source"""
        display_name = source_name.replace('Client', '')
        label = self.source_status_labels.get(source_name)
        if label:
            label.setText(f"❌ {display_name}: Error")
            label.setToolTip(error_msg)
            label.setStyleSheet("color: #dc3545;")
        self.completed_sources_count += 1

    def handle_all_finished(self):
        """Handle completion of all searches"""
        self.button_keyword.setEnabled(True)
        self.label_task_info.setText('Ready - 就绪')
        self.display_search_results(self.all_aggregated_results)
        
        # Auto-hide status group after 5 seconds
        QTimer.singleShot(5000, lambda: self.status_group.setVisible(False))

    def display_search_results(self, search_results):
        """Display search results in table"""
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
        
        # Showing
        self.results_table.setSortingEnabled(False)
        self.results_table.horizontalHeader().setSortIndicatorShown(False)
        count, row = 0, 0
        for per_source_search_results in self.search_results.values():
            count += len(per_source_search_results)
        self.results_table.setRowCount(count)
        
        self.music_records = {}  # Clear old records
        for _, (_, per_source_search_results) in enumerate(self.search_results.items()):
            for _, per_source_search_result in enumerate(per_source_search_results):
                # Prepare data for sorting
                fs_str = per_source_search_result['file_size']
                fs_val = 0
                try:
                    parts = fs_str.split()
                    num = float(parts[0])
                    unit = parts[1].upper()
                    if unit == 'GB':
                        fs_val = num * 1024 * 1024 * 1024
                    elif unit == 'MB':
                        fs_val = num * 1024 * 1024
                    elif unit == 'KB':
                        fs_val = num * 1024
                    else:
                        fs_val = num
                except:
                    fs_val = 0
                
                dur_str = per_source_search_result['duration']
                dur_val = 0
                try:
                    parts = dur_str.split(':')
                    if len(parts) == 2:
                        dur_val = int(parts[0]) * 60 + int(parts[1])
                    elif len(parts) == 3:
                        dur_val = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
                except:
                    dur_val = 0

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


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    gui = MusicdlGUI()
    gui.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
