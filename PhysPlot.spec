# -*- mode: python ; coding: utf-8 -*-
import sys

from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import collect_submodules

# Bundle the editable config tree without caches or macOS resource forks. At
# runtime physplot.user_paths.project_root() resolves this copy from
# sys._MEIPASS and the Documents/PhysPlot/config copy takes precedence.
import os

ICON = 'installer/icons/PhysPlot.icns' if sys.platform == 'darwin' else 'installer/icons/PhysPlot.ico'

datas = []
for root, dirs, files in os.walk('config'):
    dirs[:] = [d for d in dirs if d != '__pycache__']
    for name in files:
        if name.endswith(('.pyc', '.pyo')) or name == '.DS_Store' or name.startswith('._'):
            continue
        datas.append((os.path.join(root, name), root))
hiddenimports = []
datas += collect_data_files('physplot')
hiddenimports += collect_submodules('physplot')
hiddenimports += collect_submodules('physplot_gui')


a = Analysis(
    ['physplot_gui/__main__.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
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
    name='PhysPlot',
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
    icon=ICON,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PhysPlot',
)
if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='PhysPlot.app',
        icon=ICON,
        bundle_identifier=None,
    )
