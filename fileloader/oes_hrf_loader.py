"""Loader for OES .HRF files.

The .HRF files include metadata followed by comma-separated rows:
index, wavelength, intensity. PhysPlot should plot wavelength vs intensity,
so this loader drops the leading index column.

Input data structure:
    ``file_path`` is a path-like object or string pointing to an OES ``.HRF``
    file. Numeric data are parsed only after the ``PMT Voltage:`` metadata
    line.

Return type:
    ``load_data`` returns a two-column NumPy array ``[wavelength, intensity]``.
    ``DEFAULT_COLUMN_ROLES`` marks those columns as X-axis and Y-axis.

Optional main/runtime behavior:
    Loaded dynamically by the Data Loader selector. This module is not
    intended to be run directly.
"""

from pathlib import Path
import re

import numpy as np


title = "OES HRF Loader"
COLUMN_NAMES = ["Wavelength", "Intensity"]
DEFAULT_COLUMN_ROLES = ["X-axis", "Y-axis"]
DATA_ROW_PATTERN = re.compile(
    r"^\s*([-+]?\d+(?:\.\d+)?)\s*,?\s+"
    r"([-+]?\d+(?:\.\d+)?)\s*,?\s+"
    r"([-+]?\d+(?:\.\d+)?)\s*$"
)


def load_data(file_path):
    """load_data(file_path) -> numpy.ndarray

    Load OES HRF data as wavelength and intensity columns.

    Parameters:
        file_path (str | pathlib.Path): Path to an ``.HRF`` file whose numeric
        data begin after the ``PMT Voltage:`` metadata line.

    Returns:
        numpy.ndarray: Two-column array ``[wavelength, intensity]``. The leading
        index column in the HRF file is skipped.

    Raises:
        ValueError: If no numeric OES data rows are found.
    """
    rows = []
    text = Path(file_path).read_text(encoding="utf-8", errors="ignore")
    in_data_section = False
    for line in text.splitlines():
        if not in_data_section:
            if line.strip().startswith("PMT Voltage:"):
                in_data_section = True
            continue
        match = DATA_ROW_PATTERN.match(line)
        if not match:
            continue
        try:
            float(match.group(1))
            x_value = float(match.group(2))
            y_value = float(match.group(3))
        except ValueError:
            continue
        rows.append((x_value, y_value))

    if not rows:
        raise ValueError("No OES data rows found. Expected rows like: index, wavelength, intensity.")

    return np.asarray(rows, dtype=float)
