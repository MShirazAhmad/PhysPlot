"""Loader for ImageJ pore-results CSV files.

This loader reads calibrated ImageJ particle-analysis CSV files and returns
numeric columns useful for pore-size plotting. ImageJ ``Area`` is assumed to be
already calibrated in square micrometers (um^2); no pixel-size recalibration is
applied.

Input data structure:
    ``file_path`` is a path-like object or string pointing to one ImageJ
    ``*_Results.csv`` file. The file should contain at least an ``Area`` column.

Return type:
    ``load_data`` returns a NumPy array with columns listed in ``COLUMN_NAMES``.
    ``DEFAULT_COLUMN_ROLES`` marks equivalent pore diameter as X and pore area
    as Y by default, but the plotting UI can reassign roles.

Optional main/runtime behavior:
    Loaded dynamically by the Data Loader selector. This module is not intended
    to be run directly.
"""

from pathlib import Path
import re

import numpy as np
import pandas as pd


title = "ImageJ Pore Results Loader"

COLUMN_NAMES = [
    "Particle_ID",
    "Area_um2",
    "Area_nm2",
    "d_eq_um",
    "d_eq_nm",
    "Feret",
    "MinFeret",
    "Major",
    "Minor",
    "Perim.",
    "Circ.",
    "AR",
    "Round",
    "Solidity",
    "P_Torr",
]

COLUMN_DETAILS = {
    "Particle_ID": "ImageJ particle row/index identifier.",
    "Area_um2": "Calibrated ImageJ pore area, assumed already in square micrometers.",
    "Area_nm2": "Pore area converted from um^2 to nm^2 using 1 um^2 = 1e6 nm^2.",
    "d_eq_um": "Equivalent circular pore diameter: 2*sqrt(Area_um2/pi).",
    "d_eq_nm": "Equivalent circular pore diameter in nanometers.",
    "Feret": "ImageJ Feret diameter, if present.",
    "MinFeret": "ImageJ minimum Feret diameter, if present.",
    "Major": "ImageJ fitted ellipse major axis, if present.",
    "Minor": "ImageJ fitted ellipse minor axis, if present.",
    "Perim.": "ImageJ perimeter, if present.",
    "Circ.": "ImageJ circularity, if present.",
    "AR": "ImageJ aspect ratio, if present.",
    "Round": "ImageJ roundness, if present.",
    "Solidity": "ImageJ solidity, if present.",
    "P_Torr": "Pressure inferred from filename when possible; NaN if unknown.",
}

DEFAULT_COLUMN_ROLES = [
    "Ignore",      # Particle_ID
    "Ignore",      # Area_um2
    "Ignore",      # Area_nm2
    "X-axis",      # d_eq_um
    "Ignore",      # d_eq_nm
    "Ignore",      # Feret
    "Ignore",      # MinFeret
    "Ignore",      # Major
    "Ignore",      # Minor
    "Ignore",      # Perim.
    "Ignore",      # Circ.
    "Ignore",      # AR
    "Ignore",      # Round
    "Ignore",      # Solidity
    "Group",       # P_Torr
]

NUMERIC_SOURCE_COLUMNS = [
    "Area", "Feret", "MinFeret", "Major", "Minor", "Perim.",
    "Width", "Height", "Circ.", "AR", "Round", "Solidity",
]

PRESSURE_FROM_FILENAME = {
    "sample2": 200,
    "s2": 200,
    "200": 200,
    "sample1": 760,
    "s1": 760,
    "760": 760,
}


def clean_imagej_columns(dataframe):
    """Return a copy with stripped ImageJ column names and unnamed first column fixed."""
    dataframe = dataframe.copy()
    dataframe.columns = [
        str(col).strip() if str(col).strip() else "Particle_ID"
        for col in dataframe.columns
    ]
    return dataframe


def infer_pressure_torr(file_path):
    """Infer pressure from common sample tokens in the file name.

    Returns np.nan when no pressure token is recognized.
    """
    name = Path(file_path).stem.lower()

    for token, pressure in PRESSURE_FROM_FILENAME.items():
        if re.search(rf"(^|[^0-9a-z]){re.escape(token)}([^0-9a-z]|$)", name):
            return pressure

    match = re.search(r"(\d+)\s*torr", name)
    if match:
        return int(match.group(1))

    return np.nan


def load_dataframe(file_path, pressure_torr=None):
    """Load one ImageJ Results CSV as a cleaned analysis dataframe.

    Parameters:
        file_path (str | pathlib.Path): Path to one ImageJ ``*_Results.csv``.
        pressure_torr (int | float | None): Optional pressure override. If None,
            pressure is inferred from the file name when possible.

    Returns:
        pandas.DataFrame: Cleaned table containing original ImageJ columns plus
        ``P_Torr``, ``Source_file``, ``Area_um2``, ``Area_nm2``, ``d_eq_um``, and
        ``d_eq_nm``.

    Raises:
        FileNotFoundError: If ``file_path`` does not exist.
        ValueError: If the CSV lacks ``Area`` or has no valid positive areas.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")

    dataframe = clean_imagej_columns(pd.read_csv(path))

    if "Area" not in dataframe.columns:
        raise ValueError("ImageJ Results CSV must contain an 'Area' column.")

    for col in NUMERIC_SOURCE_COLUMNS:
        if col in dataframe.columns:
            dataframe[col] = pd.to_numeric(dataframe[col], errors="coerce")

    if "Particle_ID" not in dataframe.columns:
        dataframe.insert(0, "Particle_ID", np.arange(1, len(dataframe) + 1))

    dataframe["P_Torr"] = infer_pressure_torr(path) if pressure_torr is None else pressure_torr
    dataframe["Source_file"] = path.name

    dataframe = dataframe.dropna(subset=["Area"]).copy()
    dataframe = dataframe[dataframe["Area"] > 0].copy()

    if dataframe.empty:
        raise ValueError("No valid pore rows found. Expected positive numeric values in 'Area'.")

    dataframe["Area_um2"] = dataframe["Area"]
    dataframe["Area_nm2"] = dataframe["Area_um2"] * 1e6
    dataframe["d_eq_um"] = 2.0 * np.sqrt(dataframe["Area_um2"] / np.pi)
    dataframe["d_eq_nm"] = dataframe["d_eq_um"] * 1000.0

    return dataframe


def load_data(file_path):
    """load_data(file_path) -> numpy.ndarray

    Load one calibrated ImageJ pore-results CSV and return numeric plotting data.

    Parameters:
        file_path (str | pathlib.Path): Path to one ImageJ ``*_Results.csv``.

    Returns:
        numpy.ndarray: Numeric array with columns listed in ``COLUMN_NAMES``.
    """
    dataframe = load_dataframe(file_path)

    output = pd.DataFrame(index=dataframe.index)
    output["Particle_ID"] = pd.to_numeric(dataframe["Particle_ID"], errors="coerce")
    output["Area_um2"] = dataframe["Area_um2"]
    output["Area_nm2"] = dataframe["Area_nm2"]
    output["d_eq_um"] = dataframe["d_eq_um"]
    output["d_eq_nm"] = dataframe["d_eq_nm"]

    for col in ["Feret", "MinFeret", "Major", "Minor", "Perim.", "Circ.", "AR", "Round", "Solidity"]:
        output[col] = pd.to_numeric(dataframe[col], errors="coerce") if col in dataframe.columns else np.nan

    output["P_Torr"] = pd.to_numeric(dataframe["P_Torr"], errors="coerce")

    return output[COLUMN_NAMES].to_numpy(dtype=float)
