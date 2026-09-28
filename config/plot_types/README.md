# Plot Types

Named plot-type presets for existing plotter modules. Each JSON file adds an
entry to the **Plot Type** menu of the plotter it names and merges its
`config` into the plot call, so a lab can share a fixed variant of a plot
without writing a new plotter.

```json
{
  "plotter_id": "example_xy",
  "plot_type": "calibration_curve",
  "base_plot_type": "xy_markers",
  "description": "Absorbance standards against concentration",
  "config": {"x_label": "Concentration (mg/L)", "y_label": "Absorbance (a.u.)", "grid": true}
}
```

`config` takes effect only in plotters that read those options. The built-in
plotters (`basic`, `line`, `errorbar`, ...) read none, so a preset for them only
adds a name: the bundled `scatter_publication.json` draws the same as `scatter`.
`example_xy` reads `figsize`, `label`, `x_label`, `y_label` and `grid`.

Fields:

- `plotter_id`: id of an existing plotter (`basic`, `line`, `errorbar`, a
  user plotter from `config/plotter_modules`, ...).
- `plot_type`: the new name shown in the menu and stored in
  `PlotModuleStep(plot_type=...)`.
- `base_plot_type`: the plotter's own plot type that actually renders.
- `config`: options merged underneath any explicit configuration.

A file may also contain a JSON list of several presets. The per-user copy in
`Documents/PhysPlot/config/plot_types/` is searched first.

To have an AI assistant write a preset, attach `AI_GUIDE.md` from this folder to
the chat (see `AI_GUIDE.md` for what else to attach).
