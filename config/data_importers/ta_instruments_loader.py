"""Loader for TA Instruments TGA and DSC text exports.

TA Instruments Universal Analysis (Q-series instruments) exports a run as text. It
starts with a header of ``Key<TAB>Value`` lines:

- ``Size`` holds the sample mass, for example ``Size<TAB>20.8210<TAB>mg``.
- ``Sig1``, ``Sig2``, ... name the data columns in order, for example
  ``Sig2<TAB>Temperature (°C)``.

The readings follow a ``StartOfData`` line, one tab-separated row per reading. Rows
whose first value is negative are segment markers written by the instrument, not
measurements. Q-series instruments save the file as UTF-16 text; UTF-8 also works.
Exports from the newer TRIOS software use a different layout and are not read here.

Input data structure:
    ``file_path`` points to the exported ``.txt`` file. Choose this loader in the
    **Data Loader** menu: ``.txt`` files otherwise go to the built-in TXT loader.

Return type:
    ``load_data`` returns a pandas DataFrame whose column names are the ``Sig`` names.
    For a TGA run, ``Weight (%)`` (weight divided by the sample mass) is inserted just
    before the weight column. ``DEFAULT_COLUMN_ROLES`` then makes the temperature X and
    the next column Y: ``Weight (%)`` for TGA, heat flow for DSC.
"""

from pathlib import Path

import pandas as pd

title = "TA Instruments TGA/DSC Loader"
DEFAULT_COLUMN_ROLES = ["Ignore", "X", "Y"]


def _read_text(path):
    raw = Path(path).read_bytes()
    if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        return raw.decode("utf-16")
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return raw.decode("latin-1")


def load_data(file_path):
    """Read a TA Instruments text export into named columns.

    Parameters:
        file_path (str | pathlib.Path): Path to the exported text file.

    Returns:
        pandas.DataFrame: One row per reading, one column per signal, plus
        ``Weight (%)`` when the run recorded a weight and the header gives ``Size``.

    Raises:
        ValueError: If there is no ``StartOfData`` line or no readings after it.
    """
    signal_names = {}
    sample_mass = None
    rows = []
    in_data = False
    for line in _read_text(file_path).splitlines():
        if not in_data:
            key, _, value = line.partition("\t")
            if key == "StartOfData":
                in_data = True
            elif key.startswith("Sig") and key[3:].isdigit():
                signal_names[int(key[3:])] = value.strip()
            elif key == "Size":
                sample_mass = float(value.split("\t")[0])
            continue
        try:
            values = [float(part) for part in line.split()]
        except ValueError:
            continue
        if values and values[0] >= 0:  # negative first value = segment marker
            rows.append(values)

    if not rows:
        raise ValueError("No readings found after a StartOfData line. Is this a TA Instruments text export?")

    width = min(len(row) for row in rows)
    columns = [signal_names.get(number, f"Signal {number}") for number in range(1, width + 1)]
    table = pd.DataFrame([row[:width] for row in rows], columns=columns)

    weight = next((name for name in columns if name.startswith("Weight") and "(mg)" in name), None)
    if weight and sample_mass:
        table.insert(columns.index(weight), "Weight (%)", table[weight] / sample_mass * 100.0)
    return table
