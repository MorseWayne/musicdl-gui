import os
import io
import math
import struct
import tempfile
import time

import pytest

# Keep tests away from personal settings and the upstream logger's default path.
_environment = tempfile.TemporaryDirectory(prefix='musicdl-tests-')
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
for key in ('XDG_CONFIG_HOME', 'XDG_DATA_HOME', 'XDG_STATE_HOME'):
    os.environ[key] = os.path.join(_environment.name, key)

from PyQt5.QtWidgets import QApplication


@pytest.fixture(scope='session')
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def wait_until(app):
    def wait(predicate, timeout=8):
        deadline = time.monotonic() + timeout
        while not predicate() and time.monotonic() < deadline:
            app.processEvents()
            time.sleep(0.01)
        app.processEvents()
        assert predicate(), 'Qt operation did not complete in time'
    return wait


@pytest.fixture
def flac_audio():
    """A short, non-silent lossless stereo recording, with no network fixture."""
    import av
    samples = 11025
    pcm = b''.join(struct.pack('<hh', value, -value)
                   for value in (int(12000 * math.sin(index * 2 * math.pi * 440 / 44100))
                                 for index in range(samples)))
    buffer = io.BytesIO()
    with av.open(buffer, 'w', format='flac') as container:
        container.metadata['title'] = 'Test recording'
        stream = container.add_stream('flac', rate=44100)
        stream.layout = 'stereo'
        frame = av.AudioFrame(format='s16', layout='stereo', samples=samples)
        frame.sample_rate = 44100
        frame.planes[0].update(pcm)
        for packet in stream.encode(frame):
            container.mux(packet)
        for packet in stream.encode(None):
            container.mux(packet)
    return buffer.getvalue(), pcm
