import json

import pytest

import app_config


def test_legacy_settings_migrate_and_resolve_relative_downloads(tmp_path):
    legacy = tmp_path / 'old' / 'settings.json'
    legacy.parent.mkdir()
    legacy.write_text(json.dumps({'work_dir': 'downloads', 'is_dark': True, 'cookies': {'QQMusicClient': {'search': 'secret'}}}))
    target = tmp_path / 'config' / 'settings.json'
    settings, warning = app_config.load_settings(target, legacy)
    assert not warning
    assert settings['work_dir'] == str(legacy.parent / 'downloads')
    assert settings['is_dark']
    assert settings['cookies']['QQMusicClient']['search'] == 'secret'
    assert target.exists() and legacy.exists()
    assert app_config.load_settings(target, legacy)[0] == settings


@pytest.mark.parametrize('contents', ['broken', '[]', 'null'])
def test_corrupt_preferences_are_preserved(tmp_path, contents):
    path = tmp_path / 'settings.json'
    path.write_text(contents)
    settings, warning = app_config.load_settings(path)
    assert warning
    assert settings == app_config.default_settings()
    assert path.read_text() == contents


def test_validation_prevents_invalid_types_from_breaking_ui():
    settings = app_config.normalize_settings({'cookies': ['bad'], 'work_dir': None, 'selected_sources': ['Unknown'],
                                               'search_limit': -1, 'search_timeout': 999, 'is_dark': 'false'})
    assert settings['cookies'] == {}
    assert settings['selected_sources'] == []
    assert settings['search_limit'] == 1 and settings['search_timeout'] == 180
    assert settings['is_dark'] is False


def test_failed_atomic_save_keeps_existing_settings(monkeypatch, tmp_path):
    path = tmp_path / 'settings.json'
    path.write_text('{"original":true}')
    def fail(*args):
        raise OSError('disk full')
    monkeypatch.setattr(app_config.os, 'replace', fail)
    with pytest.raises(OSError):
        app_config.save_settings(app_config.default_settings(), path)
    assert path.read_text() == '{"original":true}'
    assert list(tmp_path.iterdir()) == [path]


def test_failed_migration_still_uses_legacy_preferences(monkeypatch, tmp_path):
    legacy = tmp_path / 'legacy.json'
    legacy.write_text('{"is_dark":true}')
    def fail(*args):
        raise OSError('read only')
    monkeypatch.setattr(app_config, 'save_settings', fail)
    settings, warning = app_config.load_settings(tmp_path / 'new.json', legacy)
    assert settings['is_dark'] and '迁移' in warning
