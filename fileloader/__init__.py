"""Data loader modules for PhysPlot.

Each loader module should expose a ``load_data(file_path)`` function that
returns a 2D array-like object suitable for loading into the table.

Input data structure:
    Loader modules receive a file path chosen from the import dialog.

Return type:
    Loader modules return a rectangular two-dimensional table-like object,
    usually a NumPy array.

Optional main/runtime behavior:
    Package marker for dynamically discovered loader plugins; not executable
    by itself.
"""
