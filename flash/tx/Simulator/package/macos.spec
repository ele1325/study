# -*- mode: python ; coding: utf-8 -*-


block_cipher = None

my_data = [('../conf/config.ini', './conf')]

a = Analysis(
    ['../main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('../conf/config.ini', './conf'),
    ],
    hiddenimports=['AppKit', 'objc'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='CN30UYX01.0_Simulator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    windowed=True,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='CN30UYX01.0_Simulator',
)

app = BUNDLE(
    coll,
    name='CN30UYX01.0_Simulator.app',
    icon="logo.icns",
    bundle_identifier=None,
)
