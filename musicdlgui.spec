# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all
from pathlib import Path

datas, binaries, hiddenimports = [], [], []
for package in ('musicdl', 'fake_useragent', 'curl_cffi', 'nodejs_wheel'):
    package_data, package_binaries, package_imports = collect_all(package)
    datas.extend(package_data)
    binaries.extend(package_binaries)
    hiddenimports.extend(package_imports)
icon_path = Path(SPECPATH) / 'icon.ico'
if icon_path.exists():
    datas.append((str(icon_path), '.'))

a = Analysis(
    ['musicdlgui.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PyQt5.QtWebEngine', 'PyQt5.QtWebEngineCore', 'PyQt5.QtWebEngineWidgets', 'PyQt5.QtWebChannel', 'PyQt5.QtWebSockets', 'PyQt5.QtQml', 'PyQt5.QtQuick', 'PyQt5.QtQuickWidgets', 'PyQt5.Qt3DCore', 'PyQt5.Qt3DRender', 'PyQt5.Qt3DInput', 'PyQt5.Qt3DLogic', 'PyQt5.Qt3DAnimation', 'PyQt5.Qt3DExtras', 'PyQt5.QtBluetooth', 'PyQt5.QtDBus', 'PyQt5.QtDesigner', 'PyQt5.QtHelp', 'PyQt5.QtLocation', 'PyQt5.QtMultimedia', 'PyQt5.QtMultimediaWidgets', 'PyQt5.QtNfc', 'PyQt5.QtOpenGL', 'PyQt5.QtPositioning', 'PyQt5.QtPrintSupport', 'PyQt5.QtRemoteObjects', 'PyQt5.QtSensors', 'PyQt5.QtSerialPort', 'PyQt5.QtSql', 'PyQt5.QtSvg', 'PyQt5.QtTest', 'PyQt5.QtTextToSpeech', 'PyQt5.QtXml', 'PyQt5.QtXmlPatterns'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='MusicdlGUI',
    icon=str(icon_path) if icon_path.exists() else None,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
