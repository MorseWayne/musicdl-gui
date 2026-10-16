"""MusicdlGUI desktop application."""
import multiprocessing
import sys
import uuid
from collections import deque
from datetime import datetime
from pathlib import Path

from PyQt5.QtCore import Qt, QTimer, QUrl
from PyQt5.QtGui import QDesktopServices, QIcon
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QLineEdit, QPushButton, QCheckBox, QTableWidget, QTableWidgetItem,
    QProgressBar, QMenu, QMessageBox, QHeaderView, QAbstractItemView,
    QGridLayout, QDialog, QShortcut, QPlainTextEdit,
)

import app_config
from backend import safe_filename, song_filename
from components import SortableTableWidgetItem, size_value, duration_value
from dialogs import SettingsDialog
from logger import setup_logger, log_app_start, log_app_exit, log_info, log_error
from styles import get_stylesheet
from workers import SearchWorker, DownloadWorker


class MusicdlGUI(QWidget):
    STATUS_COLUMN = 8

    def __init__(self):
        super().__init__()
        setup_logger()
        log_app_start()
        self.settings, warning = app_config.load_settings()
        self.is_dark = self.settings['is_dark']
        self.search_worker = None
        self.download_worker = None
        self.music_records = {}
        self.source_states = {}
        self.source_status_labels = {}
        self.failed_sources = set()
        self.failed_downloads = set()
        self.download_queue = deque()
        self.active_record = None
        self.search_keyword = ''
        self._closing = False
        self._search_cancelled = False
        self._download_cancelled = False
        self.setWindowTitle('MusicdlGUI · 音乐搜索与下载')
        icon = Path(__file__).with_name('icon.ico')
        if icon.exists():
            self.setWindowIcon(QIcon(str(icon)))
        self.setMinimumSize(960, 640)
        self.resize(1180, 800)
        self.setStyleSheet(get_stylesheet(self.is_dark))
        self.init_ui()
        if warning:
            self.label_task_info.setText(warning)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)
        header = QHBoxLayout()
        title = QLabel('MusicdlGUI')
        title.setObjectName('appTitle')
        header.addWidget(title)
        header.addWidget(QLabel('搜索音乐，收藏喜欢的声音'))
        header.addStretch()
        self.button_theme = QPushButton('切换主题', clicked=self.toggle_theme)
        self.button_settings = QPushButton('设置', clicked=self.open_settings)
        header.addWidget(self.button_theme)
        header.addWidget(self.button_settings)
        layout.addLayout(header)

        engines = QGroupBox('音乐来源')
        engine_layout = QHBoxLayout(engines)
        self.check_boxes = []
        for source, name in app_config.SOURCES.items():
            checkbox = QCheckBox(name)
            checkbox.setProperty('client_name', source)
            checkbox.setChecked(source in self.settings['selected_sources'])
            checkbox.toggled.connect(self.remember_sources)
            self.check_boxes.append(checkbox)
            engine_layout.addWidget(checkbox)
        layout.addWidget(engines)

        search_row = QHBoxLayout()
        self.lineedit_keyword = QLineEdit()
        self.lineedit_keyword.setPlaceholderText('输入歌名、歌手或专辑，按 Enter 搜索')
        self.lineedit_keyword.setClearButtonEnabled(True)
        self.lineedit_keyword.returnPressed.connect(self.search)
        self.button_keyword = QPushButton('搜索', clicked=self.search)
        self.button_keyword.setObjectName('button_keyword')
        self.button_keyword.setMinimumWidth(110)
        search_row.addWidget(self.lineedit_keyword)
        search_row.addWidget(self.button_keyword)
        layout.addLayout(search_row)
        self.search_summary = QLabel('选择音乐来源，开始第一次搜索。')
        self.search_summary.setWordWrap(True)
        layout.addWidget(self.search_summary)

        self.status_group = QGroupBox('各来源搜索状态')
        self.status_grid = QGridLayout(self.status_group)
        self.status_group.hide()
        layout.addWidget(self.status_group)
        self.search_errors = QPlainTextEdit()
        self.search_errors.setObjectName('errorLabel')
        self.search_errors.setReadOnly(True)
        self.search_errors.setMaximumHeight(112)
        self.search_errors.hide()
        layout.addWidget(self.search_errors)

        actions = QHBoxLayout()
        self.btn_select_all = QPushButton('全选可见结果', clicked=self.select_all_rows)
        self.btn_deselect_all = QPushButton('清空选择', clicked=self.deselect_all_rows)
        self.btn_download_selected = QPushButton('下载选中', clicked=self.download_selected)
        self.btn_download_selected.setObjectName('primaryButton')
        self.btn_retry_search = QPushButton('重试失败来源', clicked=self.retry_search)
        self.btn_retry_search.hide()
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText('筛选当前结果')
        self.filter_edit.setClearButtonEnabled(True)
        self.filter_edit.textChanged.connect(self.filter_results)
        for widget in (self.btn_select_all, self.btn_deselect_all, self.btn_download_selected, self.btn_retry_search):
            actions.addWidget(widget)
        actions.addStretch()
        actions.addWidget(self.filter_edit)
        layout.addLayout(actions)

        self.results_table = QTableWidget(0, 9)
        self.results_table.setHorizontalHeaderLabels(['选择', '歌曲', '歌手', '专辑', '时长', '大小', '格式', '来源', '下载状态'])
        table_header = self.results_table.horizontalHeader()
        table_header.setSectionResizeMode(QHeaderView.ResizeToContents)
        for column in (1, 2, 3):
            table_header.setSectionResizeMode(column, QHeaderView.Stretch)
        table_header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.results_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.results_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.verticalHeader().setVisible(False)
        self.results_table.verticalHeader().setDefaultSectionSize(42)
        self.results_table.setShowGrid(False)
        self.results_table.setSortingEnabled(True)
        self.results_table.sortItems(1, Qt.AscendingOrder)
        self.results_table.itemChanged.connect(self.update_actions)
        self.results_table.itemSelectionChanged.connect(self.update_actions)
        self.results_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.results_table.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.results_table, 1)
        self.results_count = QLabel('暂无结果')
        layout.addWidget(self.results_count)

        self.label_task_info = QLabel('勾选歌曲后点击“下载选中”，也可以右键下载。')
        self.label_task_info.setWordWrap(True)
        self.label_task_info.setTextFormat(Qt.PlainText)
        layout.addWidget(self.label_task_info)
        progress = QHBoxLayout()
        self.bar_download = QProgressBar()
        self.bar_download.setValue(0)
        self.label_progress_detail = QLabel('等待下载')
        self.btn_cancel_download = QPushButton('取消下载', clicked=self.cancel_download)
        self.btn_retry_download = QPushButton('重试失败下载', clicked=self.retry_downloads)
        self.btn_retry_download.hide()
        progress.addWidget(self.bar_download, 1)
        progress.addWidget(self.label_progress_detail)
        progress.addWidget(self.btn_cancel_download)
        progress.addWidget(self.btn_retry_download)
        layout.addLayout(progress)
        footer = QHBoxLayout()
        self.status_label = QLabel()
        self.status_label.setObjectName('mutedLabel')
        self.status_label.setWordWrap(True)
        footer.addWidget(self.status_label, 1)
        footer.addWidget(QPushButton('打开下载目录', clicked=self.open_download_directory))
        layout.addLayout(footer)
        QShortcut('Ctrl+L', self, activated=self.lineedit_keyword.setFocus)
        QShortcut('Escape', self, activated=self.cancel_active)
        self.update_directory_label()
        self.update_actions()
        self.lineedit_keyword.setFocus()

    def persist_settings(self):
        try:
            app_config.save_settings(self.settings)
            return True
        except OSError as error:
            log_error(f'保存设置失败: {error}')
            self.label_task_info.setText(f'无法保存设置：{error}')
            return False

    def remember_sources(self):
        self.settings['selected_sources'] = [box.property('client_name') for box in self.check_boxes if box.isChecked()]
        self.persist_settings()

    def toggle_theme(self):
        self.is_dark = not self.is_dark
        self.settings['is_dark'] = self.is_dark
        self.setStyleSheet(get_stylesheet(self.is_dark))
        self.persist_settings()

    def open_settings(self):
        dialog = SettingsDialog(self, self.settings)
        if dialog.exec_() == QDialog.Accepted:
            self.settings = dialog.get_settings()
            self.is_dark = self.settings['is_dark']
            self.setStyleSheet(get_stylesheet(self.is_dark))
            if self.persist_settings():
                self.label_task_info.setText('设置已保存。Cookie 修改将在下一次搜索时生效。')
            self.update_directory_label()

    def update_directory_label(self):
        structure = {'flat': '平铺', 'source': '按来源', 'date': '按日期和关键词'}[self.settings['dir_structure']]
        self.status_label.setText(f"保存到 {self.settings['work_dir']} · {structure}")

    def open_download_directory(self):
        try:
            path = Path(self.settings['work_dir'])
            path.mkdir(parents=True, exist_ok=True)
            if not QDesktopServices.openUrl(QUrl.fromLocalFile(str(path))):
                raise OSError('系统文件管理器未能打开目录')
        except OSError as error:
            self.label_task_info.setText(f'无法打开目录：{error}')

    def search(self):
        if self.search_worker is not None:
            self.cancel_search()
            return
        if self.download_worker is not None or self._closing:
            return
        keyword = self.lineedit_keyword.text().strip()
        sources = [box.property('client_name') for box in self.check_boxes if box.isChecked()]
        if not keyword or not sources:
            self.search_summary.setText('请输入搜索关键词。' if not keyword else '请至少选择一个音乐来源。')
            self.lineedit_keyword.setFocus()
            return
        self.search_keyword = keyword
        self.results_table.setRowCount(0)
        self.music_records.clear()
        self.failed_downloads.clear()
        self.failed_sources.clear()
        self.source_states.clear()
        self.filter_edit.clear()
        while self.status_grid.count():
            self.status_grid.takeAt(0).widget().deleteLater()
        self.source_status_labels = {}
        for index, source in enumerate(sources):
            label = QLabel()
            label.setTextFormat(Qt.PlainText)
            self.source_status_labels[source] = label
            self.status_grid.addWidget(label, index // 3, index % 3)
        self.status_group.show()
        self.start_search(sources)

    def start_search(self, sources):
        self._search_cancelled = False
        for source in sources:
            self.failed_sources.discard(source)
            self.set_source_status(source, 'pending', '等待搜索')
        self.search_errors.clear()
        self.search_errors.hide()
        self.search_summary.setText(f'正在搜索“{self.search_keyword}”… 可用结果会陆续显示。')
        self.search_worker = SearchWorker(sources, self.search_keyword, self.settings, self)
        self.search_worker.started_sig.connect(self.source_started)
        self.search_worker.result_sig.connect(self.source_result)
        self.search_worker.error_sig.connect(self.source_error)
        self.search_worker.finished.connect(self.search_finished)
        self.search_worker.start()
        self.update_actions()

    def source_started(self, source):
        self.set_source_status(source, 'searching', '搜索中…')

    def set_source_status(self, source, state, message):
        self.source_states[source] = state
        self.source_status_labels[source].setText(f'{app_config.SOURCES[source]} · {message}')

    def source_result(self, source, records, warning):
        message = f'{len(records)} 首' if records else '未找到可下载歌曲'
        self.set_source_status(source, 'success', message + ('（部分失败）' if warning else ''))
        self.source_status_labels[source].setToolTip(warning)
        self.append_results(records)
        self.search_summary.setText(f'已找到 {len(self.music_records)} 首，正在等待其他来源…')
        log_info(f'{source}: {len(records)} 条结果 {warning}')

    def source_error(self, source, message):
        self.failed_sources.add(source)
        self.set_source_status(source, 'error', '搜索失败')
        self.source_status_labels[source].setToolTip(message)
        self.search_errors.appendPlainText(f'{app_config.SOURCES[source]}：{message}')
        self.search_errors.show()
        log_error(f'{source}: {message}')

    def search_finished(self):
        worker, self.search_worker = self.search_worker, None
        worker.deleteLater()
        for source, state in list(self.source_states.items()):
            if state in ('pending', 'searching'):
                self.set_source_status(source, 'cancelled', '已取消')
                self.failed_sources.add(source)
        count = len(self.music_records)
        if self._search_cancelled:
            message = f'搜索已取消，保留 {count} 首可用结果。'
        elif self.failed_sources:
            message = f'找到 {count} 首，{len(self.failed_sources)} 个来源失败。可重试失败来源，或查看下方原因。'
        elif count:
            message = f'找到 {count} 首。勾选后下载，可按列排序或筛选结果。'
        else:
            message = '没有找到可下载歌曲。请换关键词或音乐来源；需要登录的平台可在设置中更新 Cookie。'
        self.search_summary.setText(message)
        self.update_actions()

    def cancel_search(self):
        if self.search_worker is not None:
            self._search_cancelled = True
            self.search_worker.requestInterruption()
            self.button_keyword.setText('正在取消…')
            self.button_keyword.setEnabled(False)

    def retry_search(self):
        if self.search_worker is None and self.download_worker is None and self.failed_sources:
            self.start_search([source for source in self.source_states if source in self.failed_sources])

    def append_results(self, records):
        self.results_table.setSortingEnabled(False)
        self.results_table.blockSignals(True)
        for song in records:
            record_id = uuid.uuid4().hex
            song = dict(song, _keyword=self.search_keyword, _date=datetime.now().strftime('%Y-%m-%d'))
            self.music_records[record_id] = song
            row = self.results_table.rowCount()
            self.results_table.insertRow(row)
            checkbox = QTableWidgetItem()
            checkbox.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            checkbox.setCheckState(Qt.Unchecked)
            checkbox.setData(Qt.UserRole, record_id)
            self.results_table.setItem(row, 0, checkbox)
            values = [
                (song['song_name'], song['song_name']), (song['singers'], song['singers']),
                (song['album'], song['album']), (song['duration'], duration_value(song['duration'])),
                (song['file_size'], size_value(song['file_size'])),
                (song['ext'].upper(), song['ext']), (app_config.SOURCES[song['source']], song['source']),
                ('未下载', '未下载'),
            ]
            for column, (text, sort_value) in enumerate(values, 1):
                item = SortableTableWidgetItem(text, sort_value)
                item.setToolTip(text)
                self.results_table.setItem(row, column, item)
        self.results_table.blockSignals(False)
        self.results_table.setSortingEnabled(True)
        self.filter_results()

    def filter_results(self):
        keyword = self.filter_edit.text().strip().casefold()
        visible = 0
        for row in range(self.results_table.rowCount()):
            text = ' '.join(self.results_table.item(row, column).text() for column in (1, 2, 3, 7)).casefold()
            hidden = keyword not in text
            self.results_table.setRowHidden(row, hidden)
            visible += not hidden
        self.results_count.setText(f'{len(self.music_records)} 首结果 · 当前显示 {visible} 首')
        self.update_actions()

    def selected_ids(self):
        checked = []
        for row in range(self.results_table.rowCount()):
            item = self.results_table.item(row, 0)
            if item and item.checkState() == Qt.Checked:
                checked.append(item.data(Qt.UserRole))
        if checked:
            return checked
        return [self.results_table.item(index.row(), 0).data(Qt.UserRole)
                for index in self.results_table.selectionModel().selectedRows()
                if not self.results_table.isRowHidden(index.row())]

    def update_actions(self):
        searching = self.search_worker is not None
        downloading = self.download_worker is not None
        selected = self.selected_ids()
        self.btn_download_selected.setText(f'下载选中（{len(selected)}）' if selected else '下载选中')
        self.btn_download_selected.setEnabled(bool(selected) and not downloading)
        self.btn_select_all.setEnabled(bool(self.music_records))
        self.btn_deselect_all.setEnabled(bool(self.music_records))
        self.btn_retry_search.setVisible(bool(self.failed_sources))
        self.btn_retry_search.setEnabled(not searching and not downloading)
        self.btn_retry_download.setVisible(bool(self.failed_downloads))
        self.btn_retry_download.setEnabled(not downloading)
        self.btn_cancel_download.setEnabled(downloading and not self._download_cancelled)
        self.button_settings.setEnabled(not searching and not downloading)
        self.button_keyword.setText('取消搜索' if searching else '搜索')
        self.button_keyword.setEnabled((not downloading or searching) and not (searching and self._search_cancelled))
        self.lineedit_keyword.setEnabled(not searching and not downloading)
        for box in self.check_boxes:
            box.setEnabled(not searching and not downloading)

    def select_all_rows(self):
        self.results_table.blockSignals(True)
        for row in range(self.results_table.rowCount()):
            if not self.results_table.isRowHidden(row):
                self.results_table.item(row, 0).setCheckState(Qt.Checked)
        self.results_table.blockSignals(False)
        self.update_actions()

    def deselect_all_rows(self):
        self.results_table.blockSignals(True)
        for row in range(self.results_table.rowCount()):
            self.results_table.item(row, 0).setCheckState(Qt.Unchecked)
        self.results_table.clearSelection()
        self.results_table.blockSignals(False)
        self.update_actions()

    def show_context_menu(self, position):
        item = self.results_table.itemAt(position)
        if item is None:
            return
        record_id = self.results_table.item(item.row(), 0).data(Qt.UserRole)
        menu = QMenu(self)
        action = menu.addAction('下载这首歌曲')
        action.setEnabled(self.download_worker is None)
        if menu.exec_(self.results_table.viewport().mapToGlobal(position)) == action:
            self.start_downloads([record_id])

    def download_selected(self):
        self.start_downloads(self.selected_ids())

    def retry_downloads(self):
        self.start_downloads([key for key in self.music_records if key in self.failed_downloads])

    def set_download_status(self, record_id, status, detail=''):
        for row in range(self.results_table.rowCount()):
            if self.results_table.item(row, 0).data(Qt.UserRole) == record_id:
                item = self.results_table.item(row, self.STATUS_COLUMN)
                # Update tooltip before text because sorting can move the row.
                item.setToolTip(detail or status)
                item.sort_value = status
                item.setText(status)
                break

    def start_downloads(self, record_ids):
        if self.download_worker is not None or not record_ids or self._closing:
            return
        self.download_queue = deque(record_ids)
        self.batch_total = len(record_ids)
        self.batch_completed = self.batch_success = 0
        self.batch_errors = []
        self._download_cancelled = False
        for record_id in record_ids:
            self.failed_downloads.discard(record_id)
            self.set_download_status(record_id, '等待下载')
        self.start_next_download()

    def start_next_download(self):
        self.active_record = self.download_queue.popleft()
        song = self.music_records[self.active_record]
        directory = Path(self.settings['work_dir'])
        if self.settings['dir_structure'] != 'flat':
            directory /= safe_filename(song['source'])
        if self.settings['dir_structure'] == 'date':
            directory /= safe_filename(f"{song['_date']} {song['_keyword']}")
        self._download_result = (False, '下载进程未返回结果', '')
        self.set_download_status(self.active_record, '下载中')
        self.label_task_info.setText(f"正在下载 {self.batch_completed + 1}/{self.batch_total}：{song['song_name']} · {song['singers']}")
        self.bar_download.setRange(0, 0)
        self.label_progress_detail.setText('正在连接…')
        self.download_worker = DownloadWorker(song, str(directory), song_filename(song), self)
        self.download_worker.progress_sig.connect(self.download_progress)
        self.download_worker.result_sig.connect(self.download_result)
        self.download_worker.finished.connect(self.download_finished)
        self.download_worker.start()
        self.update_actions()

    def download_progress(self, percent, detail):
        self.bar_download.setRange(0, 0 if percent < 0 else 100)
        if percent >= 0:
            self.bar_download.setValue(percent)
        self.label_progress_detail.setText(detail)

    def download_result(self, success, message, path):
        self._download_result = success, message, path

    def download_finished(self):
        # Advance the queue only after QThread.finished, never from result_sig.
        worker, self.download_worker = self.download_worker, None
        worker.deleteLater()
        success, message, path = self._download_result
        self.batch_completed += 1
        song = self.music_records[self.active_record]
        if success:
            self.batch_success += 1
            self.set_download_status(self.active_record, '已下载', path)
            log_info(f"下载完成: {song['song_name']} -> {path}")
        elif self._download_cancelled:
            self.set_download_status(self.active_record, '已取消')
        else:
            self.failed_downloads.add(self.active_record)
            self.batch_errors.append(f"{song['song_name']}：{message}")
            self.set_download_status(self.active_record, '失败 · 可重试', message)
            log_error(f"下载失败: {song['song_name']}: {message}")
        self.active_record = None
        if self.download_queue and not self._closing and not self._download_cancelled:
            self.start_next_download()
            return
        self.bar_download.setRange(0, 100)
        self.bar_download.setValue(100 if self.batch_success == self.batch_total else 0)
        self.label_progress_detail.setText(f'成功 {self.batch_success}/{self.batch_total}')
        message = ('下载已取消' if self._download_cancelled else '下载完成') + f' · 成功 {self.batch_success}/{self.batch_total} 首'
        if self.batch_errors:
            message += '\n' + '\n'.join(self.batch_errors[:3])
            if len(self.batch_errors) > 3:
                message += '\n其余失败原因可在“下载状态”列悬停查看。'
        elif success:
            message += f' · {path}'
        self.label_task_info.setText(message)
        self.update_actions()

    def cancel_download(self):
        if self.download_worker is not None:
            self._download_cancelled = True
            for record_id in self.download_queue:
                self.set_download_status(record_id, '已取消')
            self.download_queue.clear()
            self.download_worker.requestInterruption()
            self.label_task_info.setText('正在取消下载并清理临时文件…')
            self.update_actions()

    def cancel_active(self):
        self.cancel_search()
        self.cancel_download()

    def closeEvent(self, event):
        if self.search_worker is not None or self.download_worker is not None:
            event.ignore()
            if not self._closing:
                self._closing = True
                self.cancel_active()
                self.setEnabled(False)
            QTimer.singleShot(100, self.close)
            return
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName('MusicdlGUI')
    app.setOrganizationName('MusicdlGUI')
    window = MusicdlGUI()
    if len(sys.argv) == 3 and sys.argv[1] == '--smoke-test':
        from release_smoke import run_smoke_test
        return run_smoke_test(app, window, sys.argv[2])
    window.show()
    exit_code = app.exec_()
    log_app_exit()
    return exit_code


if __name__ == '__main__':
    multiprocessing.freeze_support()
    sys.exit(main())
