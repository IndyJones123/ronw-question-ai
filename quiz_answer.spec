# -*- mode: python ; coding: utf-8 -*-
# Build: pyinstaller quiz_answer.spec
# Hasil: dist/QuizAnswer.exe  (+ taruh .env SEBELAH exe, jangan di-bundle)

block_cipher = None

a = Analysis(
    ['quiz_answer_app.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['PIL', 'PIL.ImageGrab', 'requests', 'dotenv'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'IPython', 'jupyter', 'notebook', 'scipy',
              'pandas', 'numpy', 'tkinter.test', 'unittest'],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='QuizAnswer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,   # True saat debug crash-on-launch
    disable_windowed_traceback=False,
)
