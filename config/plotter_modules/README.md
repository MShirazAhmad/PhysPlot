# Plotter Modules

Drop-in plotter modules that appear in the **Plotter Module** menu of Simple
Mode and can be replayed headlessly through `PlotModuleStep(plotter_id=...)`.

PhysPlot scans this folder at startup (and on *File > Reload Config Modules*).
The per-user copy in `Documents/PhysPlot/config/plotter_modules/` is searched
first; a file with the same name there overrides the bundled one.

A module file can define any one of:

1. A `BasePlotter` subclass (see `physplot.plotting_modules.BasePlotter`).
2. A `PLOTTERS` list of plotter instances or dictionaries with
   `plotter_id`, `name`, `plot_types` and `function` keys.
3. A plain `plot(dataset, plot_type=None, config=None)` function together
   with `PLOTTER_ID`, `NAME` and `PLOT_TYPES` constants.

The function receives the active `Dataset` (`dataset.dataframe`,
`dataset.column_roles`, `dataset.metadata`) and must return a Matplotlib
`Figure`. See `example_xy_plotter.py` for a minimal template.

Core built-in plotters remain in `physplot/plotting_modules` so backend imports
stay stable.
