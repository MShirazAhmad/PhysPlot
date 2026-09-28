# Protocol Modules: guide for AI assistants

> **PhysPlot users:** attach this file to a chat with any AI assistant (ChatGPT, Claude, Gemini, Copilot, ...), together with the first 20-30 lines of a data file you process and, if you have one, a `Sequence.py` exported from PhysPlot (**Protocol → Export Sequence.py**). Then describe what you want. The assistant replies with one complete file: save it in `Documents/PhysPlot/config/protocol_modules/`, choose **File → Reload Config Modules**, and add its steps with **Protocol → Insert Protocol Module**. Step-by-step help: https://physplot.readthedocs.io/en/latest/extensions/ai_assistant.html

## Your task

Write one protocol module: a short, reusable block of protocol steps in a Python file.
It appears under **Protocol → Insert Protocol Module**. Choosing it appends its steps
to the end of the current protocol (**Advanced → Build Protocol**) without running
them; **Apply This Sequence** then runs the whole protocol. Typical modules: "convert
units and plot", "normalize Y and plot".

A module is a normal sequence file, so it uses the same step classes as a complete
sequence (`config/sequences/AI_GUIDE.md`). If the user wants a complete recipe for a
folder of files, a sequence is the better choice. The most reliable route: the user
does the steps once in PhysPlot, exports them with **Protocol → Export Sequence.py**
and attaches that file; you copy the relevant steps into the module.

## Ask the user first

Ask only for what is missing. Never guess column names.

1. What should the block do, step by step?
2. The column headers exactly as PhysPlot shows them (paste the first lines of a data file), and any columns that earlier steps create before the module is inserted.
3. After the block, which column is X and which is Y?
4. Which transformations, with which numbers? Any own transformation files (their file names)?
5. Which plot (plotter and plot type), or no plot?
6. The menu name and a one-sentence description.

## The file PhysPlot expects

- A plain Python file ending in `.py` in `config/protocol_modules/`, for example
  `kelvin_axis_plot.py`. The menu is sorted by file name. A file in
  `Documents/PhysPlot/config/protocol_modules/` replaces a bundled file with the same name.
- Required: a module-level list `WORKFLOW_STEPS` of step objects (classes imported from
  `physplot.steps`). Accepted instead: `build_workflow()` returning that list.
- Optional: `DISPLAY_NAME` (menu label; default is the file name with underscores
  replaced by spaces, in title case) and `DESCRIPTION` (tooltip). PhysPlot reads both
  without running the file, so each must be one plain string literal at top level:
  `DISPLAY_NAME = "..."`. f-strings, concatenation or computed values are ignored.
- The file runs only when the user inserts it. Errors show up then, not at startup.

Steps a module uses (keyword arguments; column names exactly as in the table):

| Step | Arguments |
|---|---|
| `SetRoleStep` | `roles`: keys `"x"`, `"y"`, `"xerr"`, `"yerr"`, `"group"`, `"label"`, `"batch_key"`, `"fit_weight"`, `"ignore"`; values are column names |
| `TransformColumnStep` | `input_column, function_name, output, params=None, input_column_number=None` |
| `CalculateColumnStep` | `formula, output` (numbers, `+ - * / **`, column names that are Python identifiers) |
| `RenameColumnStep` | `old_column, new_column, old_column_number=None` |
| `DeleteColumnsStep` | `columns` (list of names) |
| `DeleteRowsStep` | `row_indices` (1-based) |
| `SetCellValueStep` | `row_index` (1-based), `column, value` |
| `PlotModuleStep` | `plotter_id, plot_type, config={}` |

`function_name`: built-in `normalize_max`, `multiply` (`factor`), `divide`
(`divisor`), `add` (`value`), `subtract` (`value`), `log`, `log10`,
`baseline_subtract` (`baseline`, default the first value), or the file name without
`.py` of a transformation file in `config/transformations/`, such as `02_square` (its
`params` may be `multiplier` and `offset`).

Plotters: `basic` (`scatter`, `line`, `scatter_line`), `scatter` (`scatter`), `line`
(`line`), `errorbar` (`y_errorbar`, `x_y_errorbar`), `histogram` (`histogram`,
`density_histogram`), `overlay` (`overlay_by_group`, `overlay_by_dataset`),
`subplot_grid` (`subplots_by_group`, `subplots_by_dataset`). For built-in plotters
`config` is `{}` or holds only `"lsq_fit"` (see the sequences guide).

## Rules

1. One plain Python file. Import only step classes from `physplot.steps`. No GUI
   code, plotting code, file reading or writing, or `print`.
2. No `LoadDataStep`. The protocol the module is appended to already loads the data.
3. Use only the step classes, arguments, transformation names and plotters above.
4. Refer only to columns that exist when the module is inserted, or that earlier
   steps of the module create. Give `TransformColumnStep` an `input_column_number`
   (1-based position) so PhysPlot can use the position when a file names the column
   differently.
5. Put a `SetRoleStep` for X and Y before a `PlotModuleStep`, unless the user says the
   roles are already set.
6. Keep the module short and focused on one job. `DISPLAY_NAME` short enough for a
   menu; `DESCRIPTION` one sentence that names the columns it expects.

## Complete working example

The user wrote: "My resistance-temperature files have the columns `Temperature_C` and
`Resistance_ohm`. I want a menu item that adds a temperature column in kelvin and
plots resistance against it with lines and markers."

```python
"""Protocol module: plot resistance against temperature in kelvin.

For tables with the columns "Temperature_C" (column 1) and "Resistance_ohm".
Appends three steps to the current protocol.
"""

from physplot.steps import PlotModuleStep, SetRoleStep, TransformColumnStep

DISPLAY_NAME = "Resistance vs Temperature (K)"
DESCRIPTION = "Add 273.15 to Temperature_C as a new column Temperature_K, plot Resistance_ohm against it."

WORKFLOW_STEPS = [
    TransformColumnStep(
        input_column="Temperature_C",
        input_column_number=1,
        function_name="add",
        output="Temperature_K",
        params={"value": 273.15},
    ),
    SetRoleStep(roles={"x": "Temperature_K", "y": "Resistance_ohm"}),
    PlotModuleStep(plotter_id="basic", plot_type="scatter_line", config={}),
]
```

## Reply format

```
Reply with:
1. The file name on its own line, for example `kelvin_axis_plot.py`.
2. The complete file in one code block. Never shorten it or leave placeholders such as "..." or "rest unchanged".
3. Two or three short sentences: what the module does and anything the user should check.
If you change the file after the user reports an error, send the complete corrected file again.
```

## How the user tests it

1. Save the file in `Documents/PhysPlot/config/protocol_modules/` with a name ending
   in `.py` (not `.txt`).
2. Choose **File → Reload Config Modules** (or restart PhysPlot).
3. Load a sample file with **Import Data**.
4. Choose **Protocol → Insert Protocol Module → <DISPLAY_NAME>**. The status bar shows
   *Inserted protocol module <file name>* and the new rows appear at the end of
   **Advanced → Build Protocol**.
5. Click **Apply This Sequence** (Ctrl+R). Every row should show **OK**; the new
   columns appear in the table. **Export Plot** in Simple Mode saves the plot.

From a terminal, a module runs like any sequence file:
`physplot run-workflow kelvin_axis_plot.py --input film_01.csv --output results/film_01`
writes `data.csv` and `plot.png` to `results/film_01`.

## If PhysPlot shows an error

| What the user sees | Cause and fix |
|---|---|
| Module missing from the menu, or *No protocol modules in config/protocol_modules* | Wrong folder, name not ending in `.py`, or not reloaded. Save it again and choose **File → Reload Config Modules**. |
| Menu shows the file name instead of `DISPLAY_NAME` | `DISPLAY_NAME` is not a plain string at top level, or the file has a syntax error. |
| *Insert protocol module failed: ... must define WORKFLOW_STEPS or build_workflow()* | The list is missing or misspelled. |
| *Insert protocol module failed:* `SyntaxError`, `is not defined`, `cannot import name` | Syntax error, missing import, or a step class that does not exist. |
| *Row N failed (...): Unknown column '...'. Available columns: ...* or `Column '...' not found.` | A column name does not exist at that point. Use a name from the list. |
| *Row N failed (...): Unknown transformation '...'* | Not a built-in name and no transformation file with that name. |
| *Row N failed (...): No column has role 'Y'.* | Add a `SetRoleStep` with `"y"` before the plot step. |
| `Unknown plotter module` or `does not support plot type` | Use a plotter and plot type from the list above. |
