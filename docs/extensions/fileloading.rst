File-Loader Plugins
===================

What File Loaders Do
--------------------

File-loader plugins convert external data files into a two-dimensional table
that PhysPlot can display. A loader receives a file path and returns a
rectangular data array.

Where Loaders Appear in the UI
------------------------------

Discovered loaders are shown in two places:

- Simple Mode's **Data Importer** loader dropdown.
- The backend loader registry for scripted and headless workflows when a
  loader is implemented as a backend loader.

The selected loader is used when importing files. PhysPlot discovers loader
files at startup.

Layman Example
--------------

If your instrument saves data in a special format, a loader teaches PhysPlot how
to skip the header text and keep only the useful numeric columns. For example,
the OES HRF loader skips metadata and returns wavelength and intensity columns.

Required File Location
----------------------

Put new file-loader files in:

.. code-block:: text

   fileloader/

Use a clear filename:

.. code-block:: text

   fileloader/my_instrument_loader.py

Required Structure
------------------

Every loader should define:

``title``
   Text shown in the **Data Importer** loader dropdown.

``DISPLAY_NAME``
   Also accepted by the modern GUI for user/plugin-style loaders.

``load_data(file_path)``
   Function that receives a file path and returns a two-dimensional table-like
   object.

Optional:

``DEFAULT_COLUMN_ROLES``
   A list of default role labels such as ``["X", "Y"]``. PhysPlot
   applies these roles automatically after import.

Minimal CSV-Like Template
-------------------------

.. code-block:: python

   """Loader for a custom instrument text file."""

   from pathlib import Path
   import numpy as np

   title = "My Instrument Loader"
   DISPLAY_NAME = "My Instrument Loader"
   DEFAULT_COLUMN_ROLES = ["X", "Y"]


   def load_data(file_path):
       """load_data(file_path) -> numpy.ndarray

       Load two numeric columns from a custom instrument file.

       Parameters:
           file_path (str | pathlib.Path): Path selected in the import dialog.

       Returns:
           numpy.ndarray: Two-column array ready for the PhysPlot table.
       """
       rows = []
       for line in Path(file_path).read_text().splitlines():
           if line.startswith("#"):
               continue
           parts = line.split(",")
           if len(parts) < 2:
               continue
           rows.append((float(parts[0]), float(parts[1])))
       return np.asarray(rows, dtype=float)

Step-by-Step: Build a New Loader
--------------------------------

1. Create a new file in ``fileloader/`` (for example
   ``fileloader/my_device_loader.py``).
2. Define a human-readable ``title`` string.
3. Implement ``load_data(file_path)`` to parse your format and return a 2D
   array-like result.
4. Optionally define ``DEFAULT_COLUMN_ROLES`` to pre-assign column roles after
   import.
5. Restart PhysPlot so the loader is discovered and added to Simple Mode's
   **Data Importer** dropdown.
6. Select your loader from **Data Importer**, then import a file.

Loader Categories
-----------------

- **General tabular loader**: parse delimited numeric files.
- **Instrument-specific loader**: skip custom headers/metadata and keep
  meaningful columns.
- **Role-aware loader**: also sets ``DEFAULT_COLUMN_ROLES`` for automatic
  X/Y mapping.

OES HRF Pattern
---------------

The OES HRF loader demonstrates a common pattern:

1. Read the whole file as text.
2. Ignore metadata until a marker line.
3. Parse numeric rows.
4. Drop unnecessary index columns.
5. Return only the columns PhysPlot should show.

Practical Rules
---------------

- Always return a rectangular two-dimensional array.
- Convert values to floats when possible.
- Raise a helpful ``ValueError`` if the file contains no usable rows.
- Use ``DEFAULT_COLUMN_ROLES`` when a loader knows which columns are X and Y.
- Keep loader code independent from the GUI. Do not modify the table directly.

Existing Examples
-----------------

See:

- ``fileloader/`` for user/plugin-style loaders
- ``physplot/loaders/`` for built-in backend loaders
