File Loader API
===============

User file loaders live in the ``config/data_importers`` folder. Each loader
exposes ``title`` or ``DISPLAY_NAME`` and ``load_data(file_path)``. Built-in
backend loaders live under ``physplot.loaders``.

Package Contract
----------------

.. automodule:: config.data_importers
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

XRDML Loader
------------

.. automodule:: physplot.loaders.xrdml
   :members:

Instrument Text Tables
----------------------

.. automodule:: physplot.loaders.text_table
   :members:

Loader Plugins
--------------

.. automodule:: physplot.loaders.plugins
   :members:
