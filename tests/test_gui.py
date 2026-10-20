from PyQt5.QtCore import QObject, Qt, pyqtSignal
from pathlib import Path
import pytest

import app_config
import musicdlgui
from backend import normalize_song
from components import size_value, duration_value
from dialogs import SettingsDialog


class FakeSearch(QObject):
    started_sig = pyqtSignal(str)
    result_sig = pyqtSignal(str, list, str)
    error_sig = pyqtSignal(str, str)
    finished = pyqtSignal()

    def __init__(self, *args):
        super().__init__()
        self.cancelled = False

    def start(self):
        pass

    def requestInterruption(self):
        self.cancelled = True


@pytest.fixture
def window(app, monkeypatch, tmp_path):
    settings = dict(app_config.default_settings(), work_dir=str(tmp_path / 'downloads'))
    settings['selected_sources'] = ['QQMusicClient', 'KuwoMusicClient', 'MiguMusicClient']
    monkeypatch.setattr(app_config, 'load_settings', lambda: (settings, ''))
    monkeypatch.setattr(app_config, 'save_settings', lambda *args: None)
    monkeypatch.setattr(musicdlgui, 'SearchWorker', FakeSearch)
    window = musicdlgui.MusicdlGUI()
    yield window
    if window.search_worker is not None:
        window.search_worker.finished.emit()
    window.close()


def song(name, **kwargs):
    return normalize_song(dict(song_name=name, singers='歌手', download_url='https://example.test/audio', **kwargs), 'QQMusicClient')


def test_incremental_results_keep_selection_and_row_identity(window):
    window.lineedit_keyword.setText('test')
    window.search()
    worker = window.search_worker
    worker.result_sig.emit('QQMusicClient', [song('Z')], '')
    window.results_table.item(0, 0).setCheckState(Qt.Checked)
    selected = window.selected_ids()
    worker.result_sig.emit('MiguMusicClient', [song('A')], '')
    assert window.results_table.rowCount() == 2
    assert window.selected_ids() == selected
    assert window.music_records[selected[0]]['song_name'] == 'Z'
    assert window.btn_download_selected.isEnabled()


def test_error_is_visible_and_not_reported_as_empty_success(window):
    window.lineedit_keyword.setText('test')
    window.search()
    window.search_worker.error_sig.emit('QQMusicClient', 'HTTP 403')
    window.search_worker.finished.emit()
    assert 'HTTP 403' in window.search_errors.toPlainText()
    assert '失败' in window.search_summary.text()
    assert not window.btn_retry_search.isHidden()
    assert window.button_keyword.isEnabled()


def test_retry_keeps_successful_results(window):
    window.lineedit_keyword.setText('test')
    window.search()
    window.search_worker.result_sig.emit('QQMusicClient', [song('kept')], '')
    window.search_worker.error_sig.emit('KuwoMusicClient', 'timeout')
    window.search_worker.result_sig.emit('MiguMusicClient', [], '')
    window.search_worker.finished.emit()
    original = set(window.music_records)
    window.retry_search()
    assert set(window.music_records) == original
    assert window.source_states['QQMusicClient'] == 'success'
    assert window.source_states['KuwoMusicClient'] == 'pending'


def test_filter_selects_only_visible_rows(window):
    window.append_results([song('Visible'), song('Hidden')])
    window.filter_edit.setText('Visible')
    window.select_all_rows()
    assert [window.music_records[key]['song_name'] for key in window.selected_ids()] == ['Visible']
    window.deselect_all_rows()
    assert not window.selected_ids()


def test_batch_advances_after_finished_and_preserves_success_count(window, wait_until):
    window.append_results([song('A', downloaded_contents=b'ID3a'), song('B', downloaded_contents=b'ID3b')])
    window.start_downloads(list(window.music_records))
    wait_until(lambda: window.download_worker is None)
    assert window.batch_completed == window.batch_success == 2
    assert '成功 2/2' in window.label_task_info.text()
    # A later single download must not reuse the previous batch counters.
    window.start_downloads([next(iter(window.music_records))])
    wait_until(lambda: window.download_worker is None)
    assert window.batch_completed == window.batch_success == window.batch_total == 1


def test_batch_continues_after_failure_and_retry_uses_only_failed_records(window, wait_until):
    bad = song('Failed')
    bad['download_url'] = None
    window.append_results([bad, song('Good', downloaded_contents=b'ID3audio')])
    window.start_downloads(list(window.music_records))
    wait_until(lambda: window.download_worker is None)
    assert window.batch_completed == 2 and window.batch_success == 1
    assert len(window.failed_downloads) == 1
    failed_id = next(iter(window.failed_downloads))
    window.music_records[failed_id]['downloaded_contents'] = b'ID3retry'
    window.retry_downloads()
    wait_until(lambda: window.download_worker is None)
    assert window.batch_total == window.batch_success == 1
    assert not window.failed_downloads


def test_close_cancels_before_destroying_worker(window, app):
    window.show()
    window.lineedit_keyword.setText('test')
    window.search()
    worker = window.search_worker
    window.close()
    assert worker.cancelled and window.isVisible()
    worker.finished.emit()
    window.close()
    assert not window.isVisible()


def test_settings_preserve_source_preferences(window):
    dialog = SettingsDialog(window, window.settings)
    dialog.search_limit.setValue(8)
    dialog.output_format_combo.setCurrentIndex(dialog.output_format_combo.findData('wav'))
    dialog.save_settings()
    assert dialog.get_settings()['selected_sources'] == window.settings['selected_sources']
    assert dialog.get_settings()['search_limit'] == 8
    assert dialog.get_settings()['output_format'] == 'wav'


def test_batch_output_format_from_main_window_is_applied_and_locked(window, wait_until, flac_audio):
    window.output_format_combo.setCurrentIndex(window.output_format_combo.findData('mp3'))
    assert window.settings['output_format'] == 'mp3'
    window.append_results([song('A', downloaded_contents=flac_audio[0], ext='flac'),
                           song('B', downloaded_contents=flac_audio[0], ext='flac')])
    window.start_downloads(list(window.music_records))
    assert not window.output_format_combo.isEnabled()
    wait_until(lambda: window.download_worker is None)
    assert window.batch_success == 2
    assert window.output_format_combo.isEnabled()
    files = list(Path(window.settings['work_dir']).iterdir())
    assert len(files) == 2 and all(path.suffix == '.mp3' for path in files)


def test_numeric_sorting():
    assert size_value('10MB') > size_value('999 KB')
    assert size_value('1.5 GiB') == 1.5 * 1024 ** 3
    assert duration_value('01:02:03') == 3723
    assert duration_value(None) == size_value(None) == 0


def test_switching_language_preserves_results_filter_selection_and_status(window):
    window.append_results([song('中文歌名'), song('Another song')])
    record_id = next(iter(window.music_records))
    window.results_table.item(1, 0).setCheckState(Qt.Checked)
    window.set_download_status(record_id, '已下载', '/music/song.mp3')
    window.filter_edit.setText('中文')
    selected = window.selected_ids()
    window.settings['language'] = 'en_US'
    window.apply_language()
    assert window.selected_ids() == selected
    assert window.results_table.rowCount() == 2
    assert window.filter_edit.text() == '中文'
    assert window.music_records[record_id]['song_name'] == '中文歌名'
    assert 'Results: 2' in window.results_count.text()
    assert window.results_table.item(1, 8).text() == 'Downloaded'
    assert window.results_table.item(1, 7).text() == 'QQ Music'
    assert 'QQ Music' in [box.text() for box in window.check_boxes]
    window.settings['language'] = 'zh_CN'
    window.apply_language()
    assert window.results_table.item(1, 8).text() == '已下载'
    assert window.selected_ids() == selected


def test_english_search_states_and_download_completion(window, wait_until):
    window.settings['language'] = 'en_US'
    window.apply_language()
    window.lineedit_keyword.setText('music')
    window.search()
    worker = window.search_worker
    worker.result_sig.emit('QQMusicClient', [song('Track', downloaded_contents=b'ID3audio')], '')
    worker.error_sig.emit('KuwoMusicClient', 'HTTP 403')
    worker.result_sig.emit('MiguMusicClient', [], '')
    worker.finished.emit()
    assert 'failed sources: 1' in window.search_summary.text()
    assert 'QQ Music · Tracks: 1' in window.source_status_labels['QQMusicClient'].text()
    assert 'Kuwo Music: HTTP 403' in window.search_errors.toPlainText()
    window.start_downloads(list(window.music_records))
    wait_until(lambda: window.download_worker is None)
    assert window.label_progress_detail.text() == 'Succeeded 1/1'
    assert window.results_table.item(0, 8).text() == 'Downloaded'
    window.settings['language'] = 'zh_CN'
    window.apply_language()
    assert window.label_progress_detail.text() == '成功 1/1'
    assert '下载完成' in window.label_task_info.text()
