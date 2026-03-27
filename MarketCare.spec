# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path


PROJECT_DIR = Path(os.getcwd()).resolve()


a = Analysis(
    ['market_gui.py'],
    pathex=[str(PROJECT_DIR)],
    binaries=[],
    datas=[
        (str(PROJECT_DIR / 'db' / 'schema.sql'), 'db'),
        (str(PROJECT_DIR / 'assets'), 'assets'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MarketCare',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MarketCare',
)
