# Fit-Style Presets: guide for AI assistants

> **PhysPlot users:** attach this file to a chat with any AI assistant (ChatGPT, Claude, Gemini, Copilot, ...), together with an existing preset if you have one (PhysPlot ships `Default LSQ Fit.json`). Then describe what you want. The assistant replies with one complete file: save it in `Documents/PhysPlot/config/figureforge_fit_styles/` and click **Reload** next to **Fit Style** in PhysPlot (or choose **File → Reload Config Modules**). Step-by-step help: https://physplot.readthedocs.io/en/latest/extensions/ai_assistant.html

## Your task

Write one JSON file: a preset for the least-squares (LSQ) fit line of Simple Mode, panel **3. Plotter Module**. When the user chooses the preset in the **Fit Style** menu, PhysPlot copies four values into the **Fit Line** fields: the legend label, the line style, the line width and the **Legend** checkbox. The user can still edit the fields afterwards.

A preset holds nothing else. It has no fit function, parameter names or starting values (the user types those in **Fit Function**, **Params** and **Initial**), it does not tick **LSQ fit**, and it has no colour or marker: the fit line takes the next colour of Matplotlib's colour cycle. Despite the folder name, the Figure Editor's **Fitting → Add Fit Function** does not read presets. If the user wants a colour, explain that a figure template can set it (see `config/templates/AI_GUIDE.md`; on a Basic Plotter scatter plot the fit line is the template's `lines[0]`).

## Ask the user first

Ask in one short list for what the request does not say:

1. The legend text: a fixed label such as `"Linear fit"`, or automatic (an empty label gives `LSQ fit: a*x + b (a=2.013, b=-0.4981)` with the fitted values).
2. Line style: dashed, solid, dash-dot or dotted.
3. Line width in points.
4. Whether the legend is shown.
5. The name to show in the **Fit Style** menu.

## The file PhysPlot expects

One JSON object with these keys. Any other key is ignored.

| Key | Value |
|---|---|
| `schema_version` | `1`. Written by PhysPlot, never checked. |
| `name` | String shown in the **Fit Style** menu. Without it, the file name is shown. |
| `line_style` | Exactly one of `"--"` (dashed), `"-"` (solid), `"-."` (dash-dot), `":"` (dotted). Any other value is ignored and the field keeps its current style. |
| `line_width` | Number, in points, for example `1.5`. A value that is not a number becomes `2.0` when the plot is drawn. |
| `label` | String for the legend. `""` means the automatic label with the fitted values. Matplotlib math text such as `"$y = ax + b$"` works; write every backslash twice in JSON (`"$\\alpha$"`). A label that starts with `_` is left out of the legend. |
| `show_legend` | `true`: the legend is redrawn after the fit line is added, so it includes the fit. `false`: the legend is not redrawn (a Basic Plotter plot then has no legend, unless the chosen **Template** shows one). |

A missing key sets its field to the default when the preset is chosen: `label` `""`, `line_style` `"--"`, `line_width` `2.0`, `show_legend` `true`. So a preset without `label` clears the label field.

How PhysPlot uses the file:

- The menu lists **Default** (which changes nothing), then every `*.json` file in `Documents/PhysPlot/config/figureforge_fit_styles/` and in PhysPlot's bundled folder, sorted by `name`. A user file with the same file name as a bundled one replaces it.
- On **Generate Plot** with **LSQ fit** ticked, the current field values are saved in the protocol's `PlotModuleStep` (`lsq_fit`), so replays and bulk runs draw the same line without the preset file.
- A figure template chosen in **Template** is applied after the fit line is drawn. If the template's `lines` entry at the fit line's position sets `linestyle` or `linewidth`, it overrides the preset. The bundled **Publication Style** template does this: it makes the first line solid, orange and 2 pt wide.

## Rules

- Valid JSON only: double quotes, no comments, no trailing commas, `true` and `false` in lower case.
- The top level must be an object and `name` a string. A list at the top level, or a number as `name`, makes PhysPlot close on **Reload** and fail to start.
- Numbers are numbers (`1.5`, not `"1.5 pt"`). `show_legend` is `true` or `false`, never a string: `"false"` counts as true.
- Write all six keys, so choosing the preset always sets every field.
- Use a file name of letters, digits and underscores ending in `.json`. Do not use `Default LSQ Fit.json` unless the user wants to replace the bundled preset.

## Complete working example

The user asked: "A thin dashed fit line, 1 pt, labelled 'Linear fit' in the legend."

`thin_dashed_fit.json`:

```json
{
  "schema_version": 1,
  "name": "Thin Dashed Fit",
  "line_style": "--",
  "line_width": 1.0,
  "label": "Linear fit",
  "show_legend": true
}
```

Choosing **Thin Dashed Fit** sets the label field to `Linear fit`, the line style to `--`, the width to `1.0` and ticks **Legend**.

## Reply format

```
Reply with:
1. The file name on its own line, for example `thin_dashed_fit.json`.
2. The complete file in one code block. Never shorten it or leave placeholders such as "..." or "rest unchanged".
3. Two or three short sentences: what the module does and anything the user should check.
If you change the file after the user reports an error, send the complete corrected file again.
```

## How the user tests it

1. Save the file in `Documents/PhysPlot/config/figureforge_fit_styles/` (**File → Open Config Folder** opens `Documents/PhysPlot/config/`). The name must end in `.json`, not `.json.txt`.
2. In Simple Mode, panel **3. Plotter Module**, click **Reload** next to **Fit Style** (or choose **File → Reload Config Modules**).
3. Choose the preset in **Fit Style** and check the **Fit Line** fields: label, line style, width and **Legend**.
4. Load data, set the X and Y columns, tick **LSQ fit**, enter the fit function if needed, and click **Generate Plot**. Set **Template** to **None** for this test, so no template changes the line.

After editing a preset file, click **Reload**, then choose another entry and the preset again: reloading alone does not copy the new values into the fields.

Optional check in Python, in the environment where PhysPlot is installed (for example a Jupyter notebook). It prints every preset PhysPlot finds, with its contents:

```python
from physplot_gui.fit_styles import list_fit_style_presets

for preset in list_fit_style_presets():
    print(preset["name"], preset["style"])
```

## If PhysPlot shows an error

The user will paste the message or describe what they see. Find the matching case, fix the cause and send the complete corrected file.

| What the user sees | Likely cause and what to change |
|---|---|
| The preset is not in the **Fit Style** menu after **Reload** | Wrong folder, a name ending in `.json.txt`, or invalid JSON (a comment, single quotes, a missing or trailing comma). PhysPlot skips unreadable files without a message. |
| The file is valid JSON but does not appear in **Fit Style** | The top level is not an object (for example a list). Write one JSON object `{...}` per file. |
| The line style field does not change | `line_style` is not exactly `"--"`, `"-"`, `"-."` or `":"` (for example `"dashed"`). |
| The fit line is 2 pt wide although the preset says otherwise | `line_width` is not a plain number, for example `"1.5 pt"`. |
| **Legend** stays ticked although the preset says false | `show_legend` is the string `"false"`. Write `false` without quotes. |
| The fields do not show the edited values | Reload, then choose another entry and the preset again. |
| No fit line is drawn | **LSQ fit** is not ticked. A preset never ticks it. |
| The fit line has another colour, style or width than expected | The colour is not part of a preset. A selected **Template** with a `lines` entry at the fit line's position overrides style and width. |
| *Plot failed* with `ParseFatalException: Unknown symbol` or another math-text error | The `label` contains invalid math text between `$` signs, or single backslashes. Fix the math text and double every backslash. |
| *Plot failed* about initial guesses, parameters or `Optimal parameters not found` | These come from the fit itself (**Fit Function**, **Params**, **Initial**), not from the preset. |
