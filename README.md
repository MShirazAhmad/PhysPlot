# PhysPlot

<p align="center">
  <img src="physplot/inc/PhysPlotWide.png" alt="PhysPlot logo" width="420">
</p>

> **⚠️ Experimental Development Branch**
>
> This branch is under active development and may contain incomplete features, breaking changes, or significant bugs.
>
> **Latest Stable Release**
>
> https://github.com/MShirazAhmad/PhysPlot/tree/PhysPlot-v2.0.0

---

## Overview

PhysPlot is a scientific plotting and workflow automation application for researchers, engineers, and students who require fast, reproducible, publication-quality figures without relying on large commercial software packages.

Originally conceived in 2019 following a suggestion from **Dr. Muhammad Sabieh Anwar**, PhysPlot has evolved into a modular scientific plotting platform supporting graphical workflows, reusable plotting protocols, and automated batch processing.

The workflow is intentionally simple:

```text
Load Data
      ↓
Assign Column Roles
      ↓
Apply Transformations
      ↓
Generate Publication-Quality Plot
      ↓
Save Workflow
      ↓
Reuse or Run in Bulk
```

---

# Features

- Scientific plotting desktop application built with PyQt
- Publication-quality figure generation
- Spreadsheet-style data editor
- CSV, TXT, Excel, Nanoindentation, and DataFrame support
- Dynamic data loaders
- Dynamic mathematical transformation modules
- Modular plotting architecture
- Figure templates
- Reusable workflow protocols
- Automated batch processing
- Headless command-line execution
- Python API
- FigureForge-powered figure editor
- Plugin-friendly architecture

---

# Installation

## Option 1 — Precompiled Application (Recommended)

Precompiled releases are available for both **macOS** and **Windows**.

Download the latest release from:

https://github.com/MShirazAhmad/PhysPlot/releases

---

## Option 2 — Install from PyPI

```bash
python -m pip install python-physplot
```

Launch the graphical application:

```bash
physplot-gui
```

Launch the command-line interface:

```bash
physplot --version
```

---

## Option 3 — Run from Source

Clone the repository:

```bash
git clone https://github.com/MShirazAhmad/PhysPlot.git
cd PhysPlot
```

Create a virtual environment:

```bash
/opt/homebrew/opt/python@3.12/bin/python3.12 -m venv .venv
source .venv/bin/activate
```

Verify Python:

```bash
python --version
```

Expected output:

```text
Python 3.12.x
```

Upgrade pip and install the project requirements:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Launch PhysPlot:

```bash
physplot-gui
```

Alternatively:

```bash
python -m physplot_gui
```

---

# Tested Environment

PhysPlot has been tested with:

| Component | Version |
|------------|---------|
| Python | 3.12.x (Homebrew) |
| Operating System | macOS (Apple Silicon) |

The tested package versions are maintained in **requirements.txt**.

Installing dependencies directly from **requirements.txt** is recommended to ensure compatibility and reproducible behavior.

---

# Documentation

Complete project documentation is available online.

- Documentation
  https://physplot.readthedocs.io/

- GitHub Repository
  https://github.com/MShirazAhmad/PhysPlot

- Issue Tracker
  https://github.com/MShirazAhmad/PhysPlot/issues

Additional project documentation:

- Maintainer Project Guide
- Contributing Guide
- Trademark and Branding

---

# GUI Workflow

The graphical interface follows a table-first workflow.

### Simple Mode

1. Import Data
2. Apply Mathematical Transformations
3. Select Plot Module
4. Apply Figure Template
5. Generate Plot
6. Edit Figure
7. Export Figure

### Advanced Mode

#### Build Protocol

Create, edit, save, and reuse Python workflow protocols.

#### Run Sequence

Execute saved workflows on entire folders for automated batch processing.

---

# Python API

PhysPlot can also be used directly from Python.

```python
from physplot import PhysPlot

pp = PhysPlot()

pp.load("data.csv")
pp.set_roles(
    x="Time",
    y="Voltage"
)

fig = pp.plot_with_module(
    "basic",
    "scatter"
)
```

---

# Command-Line Examples

Show version:

```bash
physplot --version
```

Run a workflow:

```bash
physplot run-workflow workflow.py \
    --input data.csv \
    --output outputs/run
```

Run batch processing:

```bash
physplot run-bulk workflow.py \
    --input-folder data \
    --output-folder outputs/batch
```

---

# Supported Data Sources

- CSV
- TXT
- Microsoft Excel
- Nanoindentation datasets
- Pandas DataFrames

---

# License

PhysPlot source code is licensed under the **PolyForm Noncommercial License 1.0.0**.

You may:

- Study the source code
- Fork the repository
- Modify the software for noncommercial purposes
- Submit improvements through pull requests

Commercial use requires prior written permission from the project originator.

Documentation, tutorials, screenshots, and educational material are licensed under the **Creative Commons Attribution–NonCommercial 4.0 International (CC BY-NC 4.0)** unless otherwise noted.

The **PhysPlot** name, logo, application icon, GUI branding, and visual identity remain reserved by the project originator. Modified versions must not be represented as official PhysPlot releases.

For contribution policies and branding guidelines, see:

- `CONTRIBUTING.md`
- `TRADEMARK.md`