Data Import
===========

For a full step-by-step flow, see :ref:`GUI Walkthrough — Importing Data <gui-importing-data>` and :ref:`GUI Walkthrough — Choosing Axis Roles <gui-choosing-axis-roles>`.

Supported formats
-----------------

- ``.csv``, ``.txt``, ``.dat``, ``.tsv``
- ``.xls``, ``.xlsx``
- nanoindentation files through the built-in nanoindentation loader
- OES ``.HRF`` spectra through the ``OES HRF Loader`` plugin
- DataFrames through the backend API

Instrument exports
------------------

Text exports often put metadata above the data. When a plain read does not
give at least two numeric columns, PhysPlot finds the numeric table itself:

- It skips header blocks such as Malvern Panalytical XRD
  ``[Measurement conditions]`` sections and EDAX EDS ``Path :``/``KV :`` lines.
  The skipped lines are kept in the dataset metadata as ``header_lines``.
- It detects comma, tab, semicolon or whitespace separators, so tab-separated
  files saved as ``.csv`` load correctly. Quoted values such as ``"7.74"``
  are numbers.
- It turns spectra stored as rows, such as PHI XPS energy and count rows,
  into columns.

Binary files (for example AFM ``.dat`` scans), empty files and damaged
workbooks are reported by name instead of with a parser traceback.

Sequences recorded on a file loaded through a loader plugin, such as
``.HRF``, reuse that plugin for **Run Sequence** bulk runs,
``physplot run-workflow`` and an exported ``Sequence.py``'s ``run()``.
Bulk runs then process the files in the folder that have the same extension.

Loader selection
----------------

PhysPlot uses built-in and plugin-based file loaders. Choose the active loader
from Simple Mode's **Data Importer** panel before clicking **Import Data**.

Loader plugins are auto-discovered at startup from the ``config/data_importers/`` folder.
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
