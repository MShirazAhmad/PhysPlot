# Protocol Sequences: guide for AI assistants

> **PhysPlot users:** attach this file to a chat with any AI assistant (ChatGPT, Claude, Gemini, Copilot, ...), together with a `Sequence.py` you exported from PhysPlot (**Protocol → Export Sequence.py**) if you have one, and the first 20-30 lines of one data file. Then describe what you want. The assistant replies with one complete file: save it in `Documents/PhysPlot/config/sequences/` and open it with **Protocol → Import Sequence.py** (one file) or pick it as the **Sequence File** in **Advanced → Run Sequence** (a whole folder). Step-by-step help: https://physplot.readthedocs.io/en/latest/extensions/ai_assistant.html

## Your task

Write one complete PhysPlot protocol sequence: a Python file that lists processing
steps in order. PhysPlot replays the steps on a data table: assign column roles, add
computed columns, draw a plot. The same file runs in the PhysPlot window
(**Protocol → Import Sequence.py**, then **Apply This Sequence**), on every file of a
folder (**Advanced → Run Sequence**) and from a terminal (`physplot run-workflow`,
`physplot run-bulk`).

The most reliable route: the user builds the steps once in PhysPlot on one real file,
saves them with **Protocol → Export Sequence.py**, and attaches that file. Then you
edit a known-good file and change only what the user asks. Recommend this route
when the user has not done it, especially for long protocols or data that needs a
loader plugin. Otherwise write the file from scratch using only this guide.

A sequence describes processing only. The user chooses the input file and the output
folder when running it.

## Ask the user first

Ask only for what is missing. Never guess column names.

1. Do you have a `Sequence.py` exported from PhysPlot for this job? It is the most reliable starting point.
2. What type of data file is it (`.csv`, `.txt`, `.xlsx`, ...)? Paste the first 20-30 lines of one file, or the column headers exactly as PhysPlot shows them.
3. Which column is X and which is Y? Any error or group columns?
4. Which transformations, in which order, with which numbers (for example "subtract 0.02, then scale the strongest peak to 1")? Do you use your own transformation files from `Documents/PhysPlot/config/transformations/`? What are their file names?
5. Which plot (line, scatter, error bars, histogram, ...)? Should a least-squares fit be drawn over it, and with which formula and starting values?
6. Will you run it on one file or on a whole folder? (Results go to a folder you choose at run time.)
7. Only for file types other than `.csv .txt .dat .tsv .msa .xls .xlsx .xrdml`: the full path of one sample file.

## The file PhysPlot expects

- A plain Python file, UTF-8, ending in `.py`, for example `uvvis_normalize_sequence.py`.
- Required: a module-level list `WORKFLOW_STEPS` of step objects (classes imported from
  `physplot.steps`), in run order. Accepted instead: a function `build_workflow()` with
  no arguments that returns that list. If both exist, `WORKFLOW_STEPS` is used.
- PhysPlot executes the whole file every time it loads it (`__name__` is not `"__main__"`).
- Files exported by PhysPlot also define `build_workflow()` and `run()` and import
  `PhysPlot` and `load_input`. Keep these when editing an exported file.

**Where the data comes from.**

- **Apply This Sequence** runs the steps on the table currently loaded in PhysPlot.
  A `LoadDataStep` with a `path` first reloads that file.
- **Run Sequence**, `run-workflow` and `run-bulk` remove every `LoadDataStep` and load
  the input file instead, with Auto Loader (reader chosen from the file extension) or
  with the loader plugin recorded in the `LoadDataStep`.
- **Run Sequence** and `run-bulk` process only files directly in the input folder, in
  alphabetical order. Without a `LoadDataStep` (or with one whose `path` ends in a
  built-in extension): all `.csv .txt .dat .tsv .msa .xls .xlsx .xrdml` files. With a
  `LoadDataStep` whose `path` has another extension, or with a `loader_plugin`: only
  files with that extension.

So, when writing from scratch, leave out `LoadDataStep` unless the user gave a full
file path, or the data type is not in the built-in list (then add a first
`LoadDataStep` with the full path of one sample file).

**Columns.** Refer to columns by their exact header text, including spaces and units:
`"Wavelength (nm)"`. A column created by a step can be used by later steps. New
columns have no role. Arguments ending in `_column_number` are 1-based positions,
counting columns added by earlier steps. They are used only when the column name is
missing and column-number fallback is on (always in the PhysPlot window and Run
Sequence; on the command line only with `--allow-column-number-fallback`). Use `None`
when unsure. `output_column_number` is informational only.

### Step reference

These nine classes are the only steps. There is no fit, export, save, filter, smooth
or loop step. Use keyword arguments.

| Step | Arguments | Does |
|---|---|---|
| `LoadDataStep` | `path=None, loader="auto", dataset_name=None, loader_plugin=None` | Loads a file. Put it first. |
| `SetRoleStep` | `roles` (dict) | Assigns column roles. |
| `TransformColumnStep` | `input_column, function_name, output, params=None, input_column_number=None, output_column_number=None` | Writes `function(input column)` to column `output`. |
| `CalculateColumnStep` | `formula, output, formula_original=None, source_columns=None, source_column_numbers=None, output_column_number=None` | Writes an arithmetic formula to column `output`. |
| `RenameColumnStep` | `old_column, new_column, old_column_number=None` | Renames a column. |
| `DeleteColumnsStep` | `columns, column_numbers=None` | Deletes columns (list of names). |
| `DeleteRowsStep` | `row_indices` | Deletes rows (list of 1-based row numbers). |
| `SetCellValueStep` | `row_index, column, value, column_number=None` | Sets one cell (1-based row). |
| `PlotModuleStep` | `plotter_id, plot_type=None, config=None` | Draws a plot of the X and Y role columns. |

One-line examples:

```python
LoadDataStep(path="C:/Users/ana/UVVis/sample_A.csv", loader="auto")
SetRoleStep(roles={"x": "Wavelength (nm)", "y": "Absorbance", "yerr": "Abs_err"})
TransformColumnStep(input_column="Absorbance", function_name="multiply", output="Absorbance_x10", params={"factor": 10})
RenameColumnStep(old_column="Wavelength (nm)", new_column="Wavelength_nm")
CalculateColumnStep(formula="1239.84 / Wavelength_nm", output="Energy_eV")
DeleteColumnsStep(columns=["Comment"])
DeleteRowsStep(row_indices=[1, 2])
SetCellValueStep(row_index=3, column="Absorbance", value=0.0)
PlotModuleStep(plotter_id="line", plot_type="line", config={})
```

- `LoadDataStep`: `path` is a full path in forward slashes or a raw string
  (`r"C:\Users\..."`); a normal string with backslashes is a Python syntax error.
  `loader` is `"auto"` (use this), `"csv"`, `"txt"`, `"excel"` or `"xrdml"`.
  `loader_plugin` is the full path of a `config/data_importers/*.py` file; exported
  files set it together with `loader="dataframe"`. Keep those values unchanged.
- `SetRoleStep` keys: `"x"`, `"y"`, `"xerr"`, `"yerr"`, `"group"`, `"label"`,
  `"batch_key"`, `"fit_weight"`, and `"ignore"` to clear a column's role. X, Y, X
  Error, Y Error and Fit Weight belong to one column at a time: giving the role to a
  new column clears it from the old one. One column per key per step.
- `TransformColumnStep`: a new `output` name adds a column; an existing name overwrites
  that column.
- `CalculateColumnStep`: only `formula` and `output` are needed. The formula may use
  numbers, `+ - * / **`, parentheses, and column names that are valid Python
  identifiers (letters, digits, underscores). `C1`, `C2`, ... refer to columns by
  number, but only when that column's name is also an identifier. No functions such
  as `log` or `sqrt`: use a transformation. Rename a column like `"Wavelength (nm)"`
  first.
- `PlotModuleStep`: set X and Y before it. Only the last plot of a run is saved. For
  built-in plotters `config` is `{}` or holds only `"lsq_fit"`; other keys are ignored.

**Transformations** (`function_name`). Built in:

| Name | `params` | Result |
|---|---|---|
| `normalize_max` | none | divide by the largest absolute value |
| `multiply` | `factor` | multiply by `factor` |
| `divide` | `divisor` | divide by `divisor` |
| `add` | `value` | add `value` |
| `subtract` | `value` | subtract `value` |
| `log` | none | natural logarithm |
| `log10` | none | base-10 logarithm |
| `baseline_subtract` | `baseline` (optional) | subtract `baseline`, default the column's first value |

Any other name is the file name without `.py` of a transformation file in
`Documents/PhysPlot/config/transformations/` or the bundled folder, for example `"02_square"`. PhysPlot
ships `01_identity`, `02_square`, `03_cube`, `04_reciprocal`, `05_log10`, `06_log`,
`07_exponential`, `08_cos`, `09_sin`, `10_tan`, `11_arccos`, `12_arcsin`,
`13_arctan` and `14_xrd_baseline_remove`. For these files `params` may hold
`multiplier` (default `1.0`) and `offset` (default `0.0`), giving
`transform(values) * multiplier + offset`, plus any keyword that file's
`transform()` accepts. `"identity"` is not a valid name.

**Plotters** (`plotter_id` and `plot_type`, spelled exactly):

| `plotter_id` | `plot_type` (first is the default) | Uses roles |
|---|---|---|
| `basic` | `scatter`, `line`, `scatter_line` | X, Y |
| `scatter` | `scatter` | X, Y |
| `line` | `line` | X, Y |
| `errorbar` | `y_errorbar`, `x_y_errorbar` | X, Y, Y Error (X Error too for `x_y_errorbar`) |
| `histogram` | `histogram`, `density_histogram` | Y (or X) |
| `overlay` | `overlay_by_group`, `overlay_by_dataset` | X, Y, optional Group or Label (one line per group) |
| `subplot_grid` | `subplots_by_group`, `subplots_by_dataset` | X, Y, optional Group or Label |

Plotters from `config/plotter_modules/` (for example `example_xy` with `xy_markers`
and `xy_line`) and plot types from `config/plot_types/` (for example `basic` with
`scatter_publication`) also work when the user has those files.

**Least-squares fit.** Add it to the plot step:

```python
PlotModuleStep(plotter_id="basic", plot_type="scatter", config={"lsq_fit": {
    "enabled": True, "expression": "a*x + b", "parameters": "a,b", "initial": "1,0",
    "label": "", "line_style": "--", "line_width": 2.0, "show_legend": True}})
```

The expression uses `x`, the parameter names, numbers, `+ - * / **` and `abs`, `sqrt`,
`exp`, `log`, `log10`, `sin`, `cos`, `tan`, `arcsin`, `arccos`, `arctan`, `sinh`,
`cosh`, `tanh`. Give one initial value per parameter.

**What a run writes.** For each input file: `data.csv` (final table), `columns.csv`
(column list with roles), `workflow.py`, `plot.png` (last plot, 150 dpi) and
`fit.json` (fitted parameters, when a fit ran). Figure templates and Figure Editor
changes are never part of a sequence.

## Rules

1. Return one plain Python file. Import only step classes from `physplot.steps`. When
   editing an exported file, keep its existing imports (`from physplot import
   PhysPlot`, `from physplot.steps.load_data import load_input`).
2. Use only the nine step classes and the arguments listed here. Do not invent steps,
   arguments, transformation names, plotter ids, plot types or `config` keys.
3. No GUI code, plotting code, file reading or writing, `print`, `input()` or network
   access. The file only defines the steps.
4. Copy column names exactly from the user's data, including case, spaces and units.
5. Put a `SetRoleStep` for X and Y before the first `PlotModuleStep`. To plot a new
   column, give it the Y (or X) role first.
6. Use a new, descriptive `output` name for each computed column unless the user wants
   a column overwritten.
7. No absolute paths unless the user gave them. Write paths with forward slashes.
8. When editing an exported file, keep `LoadDataStep`, `build_workflow()`, `run()` and
   all steps the user did not ask to change exactly as they are.
9. If no transformation does what the user needs, say so and suggest a
   `CalculateColumnStep` or a new transformation file (`config/transformations/`).

## Complete working example

The user wrote: "My UV-Vis files are CSVs with the columns `Wavelength (nm)` and
`Absorbance`. Subtract the blank level 0.02, scale the strongest peak to 1 and plot
it against wavelength as a line. I want to run it on a folder of spectra."

```python
"""UV-Vis absorbance: remove a constant baseline, normalize to the strongest peak, plot.

Input: a CSV with the columns "Wavelength (nm)" and "Absorbance".
Load the data with Import Data (GUI), Run Sequence (a folder), or
physplot run-workflow ... --input <file>.
"""

from physplot.steps import PlotModuleStep, SetRoleStep, TransformColumnStep

WORKFLOW_STEPS = [
    SetRoleStep(roles={"x": "Wavelength (nm)", "y": "Absorbance"}),
    TransformColumnStep(
        input_column="Absorbance",
        input_column_number=2,
        function_name="subtract",
        output="Absorbance_corr",
        params={"value": 0.02},
    ),
    TransformColumnStep(
        input_column="Absorbance_corr",
        input_column_number=3,
        function_name="normalize_max",
        output="Absorbance_norm",
        params={},
    ),
    SetRoleStep(roles={"y": "Absorbance_norm"}),
    PlotModuleStep(plotter_id="line", plot_type="line", config={}),
]
```

## Reply format

```
Reply with:
1. The file name on its own line, for example `uvvis_normalize_sequence.py`.
2. The complete file in one code block. Never shorten it or leave placeholders such as "..." or "rest unchanged".
3. Two or three short sentences: what the module does and anything the user should check.
If you change the file after the user reports an error, send the complete corrected file again.
```

## How the user tests it

Save the file in `Documents/PhysPlot/config/sequences/` with a name ending in `.py`
(not `.txt`).

One file in the PhysPlot window:

1. Load one data file with **Import Data** (not needed if the sequence has a
   `LoadDataStep` with a path).
2. **Protocol → Import Sequence.py…** and choose the file. The steps appear as rows in
   **Advanced → Build Protocol**. Nothing runs yet.
3. **Apply This Sequence** (Ctrl+R). Every row should show **OK** and the status bar
   *Sequence complete*. The new columns appear in the table. No plot window opens;
   **Export Plot** in Simple Mode saves the plot.

A folder: **Advanced → Run Sequence**. Fill in **Input Folder**, **Sequence File**
(this file) and **Output Folder**, then click **Run Bulk Workflow**. The status bar
shows *Bulk complete: N outputs*. Each input file gets a folder
`<Output Folder>/<file name>/` with `data.csv` and `plot.png`.

From a terminal:

```bash
physplot run-workflow uvvis_normalize_sequence.py --input sample_A.csv --output results/sample_A
physplot run-bulk uvvis_normalize_sequence.py --input-folder spectra --output-folder results
```

They print `Workflow output written to ...` and `Bulk workflow wrote N outputs to ...`.
On Windows (PhysPlot installer), in PowerShell, write
`& "$env:LOCALAPPDATA\PhysPlot\venv\Scripts\physplot.exe"` instead of `physplot`. Add
`--allow-column-number-fallback` to use column numbers when a name is missing, as the
PhysPlot window does.

## If PhysPlot shows an error

The PhysPlot window shows *Load sequence failed* (the file cannot be read), *Apply
sequence failed: Row N failed (StepName): ...* (a step failed; the row turns
**Failed**), or *Bulk run failed: Bulk run stopped at <file>: ...*. The terminal
prints a Python traceback; its last line is the error. Ask for the complete message.

| Message contains | Cause and fix |
|---|---|
| `must define WORKFLOW_STEPS or build_workflow()` | The list is missing or misspelled. Define `WORKFLOW_STEPS`. |
| `SyntaxError`, `was never closed`, `unicodeescape` | Python syntax error at the given line; a Windows path needs forward slashes. |
| `name 'SetRoleStep' is not defined` | Missing import from `physplot.steps`. |
| `cannot import name '...' from 'physplot.steps'` | An invented step class. Use only the nine steps. |
| `Unknown column '...'. Available columns: ...`, `Column '...' not found.` | Wrong column name; pick one from the list. Only `Column 1, Column 2, ...` listed: no data was loaded; use **Import Data** first. |
| `Unknown transformation '...'` | Not a built-in name, and no transformation file with that name. Fix the name or add the file. |
| `got an unexpected keyword argument` | Wrong `params` key for that transformation (see the table). |
| `does not contain numeric values` | The column holds text. Use a numeric column. |
| `Unknown column role '...'` | Use the `SetRoleStep` keys listed above. |
| `No column has role 'Y'.` (or `'X'`) | Add a `SetRoleStep` before the plot step. |
| `Unknown plotter module '...'`, `does not support plot type '...'` | Use a `plotter_id` and `plot_type` from the table. |
| `cannot be used in formulas yet`, `Unknown formula column`, `unsupported or unsafe syntax` | Formula problem: rename the column to a simple name first; no functions in formulas. |
| `LSQ initial guesses must match`, `Optimal parameters not found` | Fit settings: one initial value per parameter; better starting values. |
| `No loader for '.xyz' files` | PhysPlot cannot read this file type; a loader plugin is needed (`config/data_importers/AI_GUIDE.md`). |
| `wrote 0 outputs` / `Bulk complete: 0 outputs` | No file in the folder matched. For non-built-in file types add a first `LoadDataStep` with the full path of one sample file. |
