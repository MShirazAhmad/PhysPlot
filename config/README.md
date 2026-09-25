# PhysPlot config folder

Everything in this folder is a reusable, user-editable module. The Windows
installer copies this tree to `Documents\PhysPlot\config\`; on every platform
PhysPlot searches `Documents/PhysPlot/config/<folder>/` first and falls back
to the bundled copy. Add, edit, or delete files there and use
*File > Reload Config Modules* (or restart) to pick them up. No reinstall or
recompile is needed. Set `PHYSPLOT_USER_DIR` to relocate the user folder.

| Folder | Contents | Used by |
| --- | --- | --- |
| `data_importers/` | Data Importer loaders (`title`, `load_data(path)`) | Simple Mode loader menu, `LoadDataStep` |
| `transformations/` | Mathematical Transformation functions (`transform(values)`) | Simple Mode function menu, `TransformColumnStep` |
| `plotter_modules/` | Plotter Modules (`plot(dataset, plot_type, config)` or `BasePlotter` subclasses) | Simple Mode plotter menu, `PlotModuleStep` |
| `plot_types/` | Plot Type presets (JSON) for existing plotters | Plot Type menu, `PlotModuleStep` |
| `protocol_modules/` | Reusable protocol fragments (`WORKFLOW_STEPS`) | Protocol > Insert Protocol Module |
| `sequences/` | Complete runnable sequences | Import/Export Sequence.py, Run Sequence |
| `pipelines/` | Transformation pipeline JSON | Advanced pipeline import/export |
| `templates/` | Figure templates (JSON) | Simple Mode Template menu, Figure Editor "Save as Template" |
| `fit_functions/` | Legacy curve-fit models (`KIND`, `DEGREE`, `function`) | Legacy curve-fit menu |
| `figureforge_fit_styles/` | LSQ fit-style presets (JSON) | Simple Mode Fit Style menu (Reload button) |
| `figureforge_plugins/` | Figure Editor (FigureForge) plugins | Copied into FigureForge when the editor opens |
| `curve_fit_functions.py`, `ui_config.json` | Legacy GUI configuration | Legacy GUI |
