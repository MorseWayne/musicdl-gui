"""musicdl adapter and file transfers, independent of the Qt UI.

Provider code runs in owned child processes so deadlines cover nested requests.
Only plain records cross the process boundary.
"""
import os
import re
import time
from pathlib import Path
from urllib.parse import urlsplit

import requests
from audio_conversion import OUTPUT_FORMATS, convert_audio


class BackendError(Exception):
    pass


def safe_error(error):
    """Keep credentials and signed URLs out of the UI and application logs."""
    if isinstance(error, requests.exceptions.ProxyError):
        return '无法连接代理，请检查系统代理设置'
    if isinstance(error, requests.exceptions.SSLError):
        return 'HTTPS 证书验证失败，请检查系统时间、证书或代理'
    if isinstance(error, requests.exceptions.Timeout):
        return '网络请求超时，请重试或切换音乐源'
    if isinstance(error, requests.exceptions.ConnectionError):
        return '网络连接失败，请检查网络或切换音乐源'
    if isinstance(error, requests.exceptions.HTTPError):
        code = error.response.status_code if error.response is not None else '未知'
        return f'平台返回 HTTP {code}，请重试；登录失效时请更新 Cookie'
    message = re.sub(r'https?://\S+', '[链接已隐藏]', str(error))
    message = re.sub(r'(?i)(cookie|authorization|token|key)\s*[:=].*', r'\1=[已隐藏]', message)
    return (message or type(error).__name__).replace('\n', ' ')[:350]


class ProviderLogger:
    """musicdl reports some failures via logging instead of raising them."""
    def __init__(self):
        self.errors = []

    def info(self, message, **kwargs):
        pass

    debug = info
    warning = info

    def error(self, message, **kwargs):
        self.errors.append(safe_error(message))


def display_text(value, fallback='—'):
    if value is None or str(value).strip() in ('', 'NULL', 'null', 'None'):
        return fallback
    if isinstance(value, (list, tuple)):
        return ' / '.join(str(item) for item in value)
    return str(value)


def normalize_song(song, source, headers=None, cookies=None):
    raw = song.todict() if hasattr(song, 'todict') else dict(song)
    record = {key: raw.get(key) for key in (
        'identifier', 'download_url', 'downloaded_contents', 'file_size_bytes',
        'duration_s', 'protocol',
    )}
    record.update({key: display_text(raw.get(key)) for key in (
        'song_name', 'singers', 'album', 'file_size', 'duration',
    )})
    record['source'] = source
    record['ext'] = str(raw.get('ext') or 'mp3').lstrip('.').lower()
    record['default_download_headers'] = dict(raw.get('default_download_headers') or headers or {})
    record['default_download_cookies'] = dict(raw.get('default_download_cookies') or cookies or {})
    return record


def search_source(source, keyword, settings, work_dir):
    # Lazy import keeps the window usable even when the backend cannot import.
    from musicdl.modules import BuildMusicClient
    from rich.progress import Progress

    logger = ProviderLogger()
    cookie = settings.get('cookies', {}).get(source, {})
    limit = settings.get('search_limit', 5)
    client = BuildMusicClient(module_cfg={
        'type': source,
        'work_dir': str(work_dir),
        'logger_handle': logger,
        'disable_print': True,
        'search_size_per_source': limit,
        'search_size_per_page': limit,
        'max_retries': 1,
        'default_search_cookies': cookie.get('search', ''),
        'default_download_cookies': cookie.get('download') or cookie.get('search', ''),
    })
    # The upstream builder deep-copies its config, including logger instances.
    client.logger_handle = logger
    with Progress(disable=True) as progress:
        task = progress.add_task('search', total=0)
        songs = client.search(keyword=keyword, num_threadings=3,
                              request_overrides={'timeout': (5, 10)},
                              main_process_context=progress, main_progress_id=task)
    records = []
    for song in songs or []:
        record = normalize_song(song, source, client.default_download_headers, client.default_download_cookies)
        if record['download_url'] or record['downloaded_contents']:
            records.append(record)
    if not records and logger.errors:
        raise BackendError(logger.errors[-1])
    warning = '部分请求失败，已保留可用结果' if logger.errors else ''
    return records[:limit], warning


def safe_filename(value, fallback='未知歌曲'):
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', str(value)).strip(' .')
    name = name.encode('utf-8')[:170].decode('utf-8', errors='ignore').rstrip(' .') or fallback
    if name.split('.')[0].upper() in {'CON', 'PRN', 'AUX', 'NUL', *(f'COM{i}' for i in range(1, 10)), *(f'LPT{i}' for i in range(1, 10))}:
        name = '_' + name
    return name


def song_filename(song):
    ext = str(song.get('ext') or 'mp3').lstrip('.').lower()
    if not re.fullmatch(r'[a-z0-9]{1,8}', ext):
        ext = 'mp3'
    return f"{safe_filename(display_text(song.get('song_name'), '未知歌曲') + ' - ' + display_text(song.get('singers'), '未知歌手'))}.{ext}"


def download_song(song, staging_path, report):
    """Write a complete HTTP audio file to staging, never to its final name."""
    if str(song.get('protocol') or 'HTTP').upper() != 'HTTP':
        raise BackendError('此结果不是直链音频，请选择同一歌曲的其他结果')
    contents = song.get('downloaded_contents')
    if isinstance(contents, bytes) and contents:
        Path(staging_path).write_bytes(contents)
        report(100, f'{len(contents) / 1048576:.1f} MB')
        return
    url = song.get('download_url')
    if not isinstance(url, str) or urlsplit(url).scheme not in ('http', 'https'):
        raise BackendError('没有可用下载地址，请重新搜索')
    headers = dict(song.get('default_download_headers') or {})
    headers['Accept-Encoding'] = 'identity'
    with requests.get(url, headers=headers, cookies=song.get('default_download_cookies') or {},
                      timeout=(5, 15), stream=True) as response:
        response.raise_for_status()
        if response.status_code != 200:
            raise BackendError(f'下载响应不完整（HTTP {response.status_code}），请重新搜索')
        content_type = response.headers.get('Content-Type', '').lower()
        if any(kind in content_type for kind in ('text/', 'json', 'xml', 'mpegurl')):
            raise BackendError('平台返回了网页或错误信息，下载链接可能已过期，请重新搜索')
        total = int(response.headers.get('Content-Length') or 0)
        if response.headers.get('Content-Encoding', 'identity') != 'identity':
            total = 0
        downloaded, last_report = 0, 0.0
        with open(staging_path, 'wb') as output:
            for chunk in response.iter_content(chunk_size=64 * 1024):
                if not chunk:
                    continue
                if downloaded == 0 and chunk.lstrip().lower().startswith((b'<!doctype', b'<html', b'<?xml', b'{', b'[')):
                    raise BackendError('下载地址返回了错误页面，请重新搜索')
                output.write(chunk)
                downloaded += len(chunk)
                if time.monotonic() - last_report >= 0.1:
                    detail = f'{downloaded / 1048576:.1f} MB'
                    if total:
                        detail += f' / {total / 1048576:.1f} MB'
                    report(min(99, int(downloaded * 100 / total)) if total else -1, detail)
                    last_report = time.monotonic()
            output.flush()
            os.fsync(output.fileno())
        if not downloaded or (total and downloaded != total):
            raise BackendError('音频文件为空或传输不完整，请重试')
    report(100, f'{downloaded / 1048576:.1f} MB')


def publish_download(staging_path, directory, filename):
    """Reserve a unique name atomically; publish only a completed download."""
    directory = Path(directory)
    filename = safe_filename(Path(filename).stem) + Path(filename).suffix
    candidate = directory / filename
    count = 0
    while True:
        try:
            descriptor = os.open(candidate, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            os.close(descriptor)
            break
        except FileExistsError:
            count += 1
            candidate = directory / f'{Path(filename).stem} ({count}){Path(filename).suffix}'
    try:
        os.replace(staging_path, candidate)
    except BaseException:
        candidate.unlink(missing_ok=True)
        raise
    return str(candidate)


def prepare_download(song, staging_path, output_format, report, phase):
    """Download and optionally convert; only return a fully prepared file."""
    if output_format not in OUTPUT_FORMATS:
        raise BackendError('不支持的保存格式，请重新选择')
    phase('download', '正在下载')
    download_song(song, staging_path, report)
    if output_format == 'original':
        return staging_path
    phase('convert', f'正在转换为 {output_format.upper()}')
    report(-1, '正在读取音频…')
    try:
        return convert_audio(staging_path, str(Path(staging_path).with_suffix('.' + output_format)),
                             output_format, report, {
                                 'title': song.get('song_name'), 'artist': song.get('singers'),
                                 'album': song.get('album'),
                             })
    except ImportError as error:
        raise BackendError('无法加载音频转换组件，请重新安装完整依赖或使用完整安装包') from error
    except Exception as error:
        raise BackendError(f'转换为 {output_format.upper()} 失败：{safe_error(error)}') from error


def execute_job(connection, kind, arguments):
    """Spawn entry point: no Qt widgets or live clients cross processes."""
    try:
        if kind == 'search':
            result = search_source(**arguments)
        else:
            result = prepare_download(**arguments,
                                      report=lambda percent, detail: connection.send(('progress', percent, detail)),
                                      phase=lambda name, detail: connection.send(('phase', name, detail)))
        connection.send(('result', result))
    except Exception as error:
        connection.send(('error', safe_error(error)))
    finally:
        connection.close()
