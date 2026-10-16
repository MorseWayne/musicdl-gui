"""Offline smoke checks runnable inside the frozen Windows executable."""
import json
import multiprocessing
import tempfile
import time
from pathlib import Path

from app_config import SOURCES, default_settings
from backend import normalize_song, safe_error


def probe_backend(connection, directory):
    try:
        from musicdl.modules import BuildMusicClient
        for source in SOURCES:
            client = BuildMusicClient(module_cfg={
                'type': source, 'work_dir': directory, 'disable_print': True,
            })
            if not client.default_search_headers:
                raise RuntimeError(f'{source}: missing request headers')
        connection.send({'ok': True, 'sources': list(SOURCES)})
    except Exception as error:
        connection.send({'ok': False, 'error': safe_error(error)})
    finally:
        connection.close()


def run_smoke_test(app, window, report_path):
    report = {'ok': False}
    try:
        with tempfile.TemporaryDirectory(prefix='musicdl-release-check-') as temporary:
            window.settings = dict(default_settings(), work_dir=temporary)
            window.show()
            app.processEvents()
            context = multiprocessing.get_context('spawn')
            parent, child = context.Pipe(duplex=False)
            process = context.Process(target=probe_backend, args=(child, temporary))
            process.start()
            child.close()
            try:
                if not parent.poll(60):
                    raise RuntimeError('Backend initialization timed out')
                probe = parent.recv()
                if not probe['ok']:
                    raise RuntimeError(probe['error'])
                report['sources'] = probe['sources']
            finally:
                process.join(timeout=2)
                if process.is_alive():
                    process.terminate()
                    process.join(timeout=2)
                if process.is_alive():
                    process.kill()
                    process.join()
                process.close()
                parent.close()
            content = b'ID3-offline-release-smoke-test'
            window.append_results([normalize_song({
                'song_name': 'release-check', 'singers': 'test',
                'ext': 'mp3', 'downloaded_contents': content,
            }, 'MiguMusicClient')])
            window.start_downloads(list(window.music_records))
            deadline = time.monotonic() + 60
            while window.download_worker is not None and time.monotonic() < deadline:
                app.processEvents()
                time.sleep(0.01)
            if window.download_worker is not None:
                window.cancel_download()
                while window.download_worker is not None:
                    app.processEvents()
                    time.sleep(0.01)
                raise RuntimeError('Download subprocess timed out')
            files = list(Path(temporary).glob('*.mp3'))
            if window.batch_success != 1 or len(files) != 1 or files[0].read_bytes() != content:
                raise RuntimeError('Download subprocess or file publication failed')
            report.update(ok=True, checks=['window', 'provider_initialization', 'download_subprocess', 'file_publication'])
    except Exception as error:
        report['error'] = safe_error(error)
    finally:
        window.close()
        app.processEvents()
        Path(report_path).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    return 0 if report['ok'] else 1
