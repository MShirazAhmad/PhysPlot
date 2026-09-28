# Figure Templates: guide for AI assistants

> **PhysPlot users:** attach this file to a chat with any AI assistant (ChatGPT, Claude, Gemini, Copilot, ...), together with a template you saved in the Figure Editor (**Figure Editor → PhysPlot → Save as Template**; it is in `Documents/PhysPlot/config/templates/`) and, if you have them, a picture of a figure in the style you want or your journal's figure guidelines. Then describe what you want. The assistant replies with one complete file: save it in `Documents/PhysPlot/config/templates/` and click **Reload** next to **Template** in PhysPlot (or choose **File → Reload Config Modules**). Step-by-step help: https://physplot.readthedocs.io/en/latest/extensions/ai_assistant.html

## Your task

Write one JSON file: a PhysPlot figure template. A template restyles a Matplotlib figure after a plotter module has drawn it: figure size and background, fonts of the axes title and axis labels, grid, spines, tick-label size and colour, line and scatter colours, and the legend. It holds no data, no axis limits and no title or label text. The user chooses it in Simple Mode, panel **3. Plotter Module**, menu **Template**; every **Generate Plot** in the GUI then applies it. It is not recorded in the protocol, so replays, **Run Sequence**, bulk runs and exported `Sequence.py` files do not apply it.

The best starting point is a template the user saved from the Figure Editor after styling a plot by hand. It has the exact layout below and matches the user's plot type. Keep its structure and change only what the user asks for. The user is a scientist, not a programmer.

Some common journal requests cannot be done with a template. Say so before you write the file, and never invent keys for them (unknown keys are ignored without a message):

- tick direction (in or out), tick length and width, minor ticks, ticks on the top and right axes. A Figure Editor plugin can do this; see `config/figureforge_plugins/AI_GUIDE.md`.
- the font family of tick labels and legend entries. They keep Matplotlib's default font (normally DejaVu Sans); a template sets only their size and colour.
- scatter marker shape and size, axis limits, tick spacing and number format, the text of the title and labels (so a template cannot remove the title), annotations, and Matplotlib `rcParams`.

## Ask the user first

Make sure you have the items below. Ask for the missing ones in one short list.

1. A template saved from the Figure Editor, attached. If the user has none, suggest: generate a plot, click **Advanced Styling…** in the plot window, select **Figure** in the Figure Explorer of the Figure Editor, choose **Figure Editor → PhysPlot → Save as Template**, and attach the saved file. Without one, write a complete file with the layout below.
2. The plotter and plot type the template is for (for example Basic Plotter, `scatter`), whether **LSQ fit** is ticked, and how many data series or subplots the plots have.
3. The target: the journal's figure guidelines (width, font, font sizes, minimum line width), or a picture of a figure to copy.
4. Colours for points, lines and the fit line, or "keep the plotter's colours".

If a template or picture is attached, read it yourself and ask only what it does not answer.

## The file PhysPlot expects

One JSON object. Every key is optional: a missing key leaves that property as the plotter drew it.

| Top-level key | Value |
|---|---|
| `schema_version` | `1`. Written by PhysPlot, never checked. |
| `name` | String shown in the **Template** menu. Without it, the file name is shown. |
| `figure` | Object with the figure keys below. |
| `axes` | List of objects, one per axes (subplot), matched by position: the first entry styles the first axes, the second the second, and so on. Surplus entries on either side are ignored. |

| `figure` key | Value |
|---|---|
| `facecolor`, `edgecolor` | Colour of the figure background and edge. |
| `dpi` | Number. On-screen resolution only: **Export Plot** always writes 300 dpi, and the Figure Editor's **File → Export** has its own DPI field. |
| `size_inches` | `[width, height]` in inches (cm / 2.54). The Figure Editor window resizes the figure; there, type the size again in **File → Export**. |
| `suptitle` | Text of a figure title above all axes, in the default font. `""` adds nothing. |

| `axes` entry key | Value |
|---|---|
| `facecolor` | Colour of the plotting area. |
| `title`, `x_label`, `y_label` | Font objects (below) for the axes title and the x and y axis labels. The plot's own text is kept. |
| `x_scale`, `y_scale` | `"linear"`, `"log"`, `"symlog"` or `"logit"`. Leave them out to keep the plotter's scale. |
| `grid` | `{"visible": false}` removes the grid. `{"visible": true, "color": ..., "linestyle": ..., "linewidth": ..., "alpha": ...}` draws major gridlines on both axes. Leave `grid` out to keep the plotter's grid. |
| `spines` | Object with any of `"left"`, `"right"`, `"bottom"`, `"top"`, each `{"visible": true, "color": ..., "linewidth": 0.8, "linestyle": "solid"}`. |
| `ticks` | `{"x": {"labelsize": 8, "labelcolor": ...}, "y": {...}}`: font size and colour of the tick labels. Nothing else about ticks. |
| `lines` | List of line styles, matched by position with the lines of the axes: `color`, `linestyle`, `linewidth`, `marker`, `markersize`, `markeredgecolor`, `markerfacecolor`, `alpha`. |
| `collections` | List matched by position with scatter series, error-bar segments and filled areas: `facecolor`, `edgecolor`, `linewidth`, `alpha`. Only one colour per series; `"facecolor": "none"` gives open markers. |
| `legend` | `visible`, `frame_on`, `fontsize` (legend entries), `loc`, `title` (text), `title_style` (a font object for the legend title). |

Font object keys: `color`; `fontsize` (points, or `"small"`, `"medium"`, `"large"`, ...); `fontfamily` (list of font names; the first installed one is used, so end the list with `"serif"` or `"sans-serif"`); `fontstyle` (`"normal"`, `"italic"`, `"oblique"`); `fontweight` (`"normal"`, `"bold"`, `"light"`, or 100 to 900); `ha` and `va` (text alignment: leave them out, or keep the values of an attached template).

Values:

- Colours: `"#rrggbb"`, or `"#rrggbbaa"` as PhysPlot saves them, or Matplotlib names such as `"black"`. `"none"` means transparent.
- Line styles: `"-"`, `"--"`, `"-."`, `":"` (or `"solid"`, `"dashed"`, `"dashdot"`, `"dotted"`), and `"None"` for no line.
- Markers: `"o"`, `"s"`, `"^"`, `"v"`, `"D"`, `"x"`, `"+"`, `"."`, `"None"`. `alpha`: 0 to 1, or `null` for none.
- `legend.loc`: `"best"`, `"upper right"`, `"upper left"`, `"lower left"`, `"lower right"`, `"right"`, `"center left"`, `"center right"`, `"lower center"`, `"upper center"`, `"center"`, or the number 0 to 10 that PhysPlot saves (0 is `"best"`).

How PhysPlot applies a template, after the plotter and the optional LSQ fit line have drawn the figure: the `figure` keys first, then for each axes the face colour, scales, fonts, grid, spines, tick labels, lines, collections and legend, and finally `tight_layout()`.

- The axis scales are always set, and this resets any custom tick spacing or number format that the plotter drew.
- Lines and collections are matched in drawing order. On a Basic Plotter `scatter` plot the points are `collections[0]` and the LSQ fit line is `lines[0]`. On `line` and `scatter_line` plots the data line is `lines[0]` and the fit line `lines[1]`. Overlay plots have one line per group. Error-bar plots also contain cap lines and bar segments, so ask for a template saved from such a plot.
- A `lines` entry with `linestyle` or `linewidth` at the fit line's position overrides the **Fit Style** settings. Give only `color` there to keep them.
- A legend with `"visible": true` is rebuilt from the labelled lines and series (the LSQ fit line is labelled; Basic Plotter data points are not). With nothing labelled, the legend is empty, and with `"frame_on": true` it shows as a small empty box. `"visible": false` leaves the plotter's legend as it is.
- For the Subplot Grid plotter, repeat the `axes` entry once for every subplot; extra entries do no harm.

## Rules

- Valid JSON only: double quotes, no comments, no trailing commas, `true`, `false` and `null` in lower case. The top level must be an object and `name` a string: a list at the top level, or a number as `name`, makes PhysPlot close on **Reload** and fail to start.
- Use only the keys above, at the level shown. Numbers are numbers (`9`, not `"9pt"`). Booleans are `true` or `false`, never strings: `"false"` counts as true.
- Leave out everything the user did not ask to change, so the plotter's look stays. When editing an attached template, change only the requested values and keep the rest, including `ha`, `va` and `schema_version`.
- Give the template a new `name`, and a file name of letters, digits and underscores ending in `.json`. Do not use `Publication_Style.json` unless the user wants to replace the bundled template.
- `size_inches` holds exactly two numbers. Typical journal widths: single column 3.3-3.5 in (85-90 mm), double column 6.7-7.2 in (170-183 mm); typical text 7-9 pt and lines 0.5-1.5 pt. Use the journal's own values when the user gives them.
- A template cannot change the font of tick labels and legend entries (normally DejaVu Sans). For one consistent font, use `["sans-serif"]`. For a serif font write, for example, `["Times New Roman", "Times", "serif"]`, and tell the user that tick labels and legend entries stay sans-serif.

## Complete working example

The user attached a template saved from a Basic Plotter `scatter` plot and asked: "Single-column journal figure, 3.35 by 2.6 inches, 9 pt labels, 8 pt tick labels, thin black axes on all sides, open black circles, a red fit line, legend without a frame, no grid."

`journal_single_column.json`:

```json
{
  "schema_version": 1,
  "name": "Journal Single Column",
  "figure": {
    "facecolor": "#ffffffff",
    "edgecolor": "#ffffffff",
    "dpi": 200,
    "size_inches": [3.35, 2.6],
    "suptitle": ""
  },
  "axes": [
    {
      "facecolor": "#ffffffff",
      "title": {"color": "#000000ff", "fontsize": 9, "fontfamily": ["sans-serif"], "fontstyle": "normal", "fontweight": "normal"},
      "x_label": {"color": "#000000ff", "fontsize": 9, "fontfamily": ["sans-serif"], "fontstyle": "normal", "fontweight": "normal"},
      "y_label": {"color": "#000000ff", "fontsize": 9, "fontfamily": ["sans-serif"], "fontstyle": "normal", "fontweight": "normal"},
      "grid": {"visible": false},
      "spines": {
        "left": {"visible": true, "color": "#000000ff", "linewidth": 0.6, "linestyle": "solid"},
        "right": {"visible": true, "color": "#000000ff", "linewidth": 0.6, "linestyle": "solid"},
        "bottom": {"visible": true, "color": "#000000ff", "linewidth": 0.6, "linestyle": "solid"},
        "top": {"visible": true, "color": "#000000ff", "linewidth": 0.6, "linestyle": "solid"}
      },
      "ticks": {
        "x": {"labelsize": 8, "labelcolor": "#000000ff"},
        "y": {"labelsize": 8, "labelcolor": "#000000ff"}
      },
      "lines": [
        {"color": "#d62728ff"}
      ],
      "collections": [
        {"facecolor": "none", "edgecolor": "#000000ff", "linewidth": 0.8, "alpha": null}
      ],
      "legend": {
        "visible": true,
        "frame_on": false,
        "fontsize": 7,
        "loc": "best",
        "title": "",
        "title_style": {}
      }
    }
  ]
}
```

On a Basic Plotter `scatter` plot this gives a 3.35 by 2.6 inch figure with open black circles. With **LSQ fit** ticked, the fit line is `lines[0]`: it turns red and keeps the line style and width from **Fit Style**, and the legend shows it without a frame. Without a fit, nothing is labelled and the frameless legend stays invisible. `x_scale` and `y_scale` are left out, so the plotter's scales stay.

## Reply format

```
Reply with:
1. The file name on its own line, for example `journal_single_column.json`.
2. The complete file in one code block. Never shorten it or leave placeholders such as "..." or "rest unchanged".
3. Two or three short sentences: what the module does and anything the user should check.
If you change the file after the user reports an error, send the complete corrected file again.
```

## How the user tests it

1. Save the file in `Documents/PhysPlot/config/templates/` (**File → Open Config Folder** opens `Documents/PhysPlot/config/`). The name must end in `.json`, not `.json.txt`.
2. In Simple Mode, panel **3. Plotter Module**, click **Reload** next to **Template** (or choose **File → Reload Config Modules**), then choose the template by its `name`.
3. Load data, set the X and Y columns, choose the plotter and plot type the template was made for, tick **LSQ fit** if it is used, and click **Generate Plot**.
4. Check size, fonts, colours, line styles and the legend. **Export Plot** saves PhysPlot's copy of the figure at 300 dpi with the template's size.

Optional check in Python, in the environment where PhysPlot is installed (for example a Jupyter notebook). It lists the templates PhysPlot finds, applies this one to a small test figure and saves `template_check.png`, and shows the full error message if something fails. Replace the file name with the real one:

```python
import matplotlib.pyplot as plt
from physplot.user_paths import user_plugin_dir
from physplot_gui.plot_styles import apply_style_module, list_style_modules

print([entry["name"] for entry in list_style_modules()])
figure, axes = plt.subplots()
axes.scatter([0, 1, 2, 3, 4], [0.1, 2.1, 3.9, 6.2, 7.9])
axes.plot([0, 4], [0, 8], linestyle="--", label="Linear fit")
axes.set_xlabel("Time (s)")
axes.set_ylabel("Voltage (V)")
apply_style_module(figure, user_plugin_dir("templates") / "journal_single_column.json")
figure.savefig("template_check.png", dpi=300)
```

## If PhysPlot shows an error

The user will paste the message or describe what they see. Find the matching case, fix the cause and send the complete corrected file.

| What the user sees | Likely cause and what to change |
|---|---|
| The template is not in the **Template** menu after **Reload** | Wrong folder, a name ending in `.json.txt`, or invalid JSON (a comment, single quotes, a missing or trailing comma). PhysPlot skips unreadable files without a message. Check the JSON syntax. |
| The file is valid JSON but does not appear in **Template** | The top level is not an object (for example a list). Write one JSON object `{...}` per file. |
| *Plot failed* with a JSON message such as `Expecting ',' delimiter: line 12 column 5` | The chosen template file was edited and is no longer valid JSON. Fix the syntax at that line. |
| *Plot failed*: `'...' is not a valid value for color` | A colour is not `#rrggbb`, `#rrggbbaa` or a Matplotlib colour name. |
| *Plot failed*: `Size is invalid. Valid font size are xx-small, ...` | A `fontsize` or `labelsize` is a string with units, such as `"9pt"`. Use a number. |
| *Plot failed*: `weight='...' is invalid`, `'...' is not a valid value for style` | `fontweight` or `fontstyle` has a value not listed above. |
| *Plot failed*: `'...' is not a valid value for ls`, `Unrecognized linestyle`, `Unrecognized marker style` | A line style, spine line style or marker is not one of the values listed above. |
| *Plot failed*: `'...' is not a valid value for scale` or `for loc` | A scale name or legend location is not listed above. |
| *Plot failed*: `not enough values to unpack (expected 2, got 1)` | `size_inches` does not hold exactly two numbers. |
| *Plot failed*: `0` | `axes` is an object instead of a list of objects. |
| A setting has no effect | The key is misspelled, at the wrong level, or not supported (see "Your task"). Unknown keys are ignored silently. |
| The wrong line or series changed style, or the fit line lost its **Fit Style** | Position matching. Check which line is `lines[0]` for this plot type, and give the fit line's entry only a `color`. |
| A small empty box in a corner of the plot | The legend is visible with `"frame_on": true`, but nothing in the plot is labelled. Use `"frame_on": false`, or `"visible": false`. |
| The font is wrong, or a message `findfont: Font family '...' not found` | That font is not installed. End `fontfamily` with `"serif"` or `"sans-serif"`. The font of tick labels and legend entries cannot be changed by a template. |
| Custom tick spacing or number format disappeared | Applying a template always resets the axis scales and their ticks. This cannot be avoided in a template. |
| Points or lines vanish on a `"log"` axis | The data has zero or negative values. Use `"symlog"`, or leave the scale out. |
