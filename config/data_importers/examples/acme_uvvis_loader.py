"""PhysPlot data importer for Acme Photonics UV-1900 ASCII exports (.uvs).

File layout, one scan per file:
- Header lines "Key:<TAB>value" (instrument, sample, date, ...). They are skipped.
- A "[Data]" line, one line of column titles, then one row per wavelength:
  wavelength, mean absorbance and its standard deviation over the replicate
  scans. Exports of a single scan have no standard-deviation column.
- An "[End]" line closes the table.
PCs set to a European locale write decimal commas ("0,0412"); a comma inside a
number is read as a decimal point.

load_data returns a NumPy array with the columns in COLUMN_NAMES, sorted by
increasing wavelength. DEFAULT_COLUMN_ROLES makes wavelength X, absorbance Y
and the standard deviation Y Error. FILE_EXTENSIONS lets Auto Loader open .uvs files.
"""

from pathlib import Path

import numpy as np

title = "Acme UV-1900 Loader (UV-Vis)"
FILE_EXTENSIONS = [".uvs"]
COLUMN_NAMES = ["Wavelength (nm)", "Absorbance", "Absorbance SD"]
DEFAULT_COLUMN_ROLES = ["X", "Y", "Y Error"]


def _number(cell):
    """Return one table cell as a float, accepting a decimal comma."""
    return float(cell.replace(",", "."))


def load_data(file_path):
    """Read the [Data] table of a UV-1900 export.

    Parameters:
        file_path (str or pathlib.Path): The .uvs file the user chose.

    Returns:
        numpy.ndarray: One row per wavelength, columns as in COLUMN_NAMES.

    Raises:
        ValueError: If there is no [Data] line, a data row is not numeric,
        or the table is empty.
    """
    # latin-1 decodes every byte, so an unusual character in the header never stops the import.
    lines = Path(file_path).read_text(encoding="latin-1").splitlines()
    starts = [index for index, line in enumerate(lines) if line.strip().lower() == "[data]"]
    if not starts:
        raise ValueError("No [Data] line found. Is this an Acme UV-1900 ASCII export (.uvs)?")

    rows = []
    for line_number, line in enumerate(lines[starts[0] + 1:], start=starts[0] + 2):
        line = line.strip()
        if line.lower() == "[end]":
            break
        if not line:
            continue
        cells = line.split()  # tabs or spaces; numbers themselves contain no spaces
        try:
            values = [_number(cell) for cell in cells[:3]]
        except ValueError:
            if not rows:
                continue  # the column-title line before the first number
            raise ValueError(f"Line {line_number} is not a row of numbers: {line!r}") from None
        if len(values) < 2:
            raise ValueError(f"Line {line_number} needs a wavelength and an absorbance: {line!r}")
        if len(values) == 2:
            values.append(float("nan"))  # single-scan export: no standard deviation
        rows.append(values)

    if not rows:
        raise ValueError("The [Data] block contains no rows of numbers.")
    table = np.array(rows, dtype=float)
    return table[np.argsort(table[:, 0])]  # the instrument scans from long to short wavelength
