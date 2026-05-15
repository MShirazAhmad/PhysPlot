"""Default data loader for PhysPlot.

This loader reads common spreadsheet and text formats and returns a 2D
NumPy array for the main table.

Input data structure:
    ``file_path`` is a path-like object or string pointing to an Excel, CSV,
    TSV, TXT, or generic delimited numeric text file.

Return type:
    ``load_data`` returns a two-dimensional NumPy array. A one-dimensional
    source is reshaped to ``(rows, 1)``.

Optional main/runtime behavior:
    Loaded dynamically by the Data Loader selector. This module is not
    intended to be run directly.
"""

from pathlib import Path

import numpy as np
import pandas as pd


title = "Default Loader"


def _as_2d_array(data):
    """_as_2d_array(data) -> numpy.ndarray

    Convert loader output into a two-dimensional NumPy array.

    Parameters:
        data (array-like): Raw table-like data loaded from a file.

    Returns:
        numpy.ndarray: A 2D array. One-dimensional input is reshaped to
        ``(rows, 1)``.
    """
    array = np.asarray(data)
    if array.ndim == 1:
        return array.reshape(-1, 1)
    return array


def load_data(file_path):
    """load_data(file_path) -> numpy.ndarray

    Load a spreadsheet or delimited text file for the PhysPlot table.

    Parameters:
        file_path (str | pathlib.Path): Path to ``.xlsx``, ``.xls``, ``.csv``,
        ``.txt``, ``.tsv``, or another delimited numeric text file.

    Returns:
        numpy.ndarray: Two-dimensional table data suitable for ``printTOTable``.
    """
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix in {".xlsx", ".xls"}:
        data = pd.read_excel(path, header=None).to_numpy()
    elif suffix == ".csv":
        data = pd.read_csv(path, header=None).to_numpy()
    elif suffix in {".txt", ".tsv"}:
        try:
            data = np.loadtxt(path)
        except Exception:
            data = pd.read_csv(path, header=None, sep=None, engine="python").to_numpy()
    else:
        try:
            data = np.loadtxt(path)
        except Exception:
            data = pd.read_csv(path, header=None, sep=None, engine="python").to_numpy()

    return _as_2d_array(data)
