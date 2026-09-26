"""Sphinx documentation configuration for PhysPlot.

Input data structure:
    Sphinx imports this module while building documentation. The configuration
    uses project metadata, extension names, mock import names, and source
    paths.

Return type:
    No explicit return value. Sphinx reads module-level variables such as
    ``project``, ``extensions``, ``html_theme``, and ``master_doc``.

Optional main/runtime behavior:
    Not intended to be run directly; used by ``sphinx-build``.
"""

import os
import re
import sys

sys.path.insert(0, os.path.abspath('..'))


def _package_version() -> str:
    init = open(os.path.join(os.path.dirname(__file__), '..', 'physplot', '__init__.py'), encoding='utf-8').read()
    match = re.search(r"__version__ = ['\"]([^'\"]+)['\"]", init)
    return match.group(1) if match else '0.0.0'


project = 'PhysPlot'
author = 'Shiraz Ahmad'
release = _package_version()
version = release

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'myst_parser',
]
autodoc_mock_imports = ['PyQt6', 'PySide6', 'FigureForge', 'appdirs', 'matplotlib', 'numpy', 'scipy', 'pandas']
autodoc_typehints = 'signature'
autodoc_preserve_defaults = True
add_module_names = False

templates_path = ['_templates']
# Internal planning notes are kept in the repo but not published.
exclude_patterns = ['_build', 'ADVANCED_MODE_PLAN.md']

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_logo = '_static/physplot_icon.png'
html_favicon = '_static/favicon.png'

master_doc = 'index'
