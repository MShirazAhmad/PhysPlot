# Plot Type Presets: guide for AI assistants

> **PhysPlot users:** attach this file to a chat with any AI assistant (ChatGPT, Claude, Gemini, Copilot, ...), together with the plotter module file the preset is for (if it is your own plotter from `Documents/PhysPlot/config/plotter_modules/`) and the names of the plotter and plot type you use now. Then describe what you want. The assistant replies with one complete file: save it in `Documents/PhysPlot/config/plot_types/` and choose **File → Reload Config Modules** in PhysPlot. Step-by-step help: https://physplot.readthedocs.io/en/latest/extensions/ai_assistant.html

## Your task

Write one JSON file that adds a named entry to the **Plot Type** menu of an existing
plotter in PhysPlot (Simple Mode panel **3. Plotter Module**). When the user chooses
that entry, PhysPlot draws one of the plotter's own plot types (`base_plot_type`) and
passes the preset's `config` options to the plotter's `plot()` function. Sequences save
the preset name as `PlotModuleStep(plot_type="<preset name>")`, so a lab can reuse a
fixed plot recipe in every run.

## Ask the user first

Ask in one short message, and only for what is still missing:

1. Which plotter (menu name or `plotter_id`) and which of its plot types to start from.
2. If it is their own plotter: the plotter's `.py` file, to see which options it reads.
3. What should differ: axis labels and units, title, figure size, grid, markers, ...
4. The new name for the **Plot Type** menu, and whether they want one preset or several.

## The file PhysPlot expects

Save location: `Documents/PhysPlot/config/plot_types/<file_name>.json`, UTF-8, strict
JSON. The file holds one preset object, or a JSON array (list) of preset objects.

| Key | Required | Meaning |
|---|---|---|
| `plotter_id` | yes | Id of an existing plotter, exactly as in the table below. |
| `plot_type` | yes | The new menu entry; also stored in saved sequences. |
| `base_plot_type` | yes | One of the plotter's own plot types; this is what is drawn. |
| `description` | no | Note for people reading the file; PhysPlot does not show it. |
| `config` | no | Object of options passed to the plotter's `plot()`. |

How PhysPlot uses it:

- The entry follows the plotter's own plot types. A preset for a plotter that is not
  installed is silently ignored.
- Merging is `{**preset_config, **step_config}`: keys in a sequence's
  `PlotModuleStep(config={...})` win over the preset, key by key (not deep).
- The recorded step stores only the preset name. Every replay reads the preset file
  again: editing it changes later replays, and deleting it breaks them.

Plotters, their own plot types, and the `config` keys they read:

| Plotter menu name | `plotter_id` | Own plot types | `config` keys read |
|---|---|---|---|
| Basic Plotter | `basic` | `scatter`, `line`, `scatter_line` | none |
| Scatter Plotter | `scatter` | `scatter` | none |
| Line Plotter | `line` | `line` | none |
| Error Bar Plotter | `errorbar` | `x_y_errorbar`, `y_errorbar` | none |
| Histogram Plotter | `histogram` | `histogram`, `density_histogram` | none |
| Overlay Plotter | `overlay` | `overlay_by_group`, `overlay_by_dataset` | none |
| Subplot Grid Plotter | `subplot_grid` | `subplots_by_group`, `subplots_by_dataset` | none |
| Nanoindentation Plotter | `nanoindentation` | `load_depth`, `hardness_depth`, `modulus_depth`, `stiffness_depth`, `contact_depth` | none |
| Oliver-Pharr Plotter | `oliver_pharr` | `load_depth_with_unloading_fit`, `unloading_fit`, `contact_stiffness_fit`, `area_function`, `hardness_summary`, `modulus_summary` | none |
| Example XY Plotter | `example_xy` | `xy_markers`, `xy_line` | `figsize` (list `[w, h]` in inches), `label` (legend text), `x_label`, `y_label`, `grid` (`true`/`false`, default `true`) |
| A user plotter | its `PLOTTER_ID` | its `PLOT_TYPES` | each `config.get("<key>", ...)` in its `plot()` |

Built-in plotters ignore `config`: a preset for them only adds a new name for an existing
plot type. For styling, say so and suggest a figure Template (`config/templates/`, saved
from the Figure Editor) or a new plotter module (`config/plotter_modules/AI_GUIDE.md`).

## Rules

1. Reply with exactly one `.json` file. No Python, no comments, no trailing commas;
   double quotes; `true`, `false` and `null` in lowercase.
2. `plotter_id` must match an installed plotter exactly (case matters).
3. `base_plot_type` must be one of that plotter's own plot types from the table or its
   `PLOT_TYPES`, never another preset name.
4. `plot_type` is new: lowercase letters, digits and underscores, not equal to any plot
   type the plotter already has, and not used by another preset file. A preset with an
   existing name silently changes that plot type. Never rename it once sequences use it.
5. Put only keys in `config` that the plotter reads. Unknown keys are ignored silently.
   Never invent keys; if the plotter cannot do what the user wants, say so.
6. Use the value types the plotter expects: numbers as numbers, booleans as `true` or
   `false` (the string `"false"` counts as true), sizes as lists such as `[5, 4]`.
7. Do not put `lsq_fit` in `config`; PhysPlot ignores it there. LSQ fits come from the
   **LSQ fit** controls in Simple Mode.

## Complete working example

File `calibration_curve.json`: Example XY Plotter markers with fixed labels and a smaller figure.

```json
{
  "plotter_id": "example_xy",
  "plot_type": "calibration_curve",
  "base_plot_type": "xy_markers",
  "description": "Absorbance standards against concentration, 5 x 4 inch figure",
  "config": {
    "x_label": "Concentration (mg/L)",
    "y_label": "Absorbance (a.u.)",
    "label": "Standards",
    "grid": true,
    "figsize": [5, 4]
  }
}
```

List form, file `iv_presets.json`: two presets in one file. The second only adds a lab
name for a Basic Plotter type, so it has no `config`.

```json
[
  {"plotter_id": "example_xy", "plot_type": "iv_curve", "base_plot_type": "xy_line",
   "description": "Current-voltage sweep as a line without grid",
   "config": {"x_label": "Voltage (V)", "y_label": "Current (mA)", "label": "I-V sweep", "grid": false}},
  {"plotter_id": "basic", "plot_type": "quick_look", "base_plot_type": "scatter_line",
   "description": "Lab name for the Basic Plotter's scatter_line type"}
]
```

## Reply format

```
Reply with:
1. The file name on its own line, for example `calibration_curve.json`.
2. The complete file in one code block. Never shorten it or leave placeholders such as "..." or "rest unchanged".
3. Two or three short sentences: what the module does and anything the user should check.
If you change the file after the user reports an error, send the complete corrected file again.
```

## How the user tests it

1. Save the file in `Documents/PhysPlot/config/plot_types/` (**File → Open Config
   Folder**); the name must end in `.json`, not `.txt`. Choose **File → Reload Config Modules**.
2. Load a data file and set the roles the plotter needs (for example X and Y).
3. In **3. Plotter Module** choose the plotter in **Plotter Module**, then the new name in
   **Plot Type** (after the plotter's own types), and click **Generate Plot**.
4. Check that the labels, size and style match the preset.

Optional check with PhysPlot's Python (script installs: `%LOCALAPPDATA%\PhysPlot\venv\Scripts\python.exe`
on Windows, `~/.physplot/venv/bin/python` on macOS); use your own plotter id and preset name:

```python
from physplot.plotting_modules import PlotterRegistry

registry = PlotterRegistry.default()
print(registry.list_plot_types("example_xy"))
print(registry.resolve_plot_type("example_xy", "calibration_curve"))
```

The first line must list the new name; the second shows the base plot type and `config`.
A line starting with `Skipping plot type preset` means the JSON is invalid.

## If PhysPlot shows an error

The user pastes the message or describes the problem. Fix the file and send it complete.

| What the user sees | Cause and fix |
|---|---|
| The new name is not in **Plot Type** | The file is in another folder or ends in `.txt`; the JSON is invalid (PhysPlot prints `Skipping plot type preset <path>: <reason>` only to the console); or `plotter_id` is wrong or that plotter is not installed. |
| An existing plot type now draws differently | `plot_type` reuses an existing name. Choose a new name. |
| `Plot failed: <Plotter> does not support plot type '<name>'.` or similar | `base_plot_type` is missing or wrong. In a replayed sequence it can also mean the preset file is missing on this computer. |
| The plot looks exactly like the base type | The plotter ignores `config` (all built-in plotters), or a key is misspelt. |
| Grid still shown with `"grid": "false"`, or `Invalid unit ... in 'figsize'` | A value has the wrong type. Use `false`, not `"false"`; `[5, 4]`, not `"5,4"`. |
| `Unknown plotter module '<id>'.` in a sequence or bulk run | The plotter module file is missing on this computer. |
