"""Application-owned paths and validated, atomic preference storage."""
import copy
import json
import os
import sys
import tempfile
from pathlib import Path

from PyQt5.QtCore import QStandardPaths


SOURCES = {
    'QQMusicClient': 'QQ 音乐',
    'KuwoMusicClient': '酷我音乐',
    'MiguMusicClient': '咪咕音乐',
    'QianqianMusicClient': '千千音乐',
    'KugouMusicClient': '酷狗音乐',
    'NeteaseMusicClient': '网易云音乐',
}
DEFAULT_SOURCES = ['KuwoMusicClient', 'MiguMusicClient', 'NeteaseMusicClient']


def application_dir():
    return Path(sys.executable if getattr(sys, 'frozen', False) else __file__).resolve().parent


def config_dir():
    return Path(QStandardPaths.writableLocation(QStandardPaths.GenericConfigLocation)) / 'MusicdlGUI'


def data_dir():
    return Path(QStandardPaths.writableLocation(QStandardPaths.GenericDataLocation)) / 'MusicdlGUI'


def default_settings():
    music_dir = QStandardPaths.writableLocation(QStandardPaths.MusicLocation)
    return {
        'work_dir': str(Path(music_dir or str(Path.home() / 'Music')) / 'Musicdl'),
        'dir_structure': 'flat',
        'is_dark': False,
        'cookies': {},
        'quark_cookies': '',
        'selected_sources': list(DEFAULT_SOURCES),
        'search_limit': 5,
        'search_timeout': 60,
    }


def normalize_settings(raw, base_dir=None):
    settings = default_settings()
    if not isinstance(raw, dict):
        raise ValueError('设置文件必须是 JSON 对象')
    path = raw.get('work_dir')
    if isinstance(path, str) and path.strip():
        path = Path(path.strip()).expanduser()
        settings['work_dir'] = str((Path(base_dir or application_dir()) / path).resolve())
    if raw.get('dir_structure') in ('flat', 'source', 'date'):
        settings['dir_structure'] = raw['dir_structure']
    settings['is_dark'] = raw.get('is_dark') is True
    for key, low, high in [('search_limit', 1, 30), ('search_timeout', 15, 180)]:
        value = raw.get(key)
        if type(value) is int:
            settings[key] = min(high, max(low, value))
    if isinstance(raw.get('selected_sources'), list):
        settings['selected_sources'] = [source for source in SOURCES if source in raw['selected_sources']]
    if isinstance(raw.get('cookies'), dict):
        for source, values in raw['cookies'].items():
            if source in SOURCES and isinstance(values, dict):
                settings['cookies'][source] = {
                    key: value.strip() for key in ('search', 'download')
                    if isinstance((value := values.get(key)), str)
                }
    if isinstance(raw.get('quark_cookies'), str):
        settings['quark_cookies'] = raw['quark_cookies'].strip()
    return settings


def load_settings(path=None, legacy_path=None):
    path = Path(path) if path is not None else config_dir() / 'settings.json'
    legacy = Path(legacy_path) if legacy_path is not None else application_dir() / 'settings.json'
    source = path if path.exists() else legacy
    if not source.exists():
        return default_settings(), ''
    try:
        settings = normalize_settings(json.loads(source.read_text(encoding='utf-8')), source.parent)
    except (OSError, ValueError) as error:
        return default_settings(), f'无法读取设置，已使用默认值；原文件保留在 {source}（{type(error).__name__}）'
    if source != path:
        try:
            save_settings(settings, path)
        except OSError:
            return settings, f'已读取原设置，但无法迁移到 {path}，请检查目录权限。'
    return settings, ''


def save_settings(settings, path=None):
    path = Path(path) if path is not None else config_dir() / 'settings.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix='.settings-', suffix='.json', dir=path.parent)
    try:
        with os.fdopen(descriptor, 'w', encoding='utf-8') as stream:
            json.dump(copy.deepcopy(settings), stream, ensure_ascii=False, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
