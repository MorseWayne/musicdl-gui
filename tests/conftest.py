import os
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
