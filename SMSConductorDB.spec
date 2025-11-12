# -*- mode: python ; coding: utf-8 -*-
# PyInstaller Spec File for SMS Conductor Database Viewer
# With Master Queue System, Bullseye Scheduler, and all enhancements

block_cipher = None

a = Analysis(
    ['conductor-sms\\SMSconductor_DB.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('conductor-sms\\CRITICAL_SQL_SETUP.md', '.'),
        ('docs\\SMS_VIEWER_ENHANCEMENTS.md', 'docs'),
        ('docs\\MASTER_QUEUE_SYSTEM.md', 'docs'),
    ],
    hiddenimports=[
        'supabase',
        'supabase._sync.client',
        'tkinter',
        'tkinter.ttk',
        'tkinter.scrolledtext',
        'dateutil',
        'dateutil.parser',
        'dateutil.tz',
        'dotenv',
        'httpx',
        'httpcore',
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
    [],
    exclude_binaries=True,
    name='SMSConductorDB',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Enabled for debugging PyInstaller issue
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add .ico file path here if you have an icon
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SMSConductorDB',
)

