import time
from pathlib import Path

import av
import pytest

import workers
from workers import DownloadWorker, SearchWorker


def hanging_job(connection, kind, arguments):
    time.sleep(30)


def converting_job(connection, kind, arguments):
    staging = Path(arguments['staging_path'])
    staging.write_bytes(b'original')
    staging.with_suffix('.wav').write_bytes(b'partial conversion')
    connection.send(('phase', 'convert', '正在转换为 WAV'))
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


@pytest.mark.parametrize('target', ['wav', 'mp3'])
def test_download_and_convert_publish_actual_target_format(tmp_path, wait_until, flac_audio, target):
    # Deliberately wrong source extension: real content must determine conversion.
    song = {'downloaded_contents': flac_audio[0], 'ext': target}
    worker = DownloadWorker(song, str(tmp_path), f'track.{target}', output_format=target)
    result, phases = [], []
    worker.result_sig.connect(lambda *args: result.append(args))
    worker.phase_sig.connect(lambda name, detail: phases.append(name))
    worker.start()
    wait_until(lambda: not worker.isRunning())
    assert result[0][0]
    files = list(tmp_path.iterdir())
    assert files == [tmp_path / f'track.{target}']
    with av.open(str(files[0])) as output:
        assert output.format.name == target
        assert next(output.decode(audio=0), None) is not None
    assert phases == ['download', 'convert']


def test_cancel_conversion_cleans_source_and_partial_target(monkeypatch, tmp_path, wait_until):
    monkeypatch.setattr(workers, 'execute_job', converting_job)
    worker = DownloadWorker({}, str(tmp_path), 'track.flac', output_format='wav')
    result, phases = [], []
    worker.result_sig.connect(lambda *args: result.append(args))
    worker.phase_sig.connect(lambda *args: phases.append(args))
    worker.start()
    wait_until(lambda: bool(phases))
    worker.requestInterruption()
    wait_until(lambda: not worker.isRunning(), timeout=4)
    assert not result[0][0]
    assert list(tmp_path.iterdir()) == []


def test_failed_conversion_does_not_overwrite_existing_song(tmp_path, wait_until):
    existing = tmp_path / 'track.wav'
    existing.write_bytes(b'existing recording')
    worker = DownloadWorker({'downloaded_contents': b'invalid audio'}, str(tmp_path), 'track.flac', output_format='wav')
    result = []
    worker.result_sig.connect(lambda *args: result.append(args))
    worker.start()
    wait_until(lambda: not worker.isRunning())
    assert not result[0][0] and '转换为 WAV 失败' in result[0][1]
    assert existing.read_bytes() == b'existing recording'
    assert list(tmp_path.iterdir()) == [existing]
