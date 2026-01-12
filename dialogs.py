'''
Function:
    Dialogs for MusicdlGUI
Author:
    Zhenchao Jin
WeChat Official Account (微信公众号):
    Charles的皮卡丘
'''
import os
import subprocess
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, 
                             QLabel, QLineEdit, QPushButton, QRadioButton, 
                             QButtonGroup, QTextEdit, QTabWidget, QWidget, 
                             QFileDialog, QMessageBox)
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
        self.setWindowTitle('Settings - 设置')
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        self.current_settings = current_settings or {}
        self.init_ui()
    
    def init_ui(self):
        """Initialize user interface"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Appearance section
        self._init_appearance_section(main_layout)
        
        # Download directory section
        self._init_directory_section(main_layout)
        
        # Log section
        self._init_log_section(main_layout)
        
        # Cookies configuration section
        self._init_cookies_section(main_layout)
        
        # Buttons
        self._init_buttons(main_layout)
        
        self.setLayout(main_layout)
    
    def _init_appearance_section(self, main_layout):
        """Initialize appearance settings section"""
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
    
    def _init_directory_section(self, main_layout):
        """Initialize download directory settings section"""
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
    
    def _init_log_section(self, main_layout):
        """Initialize log settings section"""
        log_group = QGroupBox('Log - 日志')
        log_layout = QVBoxLayout()
        log_layout.setContentsMargins(15, 20, 15, 15)
        log_layout.setSpacing(10)
        
        # Log file info
        log_file = get_log_file_path()
        if log_file:
            log_info_label = QLabel(f'当前日志文件: {os.path.basename(log_file)}')
        else:
            log_info_label = QLabel('日志文件: 尚未初始化')
        log_info_label.setStyleSheet("color: #666666; font-size: 11px;")
        log_layout.addWidget(log_info_label)
        
        # Log directory info
        log_dir = get_log_directory()
        log_dir_label = QLabel(f'日志目录: {log_dir}')
        log_dir_label.setStyleSheet("color: #666666; font-size: 11px;")
        log_dir_label.setWordWrap(True)
        log_layout.addWidget(log_dir_label)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        open_log_dir_btn = QPushButton('Open Log Folder - 打开日志目录')
        open_log_dir_btn.setCursor(Qt.PointingHandCursor)
        open_log_dir_btn.clicked.connect(self.open_log_directory)
        btn_layout.addWidget(open_log_dir_btn)
        
        open_log_file_btn = QPushButton('Open Current Log - 打开当前日志')
        open_log_file_btn.setCursor(Qt.PointingHandCursor)
        open_log_file_btn.clicked.connect(self.open_log_file)
        btn_layout.addWidget(open_log_file_btn)
        
        btn_layout.addStretch()
        log_layout.addLayout(btn_layout)
        
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)
    
    def open_log_directory(self):
        """Open log directory in file explorer"""
        log_dir = get_log_directory()
        try:
            if sys.platform == 'win32':
                os.startfile(log_dir)
            elif sys.platform == 'darwin':
                subprocess.run(['open', log_dir])
            else:
                subprocess.run(['xdg-open', log_dir])
        except Exception as e:
            QMessageBox.warning(self, 'Warning - 警告', f'无法打开日志目录: {str(e)}')
    
    def open_log_file(self):
        """Open current log file"""
        log_file = get_log_file_path()
        if not log_file or not os.path.exists(log_file):
            QMessageBox.information(self, 'Info - 信息', '日志文件尚未创建')
            return
        try:
            if sys.platform == 'win32':
                os.startfile(log_file)
            elif sys.platform == 'darwin':
                subprocess.run(['open', log_file])
            else:
                subprocess.run(['xdg-open', log_file])
        except Exception as e:
            QMessageBox.warning(self, 'Warning - 警告', f'无法打开日志文件: {str(e)}')
    
    def _init_cookies_section(self, main_layout):
        """Initialize cookies configuration section"""
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
            tab = self._create_platform_tab(platform_key, platform_name)
            self.cookies_tabs.addTab(tab, platform_name)
        
        # Quark cookies tab
        quark_tab = self._create_quark_tab()
        self.cookies_tabs.addTab(quark_tab, '夸克网盘')
        
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
        
        self.platform_cookies[platform_key] = {
            'search': search_cookie_edit,
            'download': download_cookie_edit
        }
        
        return tab
    
    def _create_quark_tab(self):
        """
        Create tab for Quark cloud storage cookies
        
        Returns:
            QWidget: Tab widget
        """
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
        return quark_tab
    
    def _init_buttons(self, main_layout):
        """Initialize dialog buttons"""
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
    
    def select_directory(self):
        """Open directory selection dialog"""
        directory = QFileDialog.getExistingDirectory(self, 'Select Download Directory - 选择下载目录', self.dir_edit.text())
        if directory:
            self.dir_edit.setText(directory)
    
    def save_settings(self):
        """Save settings and close dialog"""
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
        """
        Get saved settings
        
        Returns:
            dict: Settings dictionary or None if not saved
        """
        return getattr(self, 'settings_result', None)
