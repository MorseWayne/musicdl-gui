"""Real local HTTP transfer through the same process boundary as the GUI."""
import io
import threading
import wave
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from workers import DownloadWorker


@pytest.fixture
def audio_server():
    data = io.BytesIO()
    with wave.open(data, 'wb') as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(8000)
        output.writeframes(b'\0\0' * 800)
    audio = data.getvalue()
    requests = []

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            requests.append(dict(self.headers))
            self.send_response(200)
            self.send_header('Content-Type', 'audio/wav')
            self.send_header('Content-Length', str(len(audio) + (100 if self.path == '/truncated' else 0)))
            self.end_headers()
            self.wfile.write(audio)

        def log_message(self, *args):
            pass

    try:
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    except PermissionError:
        pytest.skip('当前沙箱禁止本机监听端口；请在允许 localhost 的环境运行此集成测试')
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f'http://127.0.0.1:{server.server_port}', audio, requests
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def test_http_download_preserves_audio_and_credentials(audio_server, tmp_path, wait_until):
    url, audio, requests = audio_server
    song = {'download_url': url + '/audio', 'default_download_headers': {'Referer': 'test-player'},
            'default_download_cookies': {'session': 'test-cookie'}}
    worker = DownloadWorker(song, str(tmp_path), 'track.wav')
    result = []
    worker.result_sig.connect(lambda *args: result.append(args))
    worker.start()
    wait_until(lambda: not worker.isRunning())
    assert result[0][0]
    assert (tmp_path / 'track.wav').read_bytes() == audio
    assert requests[0]['Referer'] == 'test-player'
    assert requests[0]['Cookie'] == 'session=test-cookie'
    assert len(list(tmp_path.iterdir())) == 1


def test_truncated_http_transfer_leaves_no_music_file(audio_server, tmp_path, wait_until):
    url, _, _ = audio_server
    worker = DownloadWorker({'download_url': url + '/truncated'}, str(tmp_path), 'track.wav')
    result = []
    worker.result_sig.connect(lambda *args: result.append(args))
    worker.start()
    wait_until(lambda: not worker.isRunning())
    assert not result[0][0]
    assert not list(tmp_path.iterdir())
