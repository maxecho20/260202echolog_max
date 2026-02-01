# -*- mode: python ; coding: utf-8 -*-
"""
EchoLog PyInstaller Spec File
=============================
用于将 EchoLog 打包成 Windows 可执行文件
"""

import sys
from pathlib import Path

# 获取项目根目录
project_root = Path(SPECPATH)

a = Analysis(
    ['main_gui.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        ('.env.example', '.'),
        ('README.md', '.'),
    ],
    hiddenimports=[
        'customtkinter',
        'websockets',
        'sounddevice',
        'numpy',
        'dotenv',
        'asyncio',
        'tkinter',
        'PIL',
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
    name='EchoLog',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 可以添加 icon='assets/icon.ico'
)
