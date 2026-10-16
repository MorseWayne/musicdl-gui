#!/usr/bin/env python
"""Noninteractive environment check and optional, bounded live search probe."""
import argparse
import importlib
import multiprocessing
import platform
import sys
from importlib.metadata import version
from pathlib import Path


def check_environment():
    print(f'Python {platform.python_version()} · {platform.system()} {platform.machine()}')
    ok = sys.version_info >= (3, 10)
    if not ok:
        print('需要 Python 3.10+，建议使用 3.11 或 3.12。')
    for package, module in [('PyQt5', 'PyQt5.QtWidgets'), ('requests', 'requests'), ('musicdl', 'musicdl.modules'), ('av', 'av')]:
        try:
            imported = importlib.import_module(module)
            installed = version(package)
            if package == 'musicdl':
                assert callable(imported.BuildMusicClient)
                assert callable(imported.SongInfo.todict)
                if installed != '2.14.0':
                    print(f'警告：musicdl {installed}，本项目验证版本为 2.14.0。')
            if package == 'av':
                for encoder in ('pcm_s16le', 'pcm_s32le', 'libmp3lame'):
                    imported.codec.Codec(encoder, 'w')
            print(f'✓ {package} {installed}')
        except Exception as error:
            print(f'✗ {package}: {type(error).__name__}: {error}')
            ok = False
    for filename in ('musicdlgui.py', 'workers.py', 'backend.py', 'audio_conversion.py', 'app_config.py', 'components.py', 'dialogs.py', 'styles.py', 'logger.py'):
        if not Path(__file__).with_name(filename).is_file():
            print(f'✗ 缺少文件：{filename}')
            ok = False
    print('环境检查通过。' if ok else '请修复以上问题，并运行 python -m pip install -r requirements.txt')
    return ok


def probe_search(args):
    from PyQt5.QtCore import QCoreApplication
    from app_config import SOURCES, default_settings
    from workers import SearchWorker

    sources = args.sources.split(',')
    unknown = set(sources) - set(SOURCES)
    if unknown:
        print(f'不支持的来源：{", ".join(sorted(unknown))}')
        return 1
    app = QCoreApplication([])
    # Never read or print personal cookies during a diagnostic probe.
    settings = dict(default_settings(), search_timeout=args.timeout, search_limit=args.limit)
    worker = SearchWorker(sources, args.search, settings)
    counts = []

    def result(source, songs, warning):
        counts.append(len(songs))
        print(f'{SOURCES[source]}：{len(songs)} 首 {warning}', flush=True)
        for song in songs[:3]:
            print(f"  {song['song_name']} · {song['singers']} · {song['ext']}", flush=True)

    worker.started_sig.connect(lambda source: print(f'{SOURCES[source]}：开始搜索', flush=True))
    worker.result_sig.connect(result)
    worker.error_sig.connect(lambda source, error: print(f'{SOURCES[source]}：失败 — {error}', flush=True))
    worker.finished.connect(app.quit)
    worker.start()
    app.exec_()
    worker.wait()
    return 0 if sum(counts) else 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--search', help='可选：联网搜索关键词，不下载音频、不读取个人 Cookie')
    parser.add_argument('--sources', default='KuwoMusicClient,MiguMusicClient,NeteaseMusicClient')
    parser.add_argument('--timeout', type=int, default=60, choices=range(1, 181), metavar='1..180')
    parser.add_argument('--limit', type=int, default=2, choices=range(1, 31), metavar='1..30')
    args = parser.parse_args()
    if not check_environment():
        return 1
    return probe_search(args) if args.search else 0


if __name__ == '__main__':
    multiprocessing.freeze_support()
    sys.exit(main())
