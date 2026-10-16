import time

import workers
from workers import DownloadWorker, SearchWorker


def hanging_job(connection, kind, arguments):
    time.sleep(30)


def source_job(connection, kind, arguments):
    source = arguments['source']
    if source == 'slow':
        time.sleep(30)
    elif source == 'error':
        connection.send(('error', 'source failure'))
    else:
        connection.send(('result', ([{'song_name': source}], '')))
    connection.close()


def test_sources_finish_independently_and_timeout(monkeypatch, wait_until):
    monkeypatch.setattr(workers, 'execute_job', source_job)
    worker = SearchWorker(['slow', 'fast', 'error', 'later'], 'test', {'search_timeout': 2})
    events = []
    worker.result_sig.connect(lambda source, songs, warning: events.append(('result', source)))
    worker.error_sig.connect(lambda source, error: events.append(('error', source)))
    worker.start()
    wait_until(lambda: ('result', 'fast') in events)
    assert worker.isRunning()  # The slow source must not hold back fast results.
    wait_until(lambda: not worker.isRunning())
    assert sorted(events) == sorted([('result', 'fast'), ('result', 'later'), ('error', 'error'), ('error', 'slow')])


def test_cancel_search_reaps_backend(monkeypatch, wait_until):
    monkeypatch.setattr(workers, 'execute_job', hanging_job)
    worker = SearchWorker(['slow'], 'test', {'search_timeout': 60})
    started = []
    worker.started_sig.connect(started.append)
    worker.start()
    wait_until(lambda: bool(started))
    worker.requestInterruption()
    wait_until(lambda: not worker.isRunning(), timeout=4)


def test_search_temp_directory_failure_is_reported(monkeypatch, wait_until):
    def fail(**kwargs):
        raise OSError('临时目录不可写')
    monkeypatch.setattr(workers.tempfile, 'TemporaryDirectory', fail)
    worker = SearchWorker(['source'], 'test', {})
    errors = []
    worker.error_sig.connect(lambda source, message: errors.append(message))
    worker.start()
    wait_until(lambda: not worker.isRunning())
    assert errors == ['临时目录不可写']


def test_real_download_process_publishes_only_complete_file(tmp_path, wait_until):
    worker = DownloadWorker({'downloaded_contents': b'ID3test-audio'}, str(tmp_path), 'track.mp3')
    results = []
    worker.result_sig.connect(lambda *result: results.append(result))
    worker.start()
    wait_until(lambda: not worker.isRunning())
    assert results[0][0]
    assert (tmp_path / 'track.mp3').read_bytes() == b'ID3test-audio'
    assert len(list(tmp_path.iterdir())) == 1


def test_cancel_download_cleans_staging(monkeypatch, tmp_path, wait_until):
    monkeypatch.setattr(workers, 'execute_job', hanging_job)
    worker = DownloadWorker({}, str(tmp_path), 'track.mp3')
    results = []
    worker.result_sig.connect(lambda *result: results.append(result))
    worker.start()
    wait_until(lambda: bool(list(tmp_path.iterdir())))
    worker.requestInterruption()
    wait_until(lambda: not worker.isRunning(), timeout=4)
    assert results == [(False, '已取消下载', '')]
    assert list(tmp_path.iterdir()) == []
