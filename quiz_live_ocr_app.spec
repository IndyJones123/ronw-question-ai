# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['quiz_live_ocr_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Bank soal JSON wajib di-bundle ke dlm EXE (diakses via sys._MEIPASS).
        ('quiz_databases/mode/sage.json', 'quiz_databases/mode'),
        ('quiz_databases/mode/hoppy.json', 'quiz_databases/mode'),
    ],
    hiddenimports=[
        'auth_client',
        'dotenv',
        'requests',
        'PIL._tkinter_finder',
    ],
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
    a.binaries,
    a.datas,
    [],
    name='quiz_live_ocr_app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
