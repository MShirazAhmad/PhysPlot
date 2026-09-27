# Plotter Modules: guide for AI assistants

> **PhysPlot users:** attach this file to a chat with any AI assistant (ChatGPT, Claude, Gemini, Copilot, ...), together with a sample of your data (a data file, or its first 30-50 lines) and, if you have one, a picture or sketch of the plot you want. Then describe what you want. The assistant replies with one complete file: save it in `Documents/PhysPlot/config/plotter_modules/` and choose **File → Reload Config Modules** in PhysPlot. Step-by-step help: https://physplot.readthedocs.io/en/latest/extensions/ai_assistant.html

## Your task

Write one complete Python file that adds a plotter to PhysPlot, a desktop plotting
application for scientists. PhysPlot holds the data in a table; the user gives columns
roles (X, Y, Y Error, ...) above the table. In the Simple Mode panel **3. Plotter Module**
the user chooses your plotter in **Plotter Module** and one of its variants in
**Plot Type**, and clicks **Generate Plot**. PhysPlot calls your `plot()` function and
shows the Matplotlib figure it returns. Saved sequences replay the same call without a
window as `PlotModuleStep(plotter_id=..., plot_type=..., config=...)`, also in bulk runs
over folders of files.

## Ask the user first

Ask in one short message, and only for what is still missing:

1. The column names and roles (X, Y, any Y Error, X Error, Group), or a sample data file.
2. What the plot should show, and which variants (plot types) they want.
3. Axis labels with units, and the title.
4. A picture or sketch of the target figure: markers or lines, log axes, size, colours.
5. Whether it will run over many files in a bulk run.

Choose sensible defaults for minor details and mention them in your reply.

## The file PhysPlot expects

Save location: `Documents/PhysPlot/config/plotter_modules/<file_name>.py`, a lowercase
name with underscores. A file named like a bundled one (`example_xy_plotter.py`) replaces
it. Use this form: four module-level names and one function.

| Name | Type | Meaning |
|---|---|---|
| `PLOTTER_ID` | `str` | Unique id, stored in saved sequences. |
| `NAME` | `str` | Label in the **Plotter Module** menu. |
| `CATEGORY` | `str` | Optional group name; use `"User"`. |
| `PLOT_TYPES` | `list[str]` | Entries of the **Plot Type** menu, in order; the first is the default. |
| `plot(dataset, plot_type=None, config=None)` | function | Draws and returns a `matplotlib.figure.Figure`. |

`plot()` receives:

- `dataset`: the active table. Treat it as read-only.
  - `dataset.dataframe`: a pandas `DataFrame`; column names are the table headers as
    strings, for example `"Time (s)"`. Cells can be numbers, text or `NaN`.
  - `dataset.column_roles`: a `dict` from column name to role, exactly one of `"X"`, `"Y"`,
    `"X Error"`, `"Y Error"`, `"Group"`, `"Label"`, `"Batch Key"`, `"Fit Weight"`,
    `"Ignore"`. `"X"`, `"Y"`, `"X Error"`, `"Y Error"` and `"Fit Weight"` are each on at
    most one column.
  - `dataset.name`: normally the data file name without its extension.
  - `dataset.metadata`: a `dict` of loader information; read it with `.get()`.
- `plot_type`: one of `PLOT_TYPES`, or `None` (then use `PLOT_TYPES[0]`).
- `config`: a `dict`, often empty. Options come from a Plot Type preset JSON in
  `config/plot_types/` or from `PlotModuleStep(config={...})` in a sequence file. When
  the user ticks **LSQ fit**, it also holds `"lsq_fit"`; ignore that key. Simple Mode has
  no fields for your options, so the defaults must give a finished plot.

PhysPlot shows the returned figure in a window titled
`PhysPlot - <plotter_id>: <plot type>` with the Matplotlib toolbar (only the built-in
Basic Plotter opens in the Figure Editor). A selected **Template** restyles each axes by
position. **LSQ fit** fits the raw Y role column against the X role column and draws the
line on `fig.axes[0]`. Headless and bulk runs save the figure as `plot.png`, without the
Template.

Other accepted forms, only if the user asks: a `physplot.plotting_modules.BasePlotter`
subclass (attributes `plotter_id`, `name`, `category`, `supported_plot_types`,
`supported_dataset_types = ("*",)`, method `plot(self, dataset, plot_type=None,
config=None)`), or a `PLOTTERS` list of dicts with `plotter_id`, `name`, `plot_types` and
`function` for several plotters in one file. PhysPlot uses `PLOTTERS` first, then
subclasses, then `plot()`, so never mix forms in one file.

## Rules

1. Reply with exactly one complete, self-contained `.py` file. It cannot import other
   files from the config folder.
2. Import only `numpy`, `pandas`, `scipy`, `matplotlib` and the Python standard library.
   A missing package (such as `seaborn` or `plotly`) makes PhysPlot skip the whole file.
   Never import PyQt, `physplot_gui` or other GUI code.
3. Use the object-oriented Matplotlib API: a new `fig, ax = plt.subplots(...)` on every
   call, draw on `ax`, end with `fig.tight_layout()` and `return fig`. Never call
   `plt.show()`, `plt.savefig()`, `fig.savefig()`, `plt.close()`, `matplotlib.use()` or
   state functions such as `plt.plot()`; never change `plt.rcParams` (it restyles every plot).
4. No file access, network access, subprocesses, `input()` or `print()`. All data comes
   from `dataset`.
5. Find columns through `dataset.column_roles`, not hard-coded names, unless the user
   asks for fixed names. Then the plot works for any file and after columns are renamed.
6. If a needed role is missing, there are too few numeric rows, or `plot_type` is
   unknown, raise `ValueError` with a clear sentence that says what to change. PhysPlot
   shows only the message text, in a "Plot failed" box. Never return `None`.
7. Convert values with `pd.to_numeric(..., errors="coerce")`, drop rows with `NaN`, and
   sort by X before drawing lines or taking derivatives. Never modify `dataset`.
8. `PLOTTER_ID` uses lowercase letters, digits and underscores, is unique, and must not
   be a built-in id: `basic`, `histogram`, `scatter`, `line`, `errorbar`, `overlay`,
   `subplot_grid`, `nanoindentation`, `oliver_pharr`, `example_xy`. Sequences store the
   id and the plot type names, so never change them once the user has used them.
9. `PLOT_TYPES` is always a list, even for one entry: `["default"]`, never `"default"`.
10. Read every option with `config.get("key", default)`, list the keys in the module
    docstring, and ignore unknown keys. Values from JSON presets arrive as lists, not tuples.
11. Always label both axes (default: the column names, which usually carry the units)
    and set a title (default: `dataset.name`). Draw the main curve on the first axes. Do
    not fix axis limits or names that fit only one file, unless the user asks.
12. Keep the top level to imports, constants and functions. PhysPlot imports the file
    again each time it lists plotters or draws a plot.

## Complete working example

File `derivative_plotter.py`, with two plot types: `normalized` (Y divided by its largest
magnitude) and `derivative` (dY/dX, labelled for example `d(Current)/d(Voltage) (mA/V)`).

```python
"""Derivative Plotter: normalized curve and dY/dX of the Y column against X.

Headless replay: PlotModuleStep(plotter_id="derivative", plot_type="derivative", config={})
Optional config keys: title, x_label, y_label, grid, marker, figsize,
normalize_by ("max" or "range"), smooth_points (moving average before dY/dX).
"""

import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PLOTTER_ID = "derivative"
NAME = "Derivative Plotter"
CATEGORY = "User"
PLOT_TYPES = ["normalized", "derivative"]


def _role_column(dataset, role):
    """Return the name of the column that has this role, or None."""
    for column, column_role in dataset.column_roles.items():
        if column_role == role and column in dataset.dataframe.columns:
            return column
    return None


def _name_and_unit(column):
    """Split 'Current (mA)' into ('Current', 'mA'); no unit gives None."""
    match = re.match(r"^\s*(.*?)\s*[\(\[]([^\)\]]+)[\)\]]\s*$", str(column))
    return (match.group(1) or str(column), match.group(2)) if match else (str(column), None)


def plot(dataset, plot_type=None, config=None):
    config = dict(config or {})
    plot_type = plot_type or PLOT_TYPES[0]
    if plot_type not in PLOT_TYPES:
        raise ValueError(f"Derivative Plotter has no plot type '{plot_type}'. Use one of: {', '.join(PLOT_TYPES)}.")

    x_col = _role_column(dataset, "X")
    y_col = _role_column(dataset, "Y")
    if x_col is None or y_col is None:
        raise ValueError("Derivative Plotter needs one column with role X and one with role Y.")

    frame = dataset.dataframe
    data = pd.DataFrame({"x": pd.to_numeric(frame[x_col], errors="coerce"),
                         "y": pd.to_numeric(frame[y_col], errors="coerce")}).dropna()
    # Sort by X and average repeated X values, so dY/dX is defined everywhere.
    data = data.groupby("x", as_index=False)["y"].mean()
    if len(data) < 3:
        raise ValueError(f"Derivative Plotter needs at least 3 rows with numbers in '{x_col}' and '{y_col}'.")
    x = data["x"].to_numpy(dtype=float)
    y = data["y"].to_numpy(dtype=float)
    x_name, x_unit = _name_and_unit(x_col)
    y_name, y_unit = _name_and_unit(y_col)

    if plot_type == "normalized":
        if config.get("normalize_by", "max") == "range":
            span = y.max() - y.min()
            if span == 0:
                raise ValueError(f"Cannot normalize '{y_col}': all values are equal.")
            values = (y - y.min()) / span
        else:
            peak = np.max(np.abs(y))
            if peak == 0:
                raise ValueError(f"Cannot normalize '{y_col}': all values are zero.")
            values = y / peak
        default_y_label = f"{y_name} (normalized)"
    else:
        window = int(config.get("smooth_points", 1))
        if window > 1:
            y = pd.Series(y).rolling(window, center=True, min_periods=1).mean().to_numpy()
        values = np.gradient(y, x)
        unit = f"{y_unit or 1}/{x_unit}" if x_unit else y_unit
        default_y_label = f"d({y_name})/d({x_name})" + (f" ({unit})" if unit else "")

    fig, ax = plt.subplots(figsize=tuple(config.get("figsize", (6.0, 4.0))))
    ax.plot(x, values, marker=config.get("marker", "o"), markersize=3, linestyle="-")
    if plot_type == "derivative":
        ax.axhline(0.0, color="0.6", linewidth=0.8)
    ax.set_xlabel(config.get("x_label", x_col))
    ax.set_ylabel(config.get("y_label", default_y_label))
    ax.set_title(config.get("title", str(dataset.name)))
    if config.get("grid", True):
        ax.grid(True, linestyle=":", alpha=0.6)
    fig.tight_layout()
    return fig
```

## Reply format

```
Reply with:
1. The file name on its own line, for example `derivative_plotter.py`.
2. The complete file in one code block. Never shorten it or leave placeholders such as "..." or "rest unchanged".
3. Two or three short sentences: what the module does and anything the user should check.
If you change the file after the user reports an error, send the complete corrected file again.
```

## How the user tests it

1. Save the file in `Documents/PhysPlot/config/plotter_modules/` (**File → Open Config
   Folder**); the name must end in `.py`, not `.txt`. Choose **File → Reload Config Modules**.
2. Load a data file and set the roles (for example X and Y) above the table.
3. In **3. Plotter Module** choose the plotter's `NAME` in **Plotter Module**, a plot type
   in **Plot Type**, and click **Generate Plot**.
4. Check the window `PhysPlot - <plotter_id>: <plot type>`: axis labels, units, and a few
   values worked out by hand. Try every plot type and a second data file.

Optional check without the window, run with PhysPlot's Python (script installs:
`%LOCALAPPDATA%\PhysPlot\venv\Scripts\python.exe` on Windows, `~/.physplot/venv/bin/python`
on macOS). Replace `derivative` and the columns with your plotter's id and data:

```python
import pandas as pd
from physplot import PhysPlot
from physplot.plotting_modules import PlotterRegistry

registry = PlotterRegistry.default()
print(registry.get("derivative").name, registry.list_plot_types("derivative"))

pp = PhysPlot()
pp.load(pd.DataFrame({"Voltage (V)": [0.0, 0.1, 0.2, 0.3, 0.4],
                      "Current (mA)": [0.0, 0.2, 0.9, 2.5, 6.0]}), loader="dataframe")
pp.set_roles(x="Voltage (V)", y="Current (mA)")
for plot_type in registry.list_plot_types("derivative"):
    pp.plot_with_module("derivative", plot_type).savefig(f"check_{plot_type}.png")
    print("saved", f"check_{plot_type}.png")
```

A line starting with `Skipping plotter module` gives the reason a file was not loaded.

## If PhysPlot shows an error

The user pastes the message. Find the cause below, fix it, and send the complete file.

| What the user sees | Cause and fix |
|---|---|
| The plotter is not in the **Plotter Module** menu | The file is in another folder, ends in `.txt`, or failed to import (syntax error, or a package outside rule 2). PhysPlot prints `Skipping plotter module <path>: <reason>` only to the console; the headless check shows it. |
| Another plotter disappeared, or the menu shows the wrong one | Two files use the same `PLOTTER_ID`, or it equals a built-in id. Choose a new unique id. |
| **Plot Type** shows single letters | `PLOT_TYPES` is a string. Make it a list. |
| `Plot failed:` followed by your own `ValueError` text | Working as intended. Tell the user what to change, for example which role to assign. |
| `Plot failed: 'Temperature'` (only a quoted name) | A `KeyError`: the code uses a column name that is not in the table. Use roles (rule 5). |
| `could not convert string to float` or `unsupported operand type` | Text cells reached the maths. Use `pd.to_numeric(..., errors="coerce")` and `dropna()`. |
| `'Axes' object has no attribute 'set_canvas'` | `plot()` returned an `Axes`. Return the `Figure`. |
| An empty plot window, no `plot.png` after a bulk run, or `No plot axes are available for the fitted line.` | `plot()` returned `None` or a figure without axes. End with `return fig`. |
| The LSQ fit line does not match the curve | LSQ fit always uses the raw Y and X columns. Untick it for transformed plots such as derivatives. |
| `Unknown plotter module '<id>'.` in a sequence or bulk run | The file is missing on this computer or its `PLOTTER_ID` changed. Restore the file or the old id. |
| `... has no plot type '<name>'` in a sequence | A plot type was renamed or removed. Restore the old name in `PLOT_TYPES`. |
