$$\text{\color{red}\Huge Warning: Experimental Branch}$$
$$\text{\color{red}\Huge Significant Bugs Or Breaking Changes May Be Present}$$

$$\text{\color{green}\Large Latest Stable Branch:}$$ https://github.com/MShirazAhmad/PhysPlot/tree/PhysPlot-v2.0.0

<p align="center">
  <img src="physplot/inc/PhysPlotWide.png" alt="PhysPlot logo" width="420">
</p>

PhysPlot began in 2019 with an idea suggested by my mentor, Dr. Muhammad Sabieh Anwar: to develop a lightweight but capable plotting tool for researchers who need to generate publication-ready graphs quickly, without depending on system-heavy software such as MATLAB or Origin.

I started building PhysPlot while I was learning Python. What began as a small learning project gradually evolved into a research-focused plotting application.

# PhysPlot: Advanced Plotting Made Simple

PhysPlot is a scientific plotting and workflow automation package with a
desktop GUI for publication-ready 2D plots. It supports CSV, TXT, Excel, and
DataFrame inputs; spreadsheet-style editing; column role assignment; modular
plotters; reusable Python protocol sequences; and headless bulk runs.

The guiding idea is simple:

```text
load data -> assign column roles -> transform -> plot -> save protocol -> run in bulk
```

The GUI is table-first, while the backend remains importable and scriptable for
notebooks, command-line runs, and automated batches.

## Features

- PyQt6 desktop GUI with Simple and Advanced modes
- Spreadsheet-style table with editable cells, column roles, copy/paste, rename,
  row/column deletion, and scrollable Excel-like behavior
- Dynamic loader discovery from built-in loaders and local `fileloader/` modules
- Dynamic function discovery from backend transformations and local `functions/`
  modules
- Modular plotter registry, including basic, histogram, error-bar, overlay,
  subplot-grid, nanoindentation, and Oliver-Pharr plotter modules
- Build Protocol table/code editor for reproducible Python workflows
- Run Sequence bulk runner that uses plot modules and configuration already
  stored in the protocol sequence
- Headless CLI support for single-file and folder workflows
- Pip-ready package published as `python-physplot`

## Installation

Install the published package:

```bash
python -m pip install python-physplot
```

Launch the GUI:

```bash
physplot-gui
```

The distribution name is `python-physplot`; the import package remains `physplot`.

Run the backend command-line interface:

```bash
physplot --version
physplot run-workflow workflow.py --input data.csv --output outputs/run
physplot run-bulk workflow.py --input-folder data/ --output-folder outputs/batch
```

You can also use PhysPlot from Python:

```python
from physplot import PhysPlot

pp = PhysPlot()
pp.load("data.csv")
pp.set_roles(x="Time", y="Voltage")
fig = pp.plot_with_module("basic", "scatter")
```

## GUI Workflow

Launch:

```bash
physplot-gui
```

Simple Mode is organized into three panels:

1. **Data Importer**: select a loader and import/export data.
2. **Apply Mathematical Transformation**: create derived columns from table
   columns.
3. **Plotter Module**: select a registered plotter and plot type.

Advanced Mode has two tabs:

- **Build Protocol**: review the operation sequence as a table, edit it as
  Python code, import/export `Sequence.py`, and apply the current sequence.
- **Run Sequence**: apply the current or imported sequence to an input folder.
  Plot mode and formatting are defined by `PlotModuleStep` entries inside the
  sequence, not by separate bulk-run controls.

## Documentation

- [Codex and Maintainer Project Guide](docs/CODEX_PROJECT_GUIDE.md)
- [Contributing](CONTRIBUTING.md)
- [Trademark and Branding](TRADEMARK.md)

The project guide includes the working structure, design philosophy, backend
contracts, testing checklist, and annotated sample protocol drafts.

## Quick Start (from source)

Clone the repository:

```bash
git clone https://github.com/MShirazAhmad/PhysPlot.git
cd PhysPlot
```

Create and activate a virtual environment:

```bash
python -m venv .venv
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

On Windows (PowerShell):

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Run PhysPlot:

```bash
physplot-gui
```

Alternative module entry point:

```bash
python -m physplot --version
```

Build local PyPI artifacts:

```bash
python -m build
python -m twine check dist/*
```

The expected package files are:

```text
dist/python_physplot-<version>-py3-none-any.whl
dist/python_physplot-<version>.tar.gz
```

## License, Tutorials, and Contributions

PhysPlot source code is licensed under the PolyForm Noncommercial License 1.0.0. You may fork PhysPlot, study the code, make noncommercial improvements, and submit revisions back through pull requests.

Commercial use is not allowed without prior written permission from the project originator.

Documentation, screenshots, tutorials, website text, walkthroughs, and educational media are licensed under Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0) unless otherwise stated. Noncommercial tutorials and educational guides are welcome.

The PhysPlot name, logo, app icon, GUI branding, and official visual identity are reserved by the project originator. Unofficial forks or modified builds must not be presented as official PhysPlot releases.

Only pull requests merged by the maintainer are official PhysPlot revisions. For details, see [CONTRIBUTING.md](CONTRIBUTING.md) and [TRADEMARK.md](TRADEMARK.md).
