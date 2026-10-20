import ast
import re
from pathlib import Path
from string import Formatter

import pytest
import requests
from PyQt5.QtWidgets import QDialog, QLabel

import app_config
import musicdlgui
from backend import safe_error
from dialogs import SettingsDialog
from i18n import ENGLISH, Translator, language_context, translate


def test_catalog_preserves_format_fields_and_covers_application_messages():
    def fields(text):
        return {field for _, field, _, _ in Formatter().parse(text) if field is not None}
    for source, english in ENGLISH.items():
        assert fields(source) == fields(english), source
        assert not re.search(r'[\u4e00-\u9fff]', english), source
    root = Path(__file__).resolve().parents[1]
    for filename in ('musicdlgui.py', 'dialogs.py', 'backend.py', 'audio_conversion.py', 'workers.py', 'app_config.py'):
        tree = ast.parse((root / filename).read_text(encoding='utf-8'))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            name = ast.unparse(node.func)
            if name in ('tr', 'translate', 'Text', 'self.i18n'):
                key = node.args[0] if node.args else None
            elif name == 'self.i18n.bind':
                key = node.args[1] if len(node.args) > 1 else None
            else:
                continue
            if isinstance(key, ast.Constant) and isinstance(key.value, str) and re.search(r'[\u4e00-\u9fff]', key.value):
                assert key.value in ENGLISH, (filename, key.value)


def test_live_bindings_handle_deleted_qt_objects(app):
    translator = Translator()
    label = translator.bind(QLabel(), '搜索')
    # Search labels and table rows can be deleted before a later language change.
    from PyQt5 import sip
    sip.delete(label)
    translator.set_language('en_US')
    live = translator.bind(QLabel(), '搜索')
    assert live.text() == 'Search'


@pytest.mark.parametrize('language', ['zh_CN', 'en_US'])
def test_network_errors_remain_localized_and_redacted(language):
    with language_context(language):
        timeout = safe_error(requests.exceptions.Timeout())
        secret = safe_error(RuntimeError('bad https://example.test/?token=private Cookie=secret'))
    assert 'private' not in secret and 'secret' not in secret
    assert ('timed out' in timeout) == (language == 'en_US')
    assert translate('搜索') == '搜索'  # Task contexts must not change the UI default.


def test_language_preview_cancel_and_save_apply_without_restart(app, monkeypatch, tmp_path):
    config = tmp_path / 'config'
    monkeypatch.setattr(app_config, 'config_dir', lambda: config)
    monkeypatch.setattr(app_config, 'data_dir', lambda: tmp_path / 'data')
    window = musicdlgui.MusicdlGUI()
    dialog = SettingsDialog(window, window.settings)
    dialog.language_combo.setCurrentIndex(dialog.language_combo.findData('en_US'))
    assert dialog.save_button.text() == 'Save'
    assert dialog.cookies_tabs.tabText(0) == 'QQ Music'
    assert dialog.output_format_combo.itemText(0) == 'Keep original'
    dialog.reject()
    assert window.settings['language'] == 'zh_CN'
    assert window.button_keyword.text() == '搜索'

    def accept_english(dialog):
        dialog.language_combo.setCurrentIndex(dialog.language_combo.findData('en_US'))
        dialog.output_format_combo.setCurrentIndex(dialog.output_format_combo.findData('wav'))
        dialog.search_limit.setValue(8)
        dialog.save_settings()
        return QDialog.Accepted
    monkeypatch.setattr(SettingsDialog, 'exec_', accept_english)
    window.open_settings()
    assert window.button_keyword.text() == 'Search'
    assert window.button_settings.text() == 'Settings'
    assert window.results_table.horizontalHeaderItem(8).text() == 'Download status'
    assert window.settings['search_limit'] == 8
    assert window.output_format_combo.currentData() == 'wav'
    assert 'Settings saved' in window.label_task_info.text()
    window.close()

    reopened = musicdlgui.MusicdlGUI()
    assert reopened.settings['language'] == 'en_US'
    assert reopened.button_keyword.text() == 'Search'
    assert reopened.output_format_combo.currentData() == 'wav'
    reopened.close()
