# Getting Started

## Install

PhysPlot needs Python 3.11–3.13. The upper limit comes from the Figure Editor
(FigureForge), which also keeps numpy below 2.

```bash
python -m pip install python-physplot
```

From a source checkout, use a virtual environment:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
```

On Windows, the installer (`PhysPlot-<version>-Windows-Setup.exe`) installs the app
and copies the sample data to `Documents\PhysPlot\test_data`.

## Launch

```bash
physplot-gui
```

or, from a checkout, `python -m physplot_gui`. The first start creates your editable
settings folder, `Documents/PhysPlot/config/`. Anything you put there (loaders,
transformations, templates, plotter modules) overrides the bundled copy with the same
file name.

## A tour of the window

The window below has an XRD scan loaded (`test_data/XRD/schema1.5_scan.XRDML`).

![PhysPlot window with numbered regions](images/getting-started/start_01_window_tour.png)

1. **Mode switcher.** **Simple** shows the three everyday panels. **Advanced** shows
   the protocol builder (**Build Protocol**) and bulk runs (**Run Sequence**).
2. **Column headers.** Each header shows the column number and name (`1: 2Theta`).
   Double-click a header to rename the column. Right-click it to rename, copy,
   paste or delete the column.
3. **Role row.** Each column's dropdown sets its role: `Ignore`, `X`, `Y`,
   `X Error`, `Y Error`, `Group`, `Label`, `Batch Key` or `Fit Weight`. Loaders
   suggest roles. Here `2Theta` is X and `Intensity` is Y.
4. **Data cells.** Values can be edited, pasted (⌘V / Ctrl+V) or cleared.
   Right-click a row number to copy, paste or delete rows. Every edit is recorded
   in the protocol.
5. **1. Data Importer.** Pick a **Data Loader** (keep **Auto Loader** for most files),
   then **Import Data**. **Export Data** saves the table, its column metadata and the
   protocol to a folder.
6. **2. Mathematical Transformation.** Makes a new column from an existing one
   (see the [GUI Walkthrough](GUI-Walkthrough#3-transform-a-column)).
7. **3. Plotter Module.** Chooses the plotter, plot type, style template and an
   optional least-squares fit, then **Generate Plot**.
8. **Status bar.** Shows the last action or error (hover for the full text) and the
   row count, column count and file name.

### Menus

| Menu | Items |
| --- | --- |
| **File** | Import Data…, Import Folder…, Export Data…, Open Config Folder, Reload Config Modules |
| **Protocol** | Import Sequence.py…, Export Sequence.py…, Apply This Sequence (Ctrl+R), Copy Sequence Code, Clear Sequence, Insert Protocol Module |
| **View** | Simple Mode (Ctrl+1), Advanced Mode (Ctrl+2) |
| **Plot** | Generate Plot (Ctrl+G), Update Integrated Preview |
| **Help** | Documentation, GitHub Repository, Report Issues or Bugs, About PhysPlot |

**Reload Config Modules** re-scans `config/` without restarting, so a new loader or
transformation file shows up straight away. **Import Folder…** currently only selects
a folder. To process every file in a folder, use
[Run Sequence](Bulk-Runs-and-Headless).

### Small screens

The window can be as narrow as about 910 px. When it is narrower than the three
Simple Mode panels, the panel row scrolls sideways instead of pushing the window
off-screen:

![Simple Mode on a narrow window with a horizontal scrollbar](images/getting-started/start_02_narrow_window.png)

1. **Scrollbar.** Drag it (or scroll sideways) to reach the Plotter Module controls.

## Next

Follow the **[GUI Walkthrough](GUI-Walkthrough)** for a complete session.
