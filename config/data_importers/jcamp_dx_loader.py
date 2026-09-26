"""Loader for JCAMP-DX spectra (``.jdx``, ``.dx``): FTIR, Raman and UV-Vis.

JCAMP-DX is the standard text format for spectra. Every header line is a
``##LABEL=value`` pair. The labels this loader uses:

- ``##XUNITS`` and ``##YUNITS``: what the axes are, for example ``1/CM`` and
  ``TRANSMITTANCE``.
- ``##FIRSTX``, ``##LASTX`` and ``##NPOINTS``: the X range and the number of points.
- ``##XFACTOR`` and ``##YFACTOR``: stored numbers times these give the real values.
- ``##XYDATA=(X++(Y..Y))``: starts the table. Each line holds one X value followed
  by several consecutive Y values. Each Y is one X step
  (``(LASTX - FIRSTX) / (NPOINTS - 1)``) further than the one before it.
- ``##END=``: closes the file.

This example reads the uncompressed (AFFN) form, as served by the NIST Chemistry
WebBook and written by many spectrometer exports. Compressed data, with letters in
place of digits, is reported with a clear error.

Return type:
    ``load_data`` returns a pandas DataFrame with two columns named from the units,
    for example ``Wavenumber (1/cm)`` and ``Transmittance``. ``DEFAULT_COLUMN_ROLES``
    makes them X and Y, and ``FILE_EXTENSIONS`` lets Auto Loader open JCAMP-DX files.
"""

from pathlib import Path

import pandas as pd

title = "JCAMP-DX Spectrum Loader"
FILE_EXTENSIONS = [".jdx", ".dx", ".jcamp"]
DEFAULT_COLUMN_ROLES = ["X", "Y"]
X_NAMES = {"1/CM": "Wavenumber (1/cm)", "NANOMETERS": "Wavelength (nm)", "MICROMETERS": "Wavelength (um)"}


def load_data(file_path):
    """Read the XYDATA table of a JCAMP-DX file as scaled X and Y columns.

    Parameters:
        file_path (str | pathlib.Path): Path to the ``.jdx`` or ``.dx`` file.

    Returns:
        pandas.DataFrame: ``NPOINTS`` rows with the X and Y columns.

    Raises:
        ValueError: If the file has no ``(X++(Y..Y))`` table or uses compressed data.
    """
    labels = {}
    table = []
    in_table = False
    for line in Path(file_path).read_text(encoding="latin-1").splitlines():
        line = line.strip()
        if line.startswith("##"):
            if in_table:
                break  # the next label (normally ##END=) closes the table
            label, _, value = line[2:].partition("=")
            labels[label.strip().upper()] = value.strip()
            if label.strip().upper() == "XYDATA":
                if value.replace(" ", "").upper() != "(X++(Y..Y))":
                    raise ValueError(f"Unsupported table type {value.strip()!r}; expected (X++(Y..Y)).")
                in_table = True
            continue
        if in_table and line:
            try:
                table.append([float(number) for number in line.replace(",", " ").split()])
            except ValueError:
                raise ValueError(
                    "This file stores compressed JCAMP-DX data, which this example loader does not decode. "
                    "Export the spectrum uncompressed (AFFN) or extend load_data."
                ) from None

    if not table:
        raise ValueError("No ##XYDATA=(X++(Y..Y)) table found. Is this a JCAMP-DX file?")

    x_factor = float(labels.get("XFACTOR", 1))
    y_factor = float(labels.get("YFACTOR", 1))
    points = int(float(labels["NPOINTS"]))
    step = (float(labels["LASTX"]) - float(labels["FIRSTX"])) / (points - 1)
    x_values, y_values = [], []
    for line_x, *line_y in table:
        for index, y in enumerate(line_y):
            # Rounding to 12 significant digits drops float noise such as 0.91650000000000001.
            x_values.append(float(f"{line_x * x_factor + index * step:.12g}"))
            y_values.append(float(f"{y * y_factor:.12g}"))

    x_units = labels.get("XUNITS", "").upper()
    x_name = X_NAMES.get(x_units, f"X ({labels.get('XUNITS', '')})")
    y_name = labels.get("YUNITS", "Y").capitalize()
    return pd.DataFrame({x_name: x_values[:points], y_name: y_values[:points]})
