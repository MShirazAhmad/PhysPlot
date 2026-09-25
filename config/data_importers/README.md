# Data Importers

Personal file loaders shown in the Simple Mode **Data Loader** menu. A loader
file defines a non-empty `title` string and `load_data(file_path)` returning a
DataFrame or 2D table. Optional `COLUMN_NAMES`, `DEFAULT_COLUMN_ROLES`, and
`PLOTTERS` let a loader name columns, preset roles, and ship its own plotter.
See `default_loader.py` and `docs/CODEX_PROJECT_GUIDE.md` (Draft 4).
