from pathlib import Path
from types import SimpleNamespace

import pytest
import requests

import backend
from backend import BackendError, download_song, normalize_song, publish_download, safe_filename, song_filename


class Response:
    def __init__(self, content=b'ID3audio', headers=None, status=200):
        self.content = content
        self.headers = headers if headers is not None else {'Content-Length': str(len(content))}
        self.status_code = status

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(response=self)

    def iter_content(self, chunk_size):
        yield self.content


def test_real_songinfo_optional_fields_and_download_auth():
    from musicdl.modules import SongInfo
    song = SongInfo(song_name='测试', singers=['甲', '乙'], download_url='https://example.test/audio',
                    default_download_headers={'Referer': 'track'}, default_download_cookies={'song': 'cookie'})
    record = normalize_song(song, 'QQMusicClient', {'Referer': 'source'}, {'source': 'cookie'})
    assert record['singers'] == '甲 / 乙'
    assert record['duration'] == record['file_size'] == record['album'] == '—'
    assert record['default_download_headers'] == {'Referer': 'track'}
    assert record['default_download_cookies'] == {'song': 'cookie'}
    assert record['ext'] == 'mp3'


def test_legacy_dictionary_gets_provider_auth():
    record = normalize_song({'song_name': 'Song'}, 'MiguMusicClient', {'Referer': 'provider'}, {'login': 'yes'})
    assert record['default_download_headers']['Referer'] == 'provider'
    assert record['default_download_cookies']['login'] == 'yes'


def test_search_reports_swallowed_provider_error(monkeypatch, tmp_path):
    import musicdl.modules

    def build(module_cfg):
        def search(**kwargs):
            module_cfg['logger_handle'].error('HTTP 403 at https://example.test/?token=private')
            return []
        return SimpleNamespace(search=search, default_download_headers={}, default_download_cookies={})

    monkeypatch.setattr(musicdl.modules, 'BuildMusicClient', build)
    with pytest.raises(BackendError, match='403') as error:
        backend.search_source('QQMusicClient', 'test', {}, tmp_path)
    assert 'private' not in str(error.value)


def test_search_keeps_partial_results(monkeypatch, tmp_path):
    import musicdl.modules

    def build(module_cfg):
        assert module_cfg['default_download_cookies'] == 'session=valid'
        def search(**kwargs):
            module_cfg['logger_handle'].error('one page failed')
            return [{'song_name': 'Song', 'download_url': 'https://example.test/audio'}]
        return SimpleNamespace(search=search, default_download_headers={}, default_download_cookies={})

    monkeypatch.setattr(musicdl.modules, 'BuildMusicClient', build)
    songs, warning = backend.search_source('QQMusicClient', 'test', {'cookies': {'QQMusicClient': {'search': 'session=valid'}}}, tmp_path)
    assert len(songs) == 1 and warning


def test_real_builder_does_not_lose_provider_errors_when_copying_config(monkeypatch, tmp_path):
    from musicdl.modules.sources.migu import MiguMusicClient

    def search(self, **kwargs):
        self.logger_handle.error('platform HTTP 503')
        return []

    monkeypatch.setattr(MiguMusicClient, 'search', search)
    with pytest.raises(BackendError, match='503'):
        backend.search_source('MiguMusicClient', 'test', {}, tmp_path)


def test_download_uses_auth_and_tls_verification(monkeypatch, tmp_path):
    calls = []
    def get(url, **kwargs):
        calls.append(kwargs)
        return Response()
    monkeypatch.setattr(backend.requests, 'get', get)
    song = {'download_url': 'https://example.test/audio', 'default_download_headers': {'Referer': 'track'},
            'default_download_cookies': {'login': 'valid'}}
    progress = []
    target = tmp_path / 'audio.part'
    download_song(song, target, lambda *args: progress.append(args))
    assert target.read_bytes() == b'ID3audio'
    assert calls[0]['headers']['Referer'] == 'track'
    assert calls[0]['cookies']['login'] == 'valid'
    assert calls[0].get('verify', True) is True
    assert progress[-1][0] == 100


@pytest.mark.parametrize('response,match', [
    (Response(b'<html>expired</html>', {'Content-Type': 'text/html'}), '网页'),
    (Response(b'{"error":"expired"}'), '错误页面'),
    (Response(b'', {}), '为空'),
    (Response(b'ID3short', {'Content-Length': '100'}), '不完整'),
    (Response(status=206), '不完整'),
    (Response(status=403), None),
])
def test_download_rejects_invalid_response(monkeypatch, tmp_path, response, match):
    monkeypatch.setattr(backend.requests, 'get', lambda *args, **kwargs: response)
    with pytest.raises((BackendError, requests.HTTPError), match=match):
        download_song({'download_url': 'https://example.test/audio'}, tmp_path / 'audio.part', lambda *args: None)


def test_unknown_length_progress_is_indeterminate(monkeypatch, tmp_path):
    monkeypatch.setattr(backend.requests, 'get', lambda *args, **kwargs: Response(headers={}))
    progress = []
    download_song({'download_url': 'https://example.test/audio'}, tmp_path / 'audio.part', lambda *args: progress.append(args))
    assert progress[0][0] == -1 and progress[-1][0] == 100


def test_publish_never_overwrites_existing_music(tmp_path):
    existing = tmp_path / 'song.mp3'
    existing.write_bytes(b'original')
    stage = tmp_path / 'download.part'
    stage.write_bytes(b'complete')
    published = publish_download(stage, tmp_path, 'song.mp3')
    assert Path(published).name == 'song (1).mp3'
    assert Path(published).read_bytes() == b'complete'
    assert existing.read_bytes() == b'original'
    assert not stage.exists()


@pytest.mark.parametrize('name', ['../../escape', 'a/b\\c:*?', 'NUL', 'CON.mp3', ' . ', '歌' * 200])
def test_filename_stays_in_download_directory(name):
    result = safe_filename(name)
    assert result not in ('.', '..', '')
    assert not any(character in result for character in '/\\:*?')
    assert len(result.encode()) <= 171
    assert result.split('.')[0].upper() not in ('NUL', 'CON')


def test_extension_cannot_escape_directory():
    assert song_filename({'song_name': '测试/歌曲', 'singers': '歌手', 'ext': '../../bad'}).endswith('.mp3')
