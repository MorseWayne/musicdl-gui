'''
Function:
    Dialogs for MusicdlGUI
Author:
    Zhenchao Jin
WeChat Official Account (微信公众号):
    Charles的皮卡丘
'''
import os
from pathlib import Path
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, 
                             QLabel, QLineEdit, QPushButton, QRadioButton, 
                             QButtonGroup, QTextEdit, QTabWidget, QWidget, 
                             QFileDialog, QMessageBox, QSpinBox, QScrollArea, QComboBox)
from audio_conversion import OUTPUT_FORMATS
from app_config import SOURCES, normalize_settings
from logger import get_log_directory, get_log_file_path


class SettingsDialog(QDialog):
    """
    Settings dialog for configuring application preferences
    """
    def __init__(self, parent=None, current_settings=None):
        """
        Initialize settings dialog
        
        Args:
            parent: Parent widget
            current_settings (dict): Current application settings
        """
        super(SettingsDialog, self).__init__(parent)
        self.setWindowTitle('设置')
        self.setMinimumSize(720, 540)
        self.resize(800, 700)
        self.current_settings = current_settings or {}
        self.init_ui()
    
    def init_ui(self):
        """Initialize user interface"""
        outer_layout = QVBoxLayout(self)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        main_layout = QVBoxLayout(content)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Appearance section
        self._init_appearance_section(main_layout)
        
        # Download directory section
        self._init_directory_section(main_layout)

        search_group = QGroupBox('搜索设置')
        search_layout = QHBoxLayout(search_group)
        self.search_limit = QSpinBox()
        self.search_limit.setRange(1, 30)
        self.search_limit.setValue(self.current_settings.get('search_limit', 5))
        self.search_timeout = QSpinBox()
        self.search_timeout.setRange(15, 180)
        self.search_timeout.setSuffix(' 秒')
        self.search_timeout.setValue(self.current_settings.get('search_timeout', 60))
        search_layout.addWidget(QLabel('每个来源最多结果'))
        search_layout.addWidget(self.search_limit)
        search_layout.addWidget(QLabel('每个来源搜索时限'))
        search_layout.addWidget(self.search_timeout)
        main_layout.addWidget(search_group)
        
        # Log section
        self._init_log_section(main_layout)
        
        # Cookies configuration section
        self._init_cookies_section(main_layout)
        
        # Buttons
        scroll.setWidget(content)
        outer_layout.addWidget(scroll)
        self._init_buttons(outer_layout)
    
    def _init_appearance_section(self, main_layout):
        """Initialize appearance settings section"""
        appearance_group = QGroupBox('外观')
        appearance_layout = QVBoxLayout()
        appearance_layout.setContentsMargins(15, 20, 15, 15)
        
        self.theme_group = QButtonGroup()
        self.light_theme_radio = QRadioButton('浅色模式')
        self.dark_theme_radio = QRadioButton('深色模式')
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
    
    def _init_directory_section(self, main_layout):
        """Initialize download directory settings section"""
        dir_group = QGroupBox('下载目录')
        dir_layout = QVBoxLayout()
        dir_layout.setContentsMargins(15, 20, 15, 15)
        dir_layout.setSpacing(10)
        
        # Directory path
        path_layout = QHBoxLayout()
        path_layout.setSpacing(10)
        self.dir_edit = QLineEdit(self.current_settings.get('work_dir', 'musicdl_outputs'))
        self.dir_button = QPushButton('浏览')
        self.dir_button.setMinimumWidth(100)
        self.dir_button.setCursor(Qt.PointingHandCursor)
        self.dir_button.clicked.connect(self.select_directory)
        path_layout.addWidget(QLabel('保存到'))
        path_layout.addWidget(self.dir_edit)
        path_layout.addWidget(self.dir_button)
        dir_layout.addLayout(path_layout)

        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel('保存格式'))
        self.output_format_combo = QComboBox()
        for value, label in OUTPUT_FORMATS.items():
            self.output_format_combo.addItem(label, value)
        index = self.output_format_combo.findData(self.current_settings.get('output_format', 'original'))
        self.output_format_combo.setCurrentIndex(max(0, index))
        format_layout.addWidget(self.output_format_combo)
        format_layout.addStretch()
        dir_layout.addLayout(format_layout)
        format_hint = QLabel('下载后自动转换，仅保存目标文件。WAV 文件较大；MP3 转换时使用 320 kbps，已有 MP3 保持原码率。')
        format_hint.setObjectName('mutedLabel')
        format_hint.setWordWrap(True)
        dir_layout.addWidget(format_hint)
        
        # Directory structure options
        dir_layout.addWidget(QLabel('文件组织方式'))
        self.dir_structure_group = QButtonGroup()
        
        self.flat_radio = QRadioButton('平铺（所有音乐直接保存到所选目录）')
        self.source_radio = QRadioButton('按音乐来源分类（为每个平台创建子文件夹）')
        self.date_radio = QRadioButton('按日期分类 (音乐源/日期 关键词/)')
        
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
    
    def _init_log_section(self, main_layout):
        """Initialize log settings section"""
        log_group = QGroupBox('日志与排查')
        log_layout = QVBoxLayout()
        log_layout.setContentsMargins(15, 20, 15, 15)
        log_layout.setSpacing(10)
        
        # Log file info
        log_file = get_log_file_path()
        if log_file:
            log_info_label = QLabel(f'当前日志文件: {os.path.basename(log_file)}')
        else:
            log_info_label = QLabel('日志文件: 尚未初始化')
        log_info_label.setObjectName('mutedLabel')
        log_layout.addWidget(log_info_label)
        
        # Log directory info
        try:
            log_dir = get_log_directory()
        except OSError:
            log_dir = '日志目录不可写'
        log_dir_label = QLabel(f'日志目录: {log_dir}')
        log_dir_label.setObjectName('mutedLabel')
        log_dir_label.setWordWrap(True)
        log_layout.addWidget(log_dir_label)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        open_log_dir_btn = QPushButton('打开日志目录')
        open_log_dir_btn.setCursor(Qt.PointingHandCursor)
        open_log_dir_btn.clicked.connect(self.open_log_directory)
        btn_layout.addWidget(open_log_dir_btn)
        
        open_log_file_btn = QPushButton('打开当前日志')
        open_log_file_btn.setCursor(Qt.PointingHandCursor)
        open_log_file_btn.clicked.connect(self.open_log_file)
        btn_layout.addWidget(open_log_file_btn)
        
        btn_layout.addStretch()
        log_layout.addLayout(btn_layout)
        
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)
    
    def open_log_directory(self):
        """Open log directory in file explorer"""
        try:
            if not QDesktopServices.openUrl(QUrl.fromLocalFile(get_log_directory())):
                raise OSError('系统文件管理器未能打开日志目录')
        except Exception as e:
            QMessageBox.warning(self, 'Warning - 警告', f'无法打开日志目录: {str(e)}')
    
    def open_log_file(self):
        """Open current log file"""
        log_file = get_log_file_path()
        if not log_file or not os.path.exists(log_file):
            QMessageBox.information(self, 'Info - 信息', '日志文件尚未创建')
            return
        try:
            if not QDesktopServices.openUrl(QUrl.fromLocalFile(log_file)):
                raise OSError('系统未能打开日志文件')
        except Exception as e:
            QMessageBox.warning(self, 'Warning - 警告', f'无法打开日志文件: {str(e)}')
    
    def _init_cookies_section(self, main_layout):
        """Initialize cookies configuration section"""
        cookies_group = QGroupBox('平台登录 Cookie（按账号已有权限访问）')
        cookies_layout = QVBoxLayout()
        cookies_layout.setContentsMargins(15, 20, 15, 15)
        
        # Create tabs for different platforms
        self.cookies_tabs = QTabWidget()
        
        # Music platform cookies
        self.platform_cookies = {}
        platforms = SOURCES.items()
        
        for platform_key, platform_name in platforms:
            tab = self._create_platform_tab(platform_key, platform_name)
            self.cookies_tabs.addTab(tab, platform_name)
        
        cookies_layout.addWidget(QLabel('下载 Cookie 留空时沿用搜索 Cookie。修改后请重新搜索。'))
        cookies_layout.addWidget(self.cookies_tabs)
        cookies_group.setLayout(cookies_layout)
        main_layout.addWidget(cookies_group)
    
    def _create_platform_tab(self, platform_key, platform_name):
        """
        Create a tab for platform-specific cookies
        
        Args:
            platform_key (str): Platform identifier
            platform_name (str): Display name for platform
            
        Returns:
            QWidget: Tab widget
        """
        tab = QWidget()
        tab_layout = QVBoxLayout()
        tab_layout.setSpacing(8)
        
        # Search cookies
        tab_layout.addWidget(QLabel('搜索 Cookie'))
        search_cookie_edit = QTextEdit()
        search_cookie_edit.setMaximumHeight(80)
        search_cookie_edit.setPlaceholderText('例如: uin=123456; qm_keyst=xxxxx; ...')
        search_cookie_edit.setPlainText(self.current_settings.get('cookies', {}).get(platform_key, {}).get('search', ''))
        tab_layout.addWidget(search_cookie_edit)
        
        # Download cookies
        tab_layout.addWidget(QLabel('下载 Cookie'))
        download_cookie_edit = QTextEdit()
        download_cookie_edit.setMaximumHeight(80)
        download_cookie_edit.setPlaceholderText('留空时沿用搜索 Cookie')
        download_cookie_edit.setPlainText(self.current_settings.get('cookies', {}).get(platform_key, {}).get('download', ''))
        tab_layout.addWidget(download_cookie_edit)
        
        # Copy button
        copy_btn = QPushButton('复制搜索 Cookie 到下载')
        copy_btn.setCursor(Qt.PointingHandCursor)
        copy_btn.clicked.connect(lambda checked, s=search_cookie_edit, d=download_cookie_edit: d.setPlainText(s.toPlainText()))
        tab_layout.addWidget(copy_btn)
        
        tab_layout.addStretch()
        tab.setLayout(tab_layout)
        
        self.platform_cookies[platform_key] = {
            'search': search_cookie_edit,
            'download': download_cookie_edit
        }
        
        return tab
    
    def _init_buttons(self, main_layout):
        """Initialize dialog buttons"""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        self.save_button = QPushButton('保存')
        self.save_button.setObjectName('primaryButton')
        self.save_button.setMinimumWidth(120)
        self.cancel_button = QPushButton('取消')
        self.cancel_button.setMinimumWidth(120)
        self.save_button.setCursor(Qt.PointingHandCursor)
        self.cancel_button.setCursor(Qt.PointingHandCursor)
        self.save_button.clicked.connect(self.save_settings)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        main_layout.addLayout(button_layout)
    
    def select_directory(self):
        """Open directory selection dialog"""
        directory = QFileDialog.getExistingDirectory(self, 'Select Download Directory - 选择下载目录', self.dir_edit.text())
        if directory:
            self.dir_edit.setText(directory)
    
    def save_settings(self):
        """Save settings and close dialog"""
        directory = self.dir_edit.text().strip()
        if not directory:
            QMessageBox.warning(self, '下载目录为空', '请选择下载保存目录。')
            self.dir_edit.setFocus()
            return
        directory = str(Path(directory).expanduser().resolve())
        if Path(directory).exists() and not Path(directory).is_dir():
            QMessageBox.warning(self, '目录无效', '所选路径是文件，请选择文件夹。')
            return
        # Determine directory structure
        if self.flat_radio.isChecked():
            dir_structure = 'flat'
        elif self.source_radio.isChecked():
            dir_structure = 'source'
        else:
            dir_structure = 'date'
        
        self.settings_result = {
            **self.current_settings,
            'work_dir': directory,
            'dir_structure': dir_structure,
            'output_format': self.output_format_combo.currentData(),
            'is_dark': self.dark_theme_radio.isChecked(),
            'cookies': {},
            'search_limit': self.search_limit.value(),
            'search_timeout': self.search_timeout.value(),
        }
        
        for platform_key, edits in self.platform_cookies.items():
            search_cookie = edits['search'].toPlainText().strip()
            download_cookie = edits['download'].toPlainText().strip()
            if search_cookie or download_cookie:
                self.settings_result['cookies'][platform_key] = {
                    'search': search_cookie,
                    'download': download_cookie
                }
        
        self.settings_result = normalize_settings(self.settings_result)
        self.accept()
    
    def get_settings(self):
        """
        Get saved settings
        
        Returns:
            dict: Settings dictionary or None if not saved
        """
        return getattr(self, 'settings_result', None)
