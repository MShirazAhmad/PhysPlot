# Data Importers: guide for AI assistants

> **PhysPlot users:** attach this file to a chat with any AI assistant (ChatGPT, Claude, Gemini, Copilot, ...), together with one real data file from your instrument (or its first 50 lines pasted as text). Then describe what you want. The assistant replies with one complete file: save it in `Documents/PhysPlot/config/data_importers/` and choose **File → Reload Config Modules** in PhysPlot. Step-by-step help: https://physplot.readthedocs.io/en/latest/extensions/ai_assistant.html

## Your task

Write exactly one Python file: a PhysPlot data importer (file loader). Name it after the instrument or format, in lowercase with underscores, ending in `_loader.py`, for example `acme_uvvis_loader.py`. PhysPlot is a table-first plotting program for scientists. It imports every `.py` file in `Documents/PhysPlot/config/data_importers/`, lists each file that defines `load_data` in its **Data Loader** menu under the file's `title`, and calls `load_data(file_path)` when the user imports a data file. Whatever the data file looks like, `load_data` returns one rectangular table of numbers: one row per measurement point, one column per quantity. The user is a scientist, not a programmer, so write plain, readable code with short comments.

## Ask the user first

Before writing code, make sure you have the items below. Ask for the missing ones in one short list. Never guess the layout of a file you have not seen.

1. A real data file, attached, or its first 30-50 lines pasted as text (every header line plus several data rows). For long files, also the last 5 lines.
2. The file extension (for example `.uvs`) and the instrument or software that wrote it.
3. Which quantities to keep, their units, which one is X, which is Y, and any error columns.
4. What the sample cannot show: decimal comma or point, several scans or blocks in one file (keep the first, keep all, or average?), corrections or scale factors to apply.

If a sample is attached, read it yourself and ask only what it does not answer.

## The file PhysPlot expects

Top-level names in the module:

| Name | Required | Type and meaning |
|---|---|---|
| `title` | yes | `str`, not empty. The label in the **Data Loader** menu, for example `"Acme UV-1900 Loader (UV-Vis)"`. Make it unique. |
| `load_data(file_path)` | yes | Receives the chosen file's path, as a `str` or a `pathlib.Path`; wrap it in `Path(file_path)`. Returns a `pandas.DataFrame` (its column names are used), a 2-D NumPy array, or a list of equal-length rows. |
| `COLUMN_NAMES` | no | `list[str]`, one name per column. Use it only when `load_data` returns an array or a list of rows. Missing names become `Column 1`, `Column 2`, ... |
| `DEFAULT_COLUMN_ROLES` | no | `list[str]`, one role per column, in column order. Each entry is exactly one of `"X"`, `"Y"`, `"X Error"`, `"Y Error"`, `"Group"`, `"Label"`, `"Batch Key"`, `"Fit Weight"`, `"Ignore"`. |
| `FILE_EXTENSIONS` | no | `list[str]` of extensions with the dot, for example `[".uvs"]`. **Auto Loader** then sends these files to this loader. |
| `PLOTTERS` | no | Plots that belong to this format. See "Optional: a plot inside the loader" below. |

How PhysPlot uses the file:

- PhysPlot runs the file as a module at start-up, on **File → Reload Config Modules** and before imports. Top-level code must only import packages and define names: if it raises an error, PhysPlot skips the whole file. Read data only inside `load_data`.
- On **Import Data**, PhysPlot calls `load_data(path)`, fills its table, names the columns and sets the roles from `DEFAULT_COLUMN_ROLES`. `"X"`, `"Y"`, `"X Error"`, `"Y Error"` and `"Fit Weight"` may each be given to one column only; a later column with the same role replaces the earlier one. Give every column a role and use `"Ignore"` for columns that should not be plotted.
- The import is recorded as a *File Loader* step. Saved sequences, Run Sequence and bulk runs call the same `load_data` on other files and then find the X, Y, ... columns by name.
- `FILE_EXTENSIONS` is matched case-insensitively against the last extension of the file name. It must be a plain list of strings written directly in the file, because PhysPlot reads it from the source text without running the file. It is ignored for extensions that built-in loaders already read: `.csv`, `.txt`, `.dat`, `.tsv`, `.msa`, `.xls`, `.xlsx`, `.xrdml`. For those, leave `FILE_EXTENSIONS` out; the user picks the loader by its `title` in **Data Loader**.

### Optional: a plot inside the loader

Add `PLOTTERS` only if the user asks for a fixed plot for this format; PhysPlot's own plotters already plot any X and Y columns. `PLOTTERS` is a list of dicts with `plotter_id` (unique, no spaces), `name` (menu label), `plot_types` (list of `str` offered in **Plot Type**) and `callable` (the function; define it above `PLOTTERS`). PhysPlot calls `function(dataset, plot_type=<chosen type>, config={})`. `dataset.dataframe` is the table as a `pandas.DataFrame` and `dataset.column_roles` maps each column name to its role. The function returns a `matplotlib.figure.Figure`. Build it with `Figure()`, not `pyplot`, and never call `show()`.

```python
from matplotlib.figure import Figure


def spectrum_plot(dataset, plot_type="publication_ready", config=None):
    """Plot the Y column against the X column, with error bars from a Y Error column."""
    column_for = {role: column for column, role in dataset.column_roles.items()}
    if "X" not in column_for or "Y" not in column_for:
        raise ValueError("Set one column to X and one to Y before plotting.")
    table = dataset.dataframe
    y_error = table[column_for["Y Error"]] if "Y Error" in column_for else None
    figure = Figure(figsize=(6, 4))
    axes = figure.add_subplot()
    axes.errorbar(table[column_for["X"]], table[column_for["Y"]], yerr=y_error, linewidth=1)
    axes.set_xlabel(column_for["X"])
    axes.set_ylabel(column_for["Y"])
    return figure


PLOTTERS = [
    {
        "plotter_id": "acme_uvvis_spectrum",
        "name": "UV-Vis Spectrum with Error Bars",
        "plot_types": ["publication_ready"],
        "callable": spectrum_plot,
    }
]
```

The plot appears in **Plotter Module** only after a file was imported with this loader chosen by name in **Data Loader** (not through **Auto Loader**). Its protocol row is for display only, so saved sequences and bulk runs do not redraw it, and the **LSQ fit** option does not apply to it.

## Rules

- Import only the Python standard library, `numpy` and `pandas`; `scipy` and `matplotlib` are also available. `pandas.read_excel` can read `.xlsx` and `.xls` (openpyxl and xlrd are installed). Nothing else may be assumed installed: a file that imports a missing package is skipped without a visible message.
- No GUI code (no PyQt, tkinter, message boxes, `input()`), no `physplot_gui` imports, no network access. Do not rely on `print`: nobody sees it. Do not write, move or delete files. Only read the file passed to `load_data`.
- Return a rectangular table of numbers. Convert every value with `float()`; use `float("nan")` for a missing value; every row has the same number of columns.
- Use short column names with units in parentheses, for example `"Wavelength (nm)"`, `"Temperature (K)"`, `"Current (mA)"`. Names must be unique and the same for every file of this format: do not build them from the sample name, date or file name, because saved sequences find columns by name.
- Either return a DataFrame and leave out `COLUMN_NAMES`, or return an array with `COLUMN_NAMES`. Never both: the table would then be named from `COLUMN_NAMES` while saved sequences use the DataFrame's names.
- Keep values in the units of the file unless the user asks for a conversion. Apply the corrections the user or the format requires (scale factors, attenuators) inside `load_data`.
- PhysPlot keeps only the returned table. If a header value matters (a scale factor, a start value and step for X, a sample temperature), use it inside `load_data`, or add it as a constant column if the user wants it in the table.
- Text encoding: read text with `encoding="latin-1"`, which never fails, unless the file is UTF-16 (it starts with the bytes `FF FE` or `FE FF`); decode that with `"utf-16"`. Use `"utf-8-sig"` when UTF-8 characters such as `°` or `µ` must survive, with `latin-1` as a fallback.
- Decimal commas: split each line into cells on the real separator first, then replace `","` with `"."` inside each cell. Never do this in a comma-separated file. With `pandas.read_csv`, pass `decimal=","` instead.
- Be tolerant: skip blank lines and surrounding spaces, and accept tabs or runs of spaces when the sample does not make the separator certain.
- When a file is not what the loader expects, `raise ValueError("...")` with one sentence that says what was expected and what was found. PhysPlot shows only this text, in an *Import failed* dialog, without a traceback. An unhandled `KeyError` or `IndexError` would show as a fragment such as `'Temperature'` or `list index out of range`.
- Start the file with a docstring that describes the input layout and the returned columns. No `__main__` block and no test code.

## Complete working example

The user attached this export from a (fictional) Acme UV-1900 spectrophotometer, `methylene_blue.uvs`. Columns are separated by tab characters, and the PC writes decimal commas.

```text
Acme Photonics UV-1900 ASCII Export
Instrument:	UV-1900 (S/N 41A2207)
Sample:	Methylene blue 5 uM in water
Date:	14.03.2026 10:42
Scan range:	700 - 600 nm
Interval:	20 nm
Path length:	10 mm
Replicates:	3
[Data]
Wavelength (nm)	Abs	Abs SD
700,0	0,0412	0,0011
680,0	0,2195	0,0019
660,0	0,3561	0,0024
640,0	0,2248	0,0017
620,0	0,1752	0,0015
600,0	0,1124	0,0012
[End]
```

`acme_uvvis_loader.py`:

```python
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
```

In PhysPlot this gives 6 rows with the columns `Wavelength (nm)` (X), `Absorbance` (Y) and `Absorbance SD` (Y Error), from 600 to 700 nm.

## Reply format

```
Reply with:
1. The file name on its own line, for example `acme_uvvis_loader.py`.
2. The complete file in one code block. Never shorten it or leave placeholders such as "..." or "rest unchanged".
3. Two or three short sentences: what the module does and anything the user should check.
If you change the file after the user reports an error, send the complete corrected file again.
```

## How the user tests it

1. Save the file in `Documents/PhysPlot/config/data_importers/` (**File → Open Config Folder** opens `Documents/PhysPlot/config/`). The name must end in `.py`, not `.py.txt`, and must differ from the loaders PhysPlot ships (for example `default_loader.py`), or it replaces them.
2. In PhysPlot choose **File → Reload Config Modules**.
3. In Simple Mode, panel **1. Data Importer**, open **Data Loader** and pick the loader by its `title`. With `FILE_EXTENSIONS`, **Auto Loader** also works.
4. Click **Import Data** and choose a real file.
5. Compare the table with the file: column names, number of rows, the first and last values. Check the role dropdowns above the table. Then plot it in **3. Plotter Module** with **Generate Plot**.
6. Repeat with two or three other files, including an unusual one (another scan range, a single scan).

Optional check in Python, in the environment where PhysPlot is installed (for example a Jupyter notebook). It shows the full error traceback if something fails. Replace the two names with the real ones:

```python
from physplot.loaders.plugins import PluginLoader
from physplot.user_paths import user_plugin_dir

loader_file = user_plugin_dir("data_importers") / "acme_uvvis_loader.py"
dataset = PluginLoader(loader_file).load(r"C:\path\to\methylene_blue.uvs")
print(dataset.dataframe)
print(dataset.describe_columns()[["column_name", "suggested_role", "dtype"]])
```

`suggested_role` shows the roles from `DEFAULT_COLUMN_ROLES`; every `dtype` should be `float64`.

## If PhysPlot shows an error

The user will paste the error message or describe what they see. Find the matching case, fix the cause, and send the complete corrected file.

| What the user sees | Likely cause and what to change |
|---|---|
| The loader is not in the **Data Loader** menu after **Reload Config Modules** | Wrong folder, a name ending in `.py.txt`, a syntax error, an import of a package that is not installed, or no `load_data` function. PhysPlot skips such files and writes the reason only to its console. Check the syntax, limit imports to the Rules, and ask the user to run the Python check above for the full error. |
| The loader is still missing although the syntax and imports are right | Top-level code raised an error, for example a `NameError` or `KeyError`, so PhysPlot skipped the file. Keep only imports and constant definitions at top level; move all other code into functions. |
| *Import failed* with the loader's own `ValueError` text | This file differs from the sample. Ask for its first 30-50 lines and extend `load_data` to handle both layouts. |
| *Import failed*: `could not convert string to float: '0,0412'` | Decimal commas. Replace `","` with `"."` in each cell after splitting. |
| *Import failed*: `could not convert string to float: ...` with header text, `list index out of range`, or a bare name in quotes | Header lines, a different separator, or trailing text reached the number parsing. Detect where the data starts and ends, and raise a clear `ValueError` instead. |
| *Import failed*: `setting an array element with a sequence ... inhomogeneous shape` | Rows of different lengths. Pad short rows with `float("nan")` or cut long ones. |
| *Import failed*: `Unknown column role '...'` | A `DEFAULT_COLUMN_ROLES` entry is not one of the allowed strings. |
| Columns named `Column 1`, `Column 2`, ... | An array was returned without `COLUMN_NAMES`, or with fewer names than columns. |
| Wrong or missing roles | `DEFAULT_COLUMN_ROLES` is not in column order, or two columns share a single-column role such as `"Y"`. |
| **Auto Loader** does not use the loader, or the Import Data dialog does not list the files | The extension is one that built-in loaders read (see above), or `FILE_EXTENSIONS` is not a plain list of strings. Choose the loader in **Data Loader** instead. |
| Garbled characters such as `Â°` or `Ã©` in names, or `UnicodeDecodeError` | Encoding. Use `"utf-8-sig"` with a `latin-1` fallback, or `"utf-16"` when the file starts with `FF FE`. |
| Values off by a factor of 10, 1000, ... | A scale factor in the header, a unit prefix, or thousands separators. Ask the user which values are correct and apply the factor in `load_data`. |
| A saved sequence or bulk run fails with `Unknown column '...'` | Column names depend on the file, or `load_data` returns a DataFrame and the file also sets `COLUMN_NAMES`. Use fixed names, set in one place only. |
