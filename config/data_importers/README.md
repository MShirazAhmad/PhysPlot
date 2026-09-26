# Data Importers

Personal file loaders shown in the Simple Mode **Data Loader** menu. A loader
file defines a non-empty `title` string and `load_data(file_path)` returning a
DataFrame or 2D table. Optional `COLUMN_NAMES`, `DEFAULT_COLUMN_ROLES`, and
`PLOTTERS` let a loader name columns, preset roles, and ship its own plotter.
Optional `FILE_EXTENSIONS` (for example `[".ras"]`) lets **Auto Loader**, replayed
sequences and bulk runs open that file type with this loader automatically.
Worked examples: `rigaku_ras_loader.py` (XRD `.ras`), `ta_instruments_loader.py`
(TGA/DSC text exports) and `jcamp_dx_loader.py` (JCAMP-DX spectra), explained step by
step in `docs/extensions/fileloading.rst`. See also `default_loader.py` and
`docs/CODEX_PROJECT_GUIDE.md` (Draft 4).
