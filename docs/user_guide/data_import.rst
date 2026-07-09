Data Import
===========

For a full step-by-step flow, see :ref:`GUI Walkthrough — Importing Data <gui-importing-data>` and :ref:`GUI Walkthrough — Choosing Axis Roles <gui-choosing-axis-roles>`.

Supported formats
-----------------

- ``.txt``
- ``.csv``
- ``.tsv``
- ``.xlsx``
- nanoindentation files through the built-in nanoindentation loader
- DataFrames through the backend API

Loader selection
----------------

PhysPlot uses built-in and plugin-based file loaders. Choose the active loader
from Simple Mode's **Data Importer** panel before clicking **Import Data**.

Loader plugins are auto-discovered at startup from the ``fileloader/`` folder.
Built-in loaders are:

- Auto Loader
- CSV Loader
- TXT Loader
- Excel Loader
- Nanoindentation Loader
- DataFrame Loader

Import steps
------------

1. Select a loader, or keep **Auto Loader** for common tabular files.
2. Click **Import Data**.
3. Select a supported file.
4. PhysPlot loads values into the table and updates the column-role dropdowns.

Column assignment
-----------------

Use the dropdown at row 0 for each column and choose one of:

- Ignore
- X
- Y
- X Error
- Y Error
- Group
- Label

.. image:: ../_static/gui_walkthrough/02_import_file_selection_dialog.png
   :alt: Data import and axis assignment
   :width: 700px
