# -*- mode: python ; coding: utf-8 -*-
import os
from pathlib import Path
ROOT = Path(SPECPATH).parent


a = Analysis(
    [str(ROOT / 'main.py')],
    pathex=[],
    binaries=[],
    datas=[(str(ROOT / '项目创建工具.ico'), '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
# 构建机环境可能把错误的 ICU 78 DLL 带入产物，必须双重过滤。
BAD = {'icuuc.dll', 'icudt78.dll', 'icudt.dll', 'icuin.dll'}
a.binaries = [b for b in a.binaries if not os.path.basename(b[0]).lower().startswith('icu')]
a.datas = [d for d in a.datas if not os.path.basename(d[0]).lower().startswith('icu')]

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ProjectCreator',
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
    icon=[str(ROOT / '项目创建工具.ico')],
    contents_directory='_internal',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ProjectCreator',
)
