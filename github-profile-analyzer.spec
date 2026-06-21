# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['src'],
    binaries=[],
    datas=[('src', 'src')],
    hiddenimports=[
        'github',
        'requests',
        'matplotlib',
        'numpy',
        'rich',
        'rich.console',
        'rich.panel',
        'rich.prompt',
        'rich.table',
        'rich.progress',
        'rich.theme',
        'rich.box',
        'unified_analyzer',
        'file_utils',
        'html_visualizer',
        'github_scraper',
        'github_scraper_cli',
        'advanced_analyzer',
        'visualizer',
        'compare_profiles',
        'export_report'
    ],
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='github-profile-analyzer',
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
