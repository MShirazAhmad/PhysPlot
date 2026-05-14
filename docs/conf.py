import os
import sys

sys.path.insert(0, os.path.abspath('..'))

project = 'PhysPlot'
author = 'Muhammad Shiraz Ahmad and Sabieh Anwar'
release = '1.1.3'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'myst_parser',
]

templates_path = ['_templates']
exclude_patterns = ['_build']

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

master_doc = 'index'
