# Codex Guide for PhysPlot

This file is the quick handoff for Codex or any other coding agent working in
this repository. The detailed project guide lives in
[`docs/CODEX_PROJECT_GUIDE.md`](docs/CODEX_PROJECT_GUIDE.md).

## Product Shape

PhysPlot is a table-first scientific plotting application:

1. Load data into the central spreadsheet.
2. Assign column roles with the dropdowns above the table.
3. Apply transformations that become replayable workflow steps.
4. Generate plots through backend plotter modules.
5. Export or bulk-run the same protocol sequence headlessly.

The GUI is only an orchestration layer. Scientific logic belongs in the backend
package under `physplot/`.

## Repository Structure

```text
physplot/                  Backend API, datasets, loaders, plotters, steps
physplot_gui/              PyQt6 desktop GUI
fileloader/                User/plugin-style personal file loaders
functions/                 User/plugin-style personal transform functions
tests/                     Backend and GUI smoke tests
docs/                      Maintainer and user-facing project documentation
```

## Development Commands

```bash
python -m pip install -e ".[dev]"
python -m pytest
QT_QPA_PLATFORM=offscreen python -m pytest tests/test_protocol_sequence_editor.py
rm -rf build dist python_physplot.egg-info
python -m build
python -m twine check dist/*
```

When the local GUI-only environment exists, use it for direct PyQt smoke checks:

```bash
QT_QPA_PLATFORM=offscreen .gui-venv/bin/python -m physplot_gui
```

## Design Rules

- Preserve the table-first layout.
- Do not duplicate backend logic in the GUI.
- Keep Simple Mode to three panels: Data Importer, Transformation, Plotter Module.
- Build Protocol is the editable sequence source of truth.
- Run Sequence applies an existing sequence to folders; plot type/configuration
  comes from `PlotModuleStep` entries in the sequence.
- If protocol rows are deleted, the remaining sequence should be replayable
  and reflected in the table.
- Generated workflow files must be normal Python that can run in notebooks or
  headless CLI workflows.

## Package Identity

- PyPI distribution name: `python-physplot`
- Import package: `physplot`
- GUI entry points: `physplot-gui`, `python-physplot-gui`
- CLI entry points: `physplot`, `python-physplot`

