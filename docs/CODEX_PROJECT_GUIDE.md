# PhysPlot Project Guide

This guide is written for maintainers, Codex sessions, and contributors who
need to understand the whole project before changing it.

## Working Philosophy

PhysPlot should feel simple to a researcher and predictable to a developer.

- The spreadsheet is the master visual control.
- Column roles are explicit and visible above the table.
- Every meaningful GUI action should map to a backend workflow step when it
  affects reproducibility.
- Saved protocol sequences are real Python, not opaque project files.
- Bulk automation must replay the same sequence that the user built in the GUI.
- Plot mode, plotter module, and plot configuration belong in the sequence. Run
  Sequence should not invent a separate plotting choice.
- The GUI must call backend APIs rather than reimplementing loaders,
  transformations, plotting, fitting, workflows, or bulk logic.

## Project Structure

```text
PhysPlot/
  pyproject.toml                Package metadata for python-physplot
  README.md                     Public project overview and installation
  AGENTS.md                     Quick instructions for Codex/agent sessions
  docs/
    CODEX_PROJECT_GUIDE.md      Maintainer guide, structure, examples
  physplot/
    api.py                      Public PhysPlot facade
    bulk.py                     Folder/batch runner
    workflow.py                 Import workflow steps from .py source
    __main__.py                 CLI entry point
    core/
      dataset.py                DataFrame wrapper, roles, metadata
      transformations.py        Registered column transformations
      formula.py                Formula evaluation
      column_resolver.py        Name/number column resolution
    loaders/
      base.py                   Built-in auto/csv/txt/excel/dataframe loaders
    plotting_modules/
      base.py                   BasePlotter contract
      registry.py               PlotterRegistry and default registration
      *_plotter.py              Modular plotter implementations
    steps/
      *.py                      Replayable workflow step classes
    inc/
      *.png                     Logo and icon assets
  physplot_gui/
    __main__.py                 python -m physplot_gui entry point
    app/
      runner.py                 GUI launcher
      main_window.py            Main orchestration window
      mode_manager.py           Simple/Advanced stacked panel switcher
      gui_state.py              Shared GUI state across modes
      plugin_discovery.py       fileloader/functions discovery
    panels/
      simple_mode_panel.py      Three-panel Simple Mode
      advanced_mode_panel.py    Build Protocol / Run Sequence tabs
      recorder_mode_panel.py    Sequence table/code and run sequence layout
      bulk_panel.py             Folder runner controls
    widgets/
      central_table.py          Spreadsheet table, editing, copy/paste
      column_role_header.py     Role dropdown header
      mode_switcher.py          Simple/Advanced switcher
      status_bar.py             Bottom status bar
  fileloader/                   User-discoverable personal file loaders
  functions/                    User-discoverable personal transform functions
  tests/                        Backend and GUI smoke tests
```

## Main User Flows

### Simple Mode

Simple Mode has exactly three panels below the table:

1. Data Importer
2. Apply Mathematical Transformation
3. Plotter Module

It is intended for everyday use: load data, assign roles, transform columns,
choose an optional template, generate a plot, edit it in the Figure Editor, and
export.

### Build Protocol

Build Protocol is the editable protocol sequence. It has two views:

- Table view: readable operation list with delete buttons.
- Code view: generated Python source that can be edited and applied back to the
  table.

Important behavior:

- `Import Sequence.py` loads workflow steps from a Python file.
- `Export Sequence.py` writes the current protocol as Python.
- `Apply This Sequence` runs the current sequence as shown.
- `Apply Code to Table` appears only in Code view and rebuilds the protocol
  table from the edited Python source.
- Deleting a row removes those workflow steps and immediately replays the
  revised protocol so the spreadsheet reflects the edited sequence.

### Run Sequence

Run Sequence is for bulk automation. It should stay intentionally small:

- Input Folder
- Sequence File, optional; blank means use the current Build Protocol sequence
- Output Folder
- Run Bulk Workflow

Plot choice is not a Run Sequence option. If a sequence contains:

```python
PlotModuleStep(
    plotter_id="basic",
    plot_type="scatter",
    config={},
)
```

then bulk execution uses that exact plotter step. If the sequence does not
contain a plot step, bulk execution exports data/metadata but does not invent a
new plot.

## Backend Contracts

Use the public facade:

```python
from physplot import PhysPlot

pp = PhysPlot()
pp.load("data.csv", loader="auto")
pp.set_roles(x="Time", y="Voltage")
pp.transform("Voltage", "multiply", output="Voltage_mV", factor=1000)
pp.plot_with_module("basic", "scatter")
pp.export("outputs/run")
```

GUI actions should map to:

```text
Import Data       -> pp.load(...)
Set column role   -> pp.set_roles(...)
Transform column  -> pp.transform(...)
Calculate formula -> pp.calculate(...)
Fit model         -> pp.fit(...)
Generate Plot     -> pp.plot_with_module(...) and Figure Editor for Basic Plotter
Export            -> pp.export(...)
Bulk Run          -> pp.run_bulk(...)
```

## Workflow Step Pattern

Each workflow step should be:

- A small class under `physplot/steps/`
- Serializable through `to_code()`
- Replayable through `apply(physplot, allow_column_number_fallback=False)`
- Safe for headless runs

Example:

```python
TransformColumnStep(
    input_column="Voltage",
    input_column_number=2,
    function_name="multiply",
    output="Voltage_mV",
    output_column_number=5,
    params={"factor": 1000},
)
```

The column number fields are fallback anchors for headless bulk runs where
different files use slightly different column names.

## Annotated Protocol Drafts

### Draft 1: Generic CSV to Basic Scatter Plot

```python
from __future__ import annotations

"""A minimal PhysPlot protocol.

Run inside a notebook:
    pp = run()

Run from CLI:
    physplot run-workflow sequence.py --input data.csv --output outputs/run
"""

from physplot import PhysPlot
from physplot.steps import LoadDataStep, PlotModuleStep, SetRoleStep

WORKFLOW_STEPS = [
    # The GUI records this when the user imports data. In bulk mode this step is
    # skipped because each input-folder file becomes the active dataset.
    LoadDataStep(
        path="test_data/sample_linear.csv",
        loader="auto",
        dataset_name="sample_linear",
    ),

    # Roles are what plot modules use to find X, Y, errors, groups, and labels.
    SetRoleStep(
        roles={"x": "Time", "y": "Voltage", "yerr": "Error", "group": "Group"},
    ),

    # Plot mode and protocol are defined here, not in the bulk runner UI.
    PlotModuleStep(
        plotter_id="basic",
        plot_type="scatter",
        config={},
    ),
]


def build_workflow():
    return list(WORKFLOW_STEPS)


def run(input_path=None, output_dir="outputs/sequence_run", loader="auto"):
    pp = PhysPlot()
    steps = build_workflow()
    if input_path:
        pp.load(input_path, loader=loader)
        steps = [step for step in steps if not isinstance(step, LoadDataStep)]
    pp.run_workflow(steps, allow_column_number_fallback=True)
    pp.export(output_dir)
    return pp
```

### Draft 2: Transform Then Plot

```python
from physplot.steps import LoadDataStep, PlotModuleStep, SetRoleStep, TransformColumnStep

WORKFLOW_STEPS = [
    LoadDataStep(path="data.csv", loader="auto", dataset_name="experiment"),
    SetRoleStep(roles={"x": "Time", "y": "Voltage"}),

    # Creates a derived column that appears in the table and can become a role.
    TransformColumnStep(
        input_column="Voltage",
        input_column_number=2,
        function_name="normalize_max",
        output="Voltage_norm",
        output_column_number=5,
        params={},
    ),

    # Reassign Y to the derived column before plotting.
    SetRoleStep(roles={"x": "Time", "y": "Voltage_norm"}),
    PlotModuleStep(plotter_id="basic", plot_type="line", config={}),
]
```

### Draft 3: Nanoindentation Visualization

```python
from physplot.steps import LoadDataStep, PlotModuleStep, SetRoleStep

WORKFLOW_STEPS = [
    LoadDataStep(path="nano.csv", loader="csv", dataset_name="nano_test"),

    # These role names are optional for nanoindentation plotters, which also use
    # aliases like "Depth (nm)", "Load (mN)", "h", and "P".
    SetRoleStep(roles={"x": "Depth (nm)", "y": "Load (mN)"}),

    PlotModuleStep(
        plotter_id="nanoindentation",
        plot_type="load_depth",
        config={},
    ),
]
```

### Draft 4: Personal File Loader With Loader-Owned Plotter

Personal file loaders live in `fileloader/`. A loader can define column names,
default roles, and allowed plotter metadata. The GUI discovers it automatically.

```python
# fileloader/my_instrument_loader.py
import pandas as pd

DISPLAY_NAME = "My Instrument Loader"
COLUMN_NAMES = ["Time", "Signal", "Error", "Sample"]
DEFAULT_COLUMN_ROLES = ["X", "Y", "Y Error", "Group"]


def load_data(path):
    """Return a DataFrame or 2D table-like object."""
    return pd.read_csv(path)


def publication_plot(dataset, plot_type="publication_ready", config=None):
    """Optional loader-owned plotter callable.

    The returned Matplotlib figure is stored as pp.last_figure and exported by
    pp.export(...). Keep custom styling here when a lab or instrument needs a
    fixed publication format.
    """
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    ax.plot(dataset.dataframe["Time"], dataset.dataframe["Signal"])
    ax.set_xlabel("Time")
    ax.set_ylabel("Signal")
    return fig


PLOTTERS = [
    {
        "plotter_id": "my_instrument_publication",
        "name": "My Instrument Publication Plot",
        "plot_types": ["publication_ready"],
        "callable": publication_plot,
    }
]
```

## Testing Checklist

Before marking work production-ready:

```bash
python -m pytest
QT_QPA_PLATFORM=offscreen python -m pytest tests/test_protocol_sequence_editor.py
rm -rf build dist python_physplot.egg-info
python -m build
python -m twine check dist/*
```

Expected result:

- All backend tests pass.
- GUI smoke tests pass or skip only when PyQt6 is unavailable.
- `twine check` passes for both wheel and source distribution.

## Release Checklist

1. Confirm `pyproject.toml` version and package metadata.
2. Run tests and package checks.
3. Confirm `dist/python_physplot-*.whl` and `.tar.gz` were freshly built.
4. Push the release branch.
5. Tag only after the maintainer approves the exact release commit.
