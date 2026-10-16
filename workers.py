"""Qt workers own and reap isolated, cancellable backend processes."""
import copy
import multiprocessing
import tempfile
import time
from collections import deque
from pathlib import Path

from PyQt5.QtCore import QThread, pyqtSignal

from backend import execute_job, publish_download, safe_error


class ProcessJob:
    def __init__(self, kind, arguments):
        context = multiprocessing.get_context('spawn')
        self.connection, child = context.Pipe(duplex=False)
        self.process = context.Process(target=execute_job, args=(child, kind, arguments), daemon=True)
        self.started = time.monotonic()
        try:
            self.process.start()
        except BaseException:
            self.connection.close()
            self.process.close()
            raise
        finally:
            child.close()

    def receive(self):
        if self.connection.poll():
            try:
                return self.connection.recv()
            except EOFError:
                return ('error', '音乐源进程意外退出，请重试或检查依赖版本')
        if not self.process.is_alive():
            return ('error', '音乐源进程意外退出，请重试或检查依赖版本')
        return None

    def close(self):
        if self.process.is_alive():
            self.process.terminate()
        self.process.join(timeout=1)
        if self.process.is_alive():
            self.process.kill()
            self.process.join()
        self.connection.close()
        self.process.close()


class SearchWorker(QThread):
    started_sig = pyqtSignal(str)
    result_sig = pyqtSignal(str, list, str)
    error_sig = pyqtSignal(str, str)

    def __init__(self, music_sources, keyword, settings, parent=None):
        super().__init__(parent)
        self.music_sources = list(music_sources)
        self.keyword = keyword
        self.settings = copy.deepcopy(settings)

    def run(self):
        try:
            self._run_sources()
        except Exception as error:
            # Even failure to create/clean a temp directory must reach the UI;
            # an exception escaping QThread.run can terminate the application.
            for source in self.music_sources:
                self.error_sig.emit(source, safe_error(error))

    def _run_sources(self):
        pending, active = deque(self.music_sources), {}
        timeout = self.settings.get('search_timeout', 60)
        with tempfile.TemporaryDirectory(prefix='musicdl-search-') as temporary:
            try:
                while pending or active:
                    if self.isInterruptionRequested():
                        break
                    while pending and len(active) < 3:
                        source = pending.popleft()
                        try:
                            active[source] = ProcessJob('search', {
                                'source': source, 'keyword': self.keyword,
                                'settings': self.settings, 'work_dir': str(Path(temporary) / source),
                            })
                            self.started_sig.emit(source)
                        except Exception as error:
                            self.error_sig.emit(source, safe_error(error))
                    for source, job in list(active.items()):
                        message = job.receive()
                        if message is None and time.monotonic() - job.started >= timeout:
                            message = ('error', f'搜索超过 {timeout} 秒，已停止；可在设置中延长时限或切换音乐源')
                        if message:
                            job.close()
                            del active[source]
                            if message[0] == 'result':
                                self.result_sig.emit(source, *message[1])
                            else:
                                self.error_sig.emit(source, message[1])
                    self.msleep(40)
            except Exception as error:
                for source in list(active) + list(pending):
                    self.error_sig.emit(source, safe_error(error))
            finally:
                for job in active.values():
                    job.close()


class DownloadWorker(QThread):
    progress_sig = pyqtSignal(int, str)
    result_sig = pyqtSignal(bool, str, str)

    def __init__(self, song_info, download_dir, filename, parent=None):
        super().__init__(parent)
        self.song_info = copy.deepcopy(song_info)
        self.download_dir = Path(download_dir)
        self.filename = filename

    def run(self):
        try:
            self.download_dir.mkdir(parents=True, exist_ok=True)
            # Keep staging on the destination filesystem for atomic publication.
            with tempfile.TemporaryDirectory(prefix='.musicdl-', dir=self.download_dir) as temporary:
                staging = str(Path(temporary) / 'audio.part')
                job = ProcessJob('download', {'song': self.song_info, 'staging_path': staging})
                try:
                    while True:
                        if self.isInterruptionRequested():
                            self.result_sig.emit(False, '已取消下载', '')
                            break
                        if time.monotonic() - job.started > 600:
                            self.result_sig.emit(False, '下载超过 10 分钟，已停止，请重试', '')
                            break
                        message = job.receive()
                        if message:
                            if message[0] == 'progress':
                                self.progress_sig.emit(*message[1:])
                            elif message[0] == 'result':
                                path = publish_download(staging, self.download_dir, self.filename)
                                self.result_sig.emit(True, '下载完成', path)
                                break
                            else:
                                self.result_sig.emit(False, message[1], '')
                                break
                        self.msleep(40)
                finally:
                    job.close()
        except Exception as error:
            self.result_sig.emit(False, safe_error(error), '')
