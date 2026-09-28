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

The current GUI header is branded: LSF and PhysLab logos are on the far left,
the PhysPlot wide logo stays centered, and the Simple/Advanced switcher stays
on the right. Help/About links live in the native menu bar.

## Repository Structure

```text
physplot/                  Backend API, datasets, loaders, plotters, steps
physplot_gui/              PyQt6 desktop GUI
physplot_gui/figure_editor/ Built-in Figure Editor (PyQt6; started from FigureForge, MIT)
config/data_importers/     Data Importer loaders (title + load_data)
config/transformations/    Mathematical Transformation functions (transform)
config/plotter_modules/    Plotter Modules (plot() or BasePlotter subclasses)
config/plot_types/         Plot Type presets (JSON) for existing plotters
config/protocol_modules/   Reusable protocol fragments (WORKFLOW_STEPS)
config/sequences/          Complete reusable protocol sequence Python files
config/pipelines/          Reusable transformation pipeline JSON files
config/templates/          Figure template JSON files
config/fit_functions/      Legacy curve-fit model plugins
config/figureforge_fit_styles/  FigureForge/Simple Mode fit-style presets
config/figureforge_plugins/     Figure Editor (FigureForge) plugins
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

The UI Reference, Sequence Walkthrough and Video Tutorials are written as wiki pages
in `wiki/`. After editing them, regenerate their Read the Docs copies in `docs/ui/`.
A line of YouTube thumbnail links in a wiki page becomes embedded players in the docs
(the `youtube` directive in `docs/_ext/youtube.py`, also usable in `.rst` pages):

```bash
python scripts/sync_wiki_to_docs.py
```

Use the local ``.venv`` for direct PyQt smoke checks:

```bash
QT_QPA_PLATFORM=offscreen .venv/bin/python -m physplot_gui
```

On macOS, prefer Python 3.12 for local GUI work:

```bash
/opt/homebrew/bin/python3.12 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/python -m physplot_gui
```

Every `config/` subfolder is user-editable. At startup PhysPlot searches
`Documents/PhysPlot/config/<folder>/` first (override with `PHYSPLOT_USER_DIR`)
and falls back to the bundled copy; the Windows installer seeds the Documents
tree from `config/`. *File > Reload Config Modules* re-scans without a restart.
Discovery lives in `physplot/user_paths.py`, `physplot/plotting_modules/user_modules.py`,
`physplot/workflow.py`, and `physplot_gui/app/plugin_discovery.py`.

## Design Rules

- Preserve the table-first layout.
- Reusable modules belong under `config/`, never in new root-level folders.
  New module kinds must be discovered through `plugin_search_dirs()` so the
  Documents copy keeps working without a reinstall.
- Do not duplicate backend logic in the GUI.
- Keep Simple Mode to three panels: Data Importer, Transformation, Plotter Module.
- Build Protocol is the editable sequence source of truth.
- Run Sequence applies an existing sequence to folders; plot type/configuration
  comes from `PlotModuleStep` entries in the sequence.
- The native menu bar should contain File, Protocol, View, Plot, and Help.
- Help should link to the Read the Docs site, GitHub repository, issue tracker,
  and About dialog.
- If protocol rows are deleted, the remaining sequence should be replayable
  and reflected in the table.
- Generated workflow files must be normal Python that can run in notebooks or
  headless CLI workflows.
- Every plot opens in a PhysPlot plot window; its **Advanced Styling…** button (or
  the **Advanced Figure Editor** tick box) opens the built-in Figure Editor
  (`physplot_gui/figure_editor`) in the same process, on the same figure. Keep it
  PyQt6 only (no PySide6) and free of FigureForge branding; keep its `LICENSE`.
- Basic Plotter plot types come from `physplot/plotting_modules/gallery.py`
  (`PLOT_CATEGORIES`, grouped like the Matplotlib gallery). Each type lists the
  roles it reads; the GUI limits the table's role menus to them and fills them in.
  Other plotters declare `role_requirements`. Keep `scatter` the default type.
- Column roles live in several places that must stay in step: `VALID_ROLES` and
  `_normalize_role` (`physplot/core/dataset.py`), `PhysPlot.set_roles`
  (`physplot/api.py`), `ROLE_FIELDS` (`physplot/steps/set_role.py`), `ROLE_OPTIONS`
  (`physplot_gui/widgets/column_role_header.py`), and `ROLE_LABELS` / `_role_key`
  (`physplot_gui/app/main_window.py`). Clearing a role records
  `SetRoleStep({"ignore": column})`.

## Package Identity

- PyPI distribution name: `python-physplot`
- Import package: `physplot`
- GUI entry points: `physplot-gui`, `python-physplot-gui`
- CLI entry points: `physplot`, `python-physplot`
