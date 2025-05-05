# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['PyWrightIDE.py'],
    pathex=[],
    binaries=[],
    datas=[("res", "res"), ("LICENSE", "."), ("README.md", "."), ("CHANGELOG.md", "."), ("CREDITS.md", ".")],
    hiddenimports=["PyQt6"],
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
    name='PyWrightIDE',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
	icon="res/icons/ideicon.png",
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    contents_directory='.'
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='pywrightide',
)
