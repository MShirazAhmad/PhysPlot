File Loader API
===============

User file loaders live in the top-level ``fileloader`` folder. Each loader
exposes ``title`` or ``DISPLAY_NAME`` and ``load_data(file_path)``. Built-in
backend loaders live under ``physplot.loaders``.

Package Contract
----------------

.. automodule:: fileloader
   :members:
   :undoc-members:

Built-In Backend Loaders
------------------------

.. automodule:: physplot.loaders
   :members:
   :undoc-members:

Loader Base Classes
-------------------

.. automodule:: physplot.loaders.base
   :members:
   :undoc-members:
