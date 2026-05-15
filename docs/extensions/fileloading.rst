File-Loader Plugins
===================

What File Loaders Do
--------------------

File-loader plugins convert external data files into a two-dimensional table
that PhysPlot can display. A loader receives a file path and returns a
rectangular data array.

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
   Text shown in the Data Loader dropdown.

``load_data(file_path)``
   Function that receives a file path and returns a two-dimensional table-like
   object.

Optional:

``DEFAULT_COLUMN_ROLES``
   A list of default role labels such as ``["X-axis", "Y-axis"]``. PhysPlot
   applies these roles automatically after import.

Minimal CSV-Like Template
-------------------------

.. code-block:: python

   """Loader for a custom instrument text file."""

   from pathlib import Path
   import numpy as np

   title = "My Instrument Loader"
   DEFAULT_COLUMN_ROLES = ["X-axis", "Y-axis"]


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

- ``fileloader/default_loader.py``
- ``fileloader/oes_hrf_loader.py``
