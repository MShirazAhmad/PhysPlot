Data Import
===========

For a full step-by-step flow, see :ref:`GUI Walkthrough — Importing Data <gui-importing-data>` and :ref:`GUI Walkthrough — Choosing Axis Roles <gui-choosing-axis-roles>`.

Supported formats
-----------------

- ``.csv``, ``.txt``, ``.dat``, ``.tsv``
- ``.xls``, ``.xlsx``
- Malvern Panalytical ``.xrdml`` XRD scans
- nanoindentation files through the built-in nanoindentation loader
- OES ``.HRF`` spectra through the ``OES HRF Loader`` plugin (also picked by
  **Auto Loader**)
- any format a loader plugin declares in ``FILE_EXTENSIONS``
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
- XRDML Loader (Panalytical XRD)
- DataFrame Loader

XRDML files
-----------

**Auto Loader** reads ``.xrdml`` files directly (schema 1.5 and 1.7 tested).
The table has the scanned axis (``2Theta``, or ``Omega`` for rocking curves)
and ``Intensity``, which are suggested as X and Y. For repeated scans
("reps"), ``Intensity`` is the sum of the scans' raw counts, the same values
the instrument software writes to CSV. ``Intensity 1`` ... ``Intensity N`` hold
the individual scans. Attenuation factors are not applied, matching that
export.

Wavelengths (``kAlpha1``, ``kAlpha2``, ratio), anode, tube voltage and
current, sample name, step size, counting time, attenuation factors and
start time are stored in the dataset metadata under ``xrdml``.

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

.. image:: ../_static/gui_walkthrough/walk_02_data_loader_menu.png
   :alt: Data import and axis assignment
   :width: 700px
