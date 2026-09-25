# Advanced Mode and Bulk Automation: Implementation Plan

Handoff document for a coding agent (written 2026-09-25 after a full review of
the `indevelopment` working tree). Read `AGENTS.md` and
`docs/CODEX_PROJECT_GUIDE.md` first. Work phase by phase, in order; each phase
is independently shippable and ends with the verification commands in the
last section passing.

## Ground rules

- Backend first. Every feature below is a backend capability in `physplot/`
  with a thin GUI binding in `physplot_gui/`. The GUI never reimplements
  logic (`AGENTS.md`, Design Rules).
- Sequences stay plain Python. `WORKFLOW_STEPS` / `build_workflow()` files
  must keep running in notebooks and through `physplot run-workflow`.
- Do not break the public step API: `WorkflowStep.apply(physplot,
  allow_column_number_fallback=False)` and `to_code()` in
  `physplot/steps/base.py`. Add to it; do not rename.
- Build Protocol (`state.pp.workflow` plus `state.timeline` rows in
  `physplot_gui/app/main_window.py`) is the single source of truth. Rows are
  derived from steps by `MainWindow._sequence_rows_from_steps`; never store
  state only in the table widget.
- Keep Simple Mode at three panels. Everything here lives in Advanced Mode
  (`Build Protocol` and `Run Sequence` tabs) or the backend/CLI.
- Tests run offscreen: `QT_QPA_PLATFORM=offscreen`. `MainWindow._error`
  prints instead of showing a modal dialog when the platform is offscreen;
  assert on `window.last_error` in tests.
- No new root-level folders. Reusable files go under `config/`.

## Current state (what exists, where)

| Concern | Location | Notes |
| --- | --- | --- |
| Step classes | `physplot/steps/*.py` | `LoadDataStep`, `SetRoleStep`, `TransformColumnStep`, `CalculateColumnStep`, `RenameColumnStep`, `DeleteRowsStep`, `DeleteColumnsStep`, `SetCellValueStep`, `PlotModuleStep` |
| Sequence execution | `PhysPlot.run_workflow` in `physplot/api.py` | Plain loop, no per-step status |
| Sequence load/save | `physplot/workflow.py`, `PhysPlot.save_workflow/load_workflow` | `load_workflow_source` execs Python |
| Bulk runner | `physplot/bulk.py::run_folder` | Serial, stops on first error, extension filter only, fixed export set |
| CLI | `physplot/__main__.py` | `run-workflow`, `run-bulk` |
| Build Protocol GUI | `physplot_gui/panels/recorder_mode_panel.py` (`SequenceBuilder`), `MainWindow.delete_timeline_step`, `apply_sequence_code`, `_run_current_sequence` | Table + code views; delete-only editing; every change replays all steps |
| Run Sequence GUI | `physplot_gui/panels/bulk_panel.py`, `MainWindow.run_bulk_workflow` | Three path fields, synchronous run on the GUI thread |
| Protocol modules | `physplot/workflow.py::discover_protocol_modules`, `MainWindow.insert_protocol_module` | Appends steps from `config/protocol_modules` |
| Tests | `tests/test_protocol_sequence_editor.py`, `tests/test_sequence_workflow.py`, `tests/test_bulk_column_number_fallback.py`, `tests/test_plot_module_workflow.py` | Use as templates |

## Phase 1: Per-step execution status and rerun-from-step

Status: done (2026-09-25). Implemented as below; later phases build on it.

- `physplot/execution.py`: `StepResult` (`index`, `step`, `status`,
  `error`, `duration_s`, `step_name`), `execute_steps`, `Snapshot`,
  `SnapshotStore` (keeps the earliest snapshot plus the latest ones up to
  20), `cumulative_fingerprints`, `first_failure`.
- `PhysPlot.run_workflow_detailed(steps, *, start_index=0,
  allow_column_number_fallback=False, raise_on_error=False,
  keep_snapshots=True)`. Execution always stops at the first failure;
  `raise_on_error` only controls whether it is re-raised. (The draft name
  `stop_on_error` was replaced because it did not describe that.)
- `PhysPlot.rerun_from(index, steps=None, *, allow_column_number_fallback,
  raise_on_error=False)` restores the latest snapshot at or before `index`
  whose earlier-step fingerprint still matches; raises `RuntimeError` if none.
- `PhysPlot.run_workflow` wraps `execute_steps(raise_on_error=True)` without
  snapshots, so bulk runs pay no copy cost. `PhysPlot.last_results` is set by
  every run.
- `Dataset.copy()` in `physplot/core/dataset.py`.
- GUI: Status column (index 4; Delete moved to 5) in
  `recorder_mode_panel.py`, row context menu "Rerun from this step",
  `MainWindow.timeline_row_status`, `rerun_from_timeline_step`,
  `_row_workflow_indices`, `_current_step_results`. `MainWindow.last_error`
  records the last error for tests.
- Tests: `tests/test_step_results.py`, three new tests in
  `tests/test_protocol_sequence_editor.py`.
- Docs: `docs/user_guide/protocol_sequences.rst`.

Known limitation: Simple Mode plugin transformations from
`config/transformations` are not recorded as workflow steps, so they never
appear in statuses or replays. Tracked separately.

## Phase 2: Editable steps (parameters, reorder, enable/disable)

Goal: users iterate on a protocol from the table without touching Python.

Backend:

1. Add to `WorkflowStep` (non-abstract, defaults provided):
   `enabled: bool = True`, `describe() -> dict` returning editable fields as
   `{name: {"value": ..., "type": "str|int|float|bool|column|choice",
   "choices": [...]}}`, and `update(**fields)`. Implement `describe/update`
   in every step under `physplot/steps/`. `to_code()` must emit
   `enabled=False` when disabled, and `apply` must no-op when disabled.
2. `PhysPlot.move_step(old_index, new_index)` and
   `PhysPlot.insert_step(index, step)`.

GUI:

3. Step editor dialog (`physplot_gui/widgets/step_editor.py`): built from
   `describe()`; `column` fields become a combo of current table columns,
   `choice` fields a combo, others line edits with validation. Double-click
   on a table row opens it. On accept, call `update(**fields)`, rebuild rows
   with `_sequence_rows_from_steps`, and run Phase 1 detailed replay.
4. Enable/disable checkbox column at the far left of the table.
5. Reorder: "Move up" / "Move down" in the row context menu (drag-and-drop is
   optional; the context menu is the requirement). `LoadDataStep` rows stay
   pinned first.
6. "Insert Protocol Module" and a new "Insert Step..." action should insert
   after the selected row, not only append. Add an `index` parameter to
   `MainWindow.insert_protocol_module`.

Acceptance:

- Editing `TransformColumnStep.function_name` in the dialog updates the code
  view and the replay result.
- A disabled step is skipped, shows `skipped`, and round-trips through
  Export Sequence.py / Import Sequence.py.
- Moving a `SetRoleStep` below a `PlotModuleStep` produces the expected
  failure status rather than an exception dialog.

## Phase 3: Robust bulk runs with a results summary

Goal: folder runs of hundreds of files finish, report per-file status, and
produce one combined results table.

Backend (`physplot/bulk.py`):

1. Extend `run_folder` with keyword arguments: `pattern="*"` (glob),
   `recursive=False`, `continue_on_error=True`, `workers=1`,
   `progress=None` (callable receiving `(done, total, path, status)`),
   `cancel=None` (callable returning `True` to stop).
2. Return a `BulkReport` with `entries: list[BulkEntry]` (`path`,
   `output_dir`, `status`, `error`, `fit_parameters: dict`, `duration_s`) and
   `summary_path`. Write `summary.csv` in the output folder: one row per
   input file with status, error text, and one column per fit parameter
   (`pp.fit_result["parameters"]` flattened; empty when no fit).
3. Write `bulk.log` in the output folder with full tracebacks.
4. `workers > 1` uses `concurrent.futures.ProcessPoolExecutor`; each worker
   builds its own `PhysPlot`. Matplotlib must use the `Agg` backend inside
   workers.
5. CLI: expose `--pattern`, `--recursive`, `--workers`, `--stop-on-error` on
   `run-bulk` in `physplot/__main__.py`; print the summary path and counts.

GUI (`bulk_panel.py`, `MainWindow.run_bulk_workflow`):

6. Run in a `QThread` (or `QThreadPool` runnable) with a progress bar, a
   live per-file list (path, status), and a Cancel button. Never block the
   GUI thread.
7. Add fields: file pattern, recursive checkbox, continue-on-error checkbox,
   workers spin box.
8. After completion, show a results table from `summary.csv` inside the Run
   Sequence tab with an "Open Output Folder" button.

Acceptance:

- A folder with one corrupt file and nine good ones yields nine outputs, one
  `failed` row in `summary.csv`, and the GUI stays responsive throughout.
- `physplot run-bulk seq.py --input-folder d/ --output-folder o/ --workers 4`
  produces identical `summary.csv` content to `--workers 1` (ordering by
  path).
- New `tests/test_bulk_report.py` covers continue-on-error, pattern filter,
  and summary columns for a sequence containing an `lsq_fit` config.

## Phase 4: Dry-run validation

Goal: know before running whether a sequence fits a file or folder.

Backend (`physplot/validation.py`):

1. `validate_sequence(steps, dataset) -> list[Issue]` where `Issue` has
   `step_index`, `severity` (`error|warning`), `message`. Checks, without
   executing plots: referenced columns exist (respecting column-number
   fallback), roles required by the plotter are satisfiable
   (`BasePlotter` gains an optional `required_roles` tuple; default empty),
   transformation names exist in `list_transforms()` or
   `config/transformations`, plotter ids and plot types exist in
   `PlotterRegistry.default()`.
2. `validate_folder(steps, folder, loader="auto", pattern="*")` loads only
   the header of each file (first 50 rows) and aggregates issues per file.
3. `PlotModuleStep` should declare column requirements by delegating to
   the plotter's `required_roles`.

GUI:

4. "Validate" button on both Build Protocol and Run Sequence tabs. Results
   appear as the Phase 1 status column (`warning` in amber) or, for folders,
   as the per-file list in the Run Sequence tab.

Acceptance:

- Validating the bundled `config/protocol_modules/normalize_and_plot.py`
  against a two-column CSV yields no errors; against a one-column CSV yields
  an error on the transform step naming column 2.

## Phase 5: Run-time sequence parameters

Goal: a sequence author defines a few parameters; a student fills them in
without editing code.

Backend:

1. Sequence files may define `PARAMETERS = {"fit_min": {"value": 2.0,
   "type": "float", "label": "Fit range start"}, ...}`. Steps reference them
   with `Param("fit_min")` markers (`physplot/steps/params.py`), resolved
   at `run_workflow` time through `PhysPlot.parameters: dict`.
2. `load_workflow` returns steps and also exposes `PARAMETERS`
   (`load_workflow_with_parameters(path) -> (steps, parameters)`); the plain
   `load_workflow` stays unchanged.
3. `workflow_script()` emits the `PARAMETERS` block and `Param(...)` calls
   when present, so export/import round-trips.
4. CLI: `--param name=value` (repeatable) on `run-workflow` and `run-bulk`.

GUI:

5. A "Parameters" strip above the Build Protocol table, generated from
   `PARAMETERS`, editable, applied before every replay and bulk run.
6. Step editor (Phase 2) offers "bind to parameter" for numeric fields.

Acceptance:

- Changing `fit_min` in the strip changes the fit result without editing
  the sequence; exporting and re-importing preserves the binding.

## Phase 6: Sequence snapshots and diff

Goal: keep good protocol versions and see what changed.

1. `PhysPlot.snapshot_workflow(label)` writes
   `Documents/PhysPlot/config/sequences/history/<name>/<timestamp>_<label>.py`
   (use `physplot.user_paths.writable_plugin_dir("sequences")`).
2. GUI: "Snapshot..." and "History..." actions in the Protocol menu. History
   dialog lists snapshots, shows a unified diff (`difflib`) of the generated
   code against the current sequence, and offers "Restore".
3. Auto-snapshot before Import Sequence.py and Clear Sequence.

Acceptance:

- Clear Sequence followed by History > Restore returns the exact prior
  steps and rows.

## Out of scope for this plan

Fit uncertainties, residual plots, units, instrument importers, journal
presets, and module packaging are separate plans. Do not fold them in.

## Verification for every phase

```bash
QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -q
QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -q tests/test_protocol_sequence_editor.py
.venv/bin/python -m build --sdist --wheel --outdir /tmp/physplot-pkg
.venv/bin/python -m twine check /tmp/physplot-pkg/*
```

Also render the GUI offscreen and confirm the Advanced tab still fits in the
300 to 430 px band set in `physplot_gui/app/mode_manager.py`; widen that band
only if the new results table needs it, and keep Simple Mode untouched.

Update `docs/CODEX_PROJECT_GUIDE.md` (Build Protocol and Run Sequence
sections) and `docs/user_guide/` at the end of each phase.
