# Extending PhysPlot

PhysPlot's everyday building blocks are plain Python or JSON files in `config/`.
Put your own in `Documents/PhysPlot/config/<folder>/` (**File → Open Config Folder**),
then choose **File → Reload Config Modules**. A file there overrides a bundled file
with the same name.

| Folder | What it holds |
| --- | --- |
| `transformations/` | Mathematical Transformation functions (`transform(values)`) |
| `data_importers/` | File loader plugins (`load_data(file_path)`) |
| `fit_functions/` | Curve-fit models |
| `templates/` | Plot style templates |
| `plotter_modules/` | Extra plotters for the Plotter Module menu |
| `plot_types/` | Named plot-type presets (JSON) |
| `protocol_modules/` | Reusable protocol snippets (**Protocol → Insert Protocol Module**) |
| `sequences/` | Saved `Sequence.py` files |
| `figureforge_plugins/`, `figureforge_fit_styles/` | Figure Editor actions and fit-line styles |

## Transformation plugins

```python
"""15_normalize.py: normalize a column to 0–1."""

import numpy as np

DISPLAY_NAME = "Normalize 0-1"   # label in the Function menu


def transform(values, floor=0.0):
    values = np.asarray(values, dtype=float)
    span = np.nanmax(values) - np.nanmin(values)
    return np.full_like(values, floor) if span == 0 else (values - np.nanmin(values)) / span + floor
```

- `values` is a copy of the input column as floats, with `NaN` for blank or text
  cells. Editing it in place is safe.
- Return one value per row: a list, an array, a Series or an `(n, 1)` column. A single
  number fills every row.
- The first line of the docstring appears as the menu tooltip.
- Sequences record the **file stem** (`15_normalize`), so renaming a file breaks
  saved protocols that use it.
- Don't name a file after a built-in (`log.py`, `multiply.py`, …) and don't call
  `sys.exit()` or run `argparse` on import. Such files are skipped.
- Extra parameters (`floor` above) can be set in the step's `params` in the Code view.

More detail: [Replayable Plugin Transformations](Replayable-Plugin-Transformations).

## File loader plugins

```python
"""pipe_loader.py: files with 'wavelength|intensity' lines."""

title = "Pipe Loader"                        # name in the Data Loader menu
FILE_EXTENSIONS = [".pip"]                   # Auto Loader, replays and bulk runs use this loader for .pip
COLUMN_NAMES = ["Wavelength", "Intensity"]
DEFAULT_COLUMN_ROLES = ["X-axis", "Y-axis"]  # X-axis, Y-axis, X error, Y error, group, label


def load_data(file_path):
    rows = [line.split("|") for line in open(file_path) if "|" in line]
    return [[float(a), float(b)] for a, b in rows]   # or a pandas DataFrame
```

- `load_data` returns a DataFrame or a 2D table.
- `COLUMN_NAMES` and `DEFAULT_COLUMN_ROLES` name the columns and preset their roles.
- `FILE_EXTENSIONS` lets **Auto Loader** pick this plugin for those files, so they
  load the same way in the GUI, in replayed and exported sequences, and in bulk runs.
  Without it, choose the loader in **Data Loader** by hand.
- A loader can also offer its own plotters with `PLOTTERS` (see `config/data_importers/README.md`).

The bundled `oes_hrf_loader.py` is a complete example.
