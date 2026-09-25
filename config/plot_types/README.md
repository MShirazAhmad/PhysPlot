# Plot Types

Named plot-type presets for existing plotter modules. Each JSON file adds an
entry to the **Plot Type** menu of the plotter it names and merges its
`config` into the plot call, so a lab can share a fixed protocol such as
"scatter with publication grid" without writing a new plotter.

```json
{
  "plotter_id": "basic",
  "plot_type": "scatter_publication",
  "base_plot_type": "scatter",
  "description": "Scatter plot with grid and larger markers",
  "config": {"grid": true, "marker_size": 40}
}
```

Fields:

- `plotter_id`: id of an existing plotter (`basic`, `line`, `errorbar`, a
  user plotter from `config/plotter_modules`, ...).
- `plot_type`: the new name shown in the menu and stored in
  `PlotModuleStep(plot_type=...)`.
- `base_plot_type`: the plotter's own plot type that actually renders.
- `config`: options merged underneath any explicit configuration.

A file may also contain a JSON list of several presets. The per-user copy in
`Documents/PhysPlot/config/plot_types/` is searched first.
