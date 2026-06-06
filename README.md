<p align="center">
  <img src="physplot/inc/PhysPlotWide.png" alt="PhysPlot logo" width="420">
</p>

PhysPlot began in 2019 with an idea suggested by my mentor, Dr. Muhammad Sabieh Anwar: to develop a lightweight but capable plotting tool for researchers who need to generate publication-ready graphs quickly, without depending on system-heavy software such as MATLAB or Origin.

I started building PhysPlot while I was learning Python. What began as a small learning project gradually evolved into a research-focused plotting application.

# PhysPlot: Advanced Plotting Made Simple

PhysPlot is a scientific plotting software with a graphical user interface, designed to produce publication-ready 2D plots. It supports vector and bitmap output, including PDF, Postscript, SVG and EPS. It allows data to be imported from text, CSV and Excel files and It can export data in text format. Datasets can also be entered within the program, and new datasets can be created via the manipulation of existing datasets using mathematical expressions.

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

## License, Tutorials, and Contributions

PhysPlot source code is licensed under the PolyForm Noncommercial License 1.0.0. You may fork PhysPlot, study the code, make noncommercial improvements, and submit revisions back through pull requests.

Commercial use is not allowed without prior written permission from the project originator.

Documentation, screenshots, tutorials, website text, walkthroughs, and educational media are licensed under Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0) unless otherwise stated. Noncommercial tutorials and educational guides are welcome.

The PhysPlot name, logo, app icon, GUI branding, and official visual identity are reserved by the project originator. Unofficial forks or modified builds must not be presented as official PhysPlot releases.

Only pull requests merged by the maintainer are official PhysPlot revisions. For details, see [CONTRIBUTING.md](CONTRIBUTING.md) and [TRADEMARK.md](TRADEMARK.md).
