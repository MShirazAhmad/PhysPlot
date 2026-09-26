"""Loader for Rigaku SmartLab ``.ras`` XRD scans.

A ``.ras`` file is plain text. Header lines start with ``*`` and hold quoted values
(``*MEAS_SCAN_START "20.0000"``). The measured points sit between ``*RAS_INT_START``
and ``*RAS_INT_END``, one per line: angle, counts and the attenuator factor that was in
the beam. Multiplying counts by that factor gives the true intensity, which matters at
strong peaks where SmartLab inserts an attenuator.

Input data structure:
    ``file_path`` points to a ``.ras`` file. Only the first scan is read when a file
    holds several.

Return type:
    ``load_data`` returns a two-column NumPy array ``[2Theta, Intensity]`` with
    ``Intensity = counts * attenuator factor``. ``COLUMN_NAMES`` names the columns and
    ``DEFAULT_COLUMN_ROLES`` makes them X and Y. ``FILE_EXTENSIONS`` lets Auto Loader,
    replayed sequences and bulk runs open ``.ras`` files with this loader.
"""

from pathlib import Path

import numpy as np

title = "Rigaku RAS Loader (XRD)"
FILE_EXTENSIONS = [".ras"]
COLUMN_NAMES = ["2Theta", "Intensity"]
DEFAULT_COLUMN_ROLES = ["X", "Y"]


def load_data(file_path):
    """Read the first scan of a Rigaku ``.ras`` file.

    Parameters:
        file_path (str | pathlib.Path): Path to the ``.ras`` file.

    Returns:
        numpy.ndarray: One row per point, columns ``[2Theta, Intensity]``.

    Raises:
        ValueError: If the file has no ``*RAS_INT_START`` block with numeric rows.
    """
    # Rigaku writes comments in the PC's code page; latin-1 never fails to decode.
    lines = Path(file_path).read_text(encoding="latin-1").splitlines()
    rows = []
    in_data = False
    for line in lines:
        line = line.strip()
        if line.startswith("*RAS_INT_START"):
            in_data = True
            continue
        if line.startswith("*RAS_INT_END"):
            if rows:
                break  # first scan only
            in_data = False
            continue
        if not in_data or not line or line.startswith("*"):
            continue
        parts = line.split()
        angle, counts = float(parts[0]), float(parts[1])
        attenuator = float(parts[2]) if len(parts) > 2 else 1.0
        rows.append((angle, counts * attenuator))

    if not rows:
        raise ValueError("No scan data found. Expected lines between *RAS_INT_START and *RAS_INT_END.")
    return np.asarray(rows, dtype=float)
