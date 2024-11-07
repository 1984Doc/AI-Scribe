# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src\\FreeScribe.client\\client.py'],
    pathex=[],
    binaries=[],
    datas=[('.\\src\\FreeScribe.client\\whisper-assets', 'whisper\\assets'), ('.\\src\\FreeScribe.client\\markdown', 'markdown'), ('.\\src\\FreeScribe.client\\assets', 'assets')],
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
    name='freescribe-client',
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
    icon=['src\\FreeScribe.client\\assets\\logo.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='freescribe-client',
)
