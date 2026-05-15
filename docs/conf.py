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
import sys

sys.path.insert(0, os.path.abspath('..'))

project = 'PhysPlot'
author = 'Shiraz Ahmad'
release = '2.0.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'myst_parser',
]
autodoc_mock_imports = ['PyQt5', 'matplotlib', 'numpy', 'scipy', 'pandas']
autodoc_typehints = 'signature'
autodoc_preserve_defaults = True
add_module_names = False

templates_path = ['_templates']
exclude_patterns = ['_build']

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

master_doc = 'index'
