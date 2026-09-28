# Transformation Pipelines: guide for AI assistants

> **PhysPlot users:** attach this file to a chat with any AI assistant (ChatGPT, Claude, Gemini, Copilot, ...), together with the first 20-30 lines of one data file (or its column headers). Then describe what you want. The assistant replies with one complete file: save it in `Documents/PhysPlot/config/pipelines/` and apply it with the short Python script under "How the user tests it". PhysPlot 1.0 has no menu command for pipeline files; to add the same transformations from a menu, ask for a protocol module instead (`config/protocol_modules/AI_GUIDE.md`). Step-by-step help: https://physplot.readthedocs.io/en/latest/extensions/ai_assistant.html

## Your task

Write one transformation pipeline: a JSON file that lists column transformations in
order (input column, function, parameters, output column), in the format of
PhysPlot's pipeline export.

First tell the user, in one or two sentences: PhysPlot 1.0 has no menu item or button
for pipeline files; a pipeline is applied with the Python script under "How the user
tests it", which also saves it as a sequence. To add transformations from PhysPlot's
menus, a protocol module (`config/protocol_modules/AI_GUIDE.md`) is the better
choice; for a whole recipe with roles and a plot, a sequence
(`config/sequences/AI_GUIDE.md`). Write the pipeline if the user still wants it.

## Ask the user first

Ask only for what is missing. Never guess column names.

1. The column headers exactly as PhysPlot shows them (paste the first lines of a data file).
2. Which transformations, in which order, with which numbers, and the name of each new column.
3. Any own transformation files in `Documents/PhysPlot/config/transformations/` (their file names)?

## The file PhysPlot expects

A UTF-8 JSON file ending in `.json`, for example `uvvis_cleanup.json`. The top level
is an array with one object per transformation, applied from first to last. Each
object has exactly these four keys:

| Key | Value |
|---|---|
| `"input"` | Exact name of the column to transform. It may be the `"output"` of an earlier entry. |
| `"function"` | Transformation name (see below). |
| `"params"` | Text such as `"value=0.02"` or `"factor=10, value=1"`; `"-"` when there are none. Values that look like numbers are read as numbers. A value cannot contain a comma. |
| `"output"` | Name of the new column. An existing name overwrites that column. |

Transformation names and their parameters:

| `"function"` | `"params"` |
|---|---|
| `normalize_max` (divide by the largest absolute value) | `-` |
| `multiply` | `factor=...` |
| `divide` | `divisor=...` |
| `add` | `value=...` |
| `subtract` | `value=...` |
| `log` (natural), `log10` | `-` |
| `baseline_subtract` | `baseline=...`, or `-` to subtract the column's first value |
| a transformation file name without `.py`, e.g. `02_square`, `14_xrd_baseline_remove` | `-`, or `multiplier=..., offset=...` (result is `transform(values) * multiplier + offset`) |

## Rules

1. Strict JSON: double quotes, no comments, no trailing commas.
2. Use only the four keys and only the transformation names above or the user's own
   transformation file names. Parameter names exactly as listed.
3. Copy column names exactly from the user's data, including case, spaces and units.
4. A pipeline holds transformations only. Roles, plots, fits, renames and loading need
   a sequence or a protocol module.
5. Give every output a new, descriptive name unless the user wants a column overwritten.

## Complete working example

The user wrote: "My UV-Vis CSVs have the columns `Wavelength (nm)` and `Absorbance`.
Subtract 0.02 from the absorbance, then scale the strongest peak to 1."

```json
[
  {"input": "Absorbance", "function": "subtract", "params": "value=0.02", "output": "Absorbance_corr"},
  {"input": "Absorbance_corr", "function": "normalize_max", "params": "-", "output": "Absorbance_norm"}
]
```

## Reply format

```
Reply with:
1. The file name on its own line, for example `uvvis_cleanup.json`.
2. The complete file in one code block. Never shorten it or leave placeholders such as "..." or "rest unchanged".
3. Two or three short sentences: what the module does and anything the user should check.
If you change the file after the user reports an error, send the complete corrected file again.
```

## How the user tests it

1. Save the file in `Documents/PhysPlot/config/pipelines/` with a name ending in
   `.json` (not `.txt`).
2. Save this script as `apply_pipeline.py` next to a data file. Change the two names
   in quotes to your pipeline and data file.

```python
import json
from physplot import PhysPlot
from physplot.user_paths import user_plugin_dir

pipeline = user_plugin_dir("pipelines") / "uvvis_cleanup.json"
data_file = "sample_A.csv"

pp = PhysPlot()
pp.load(data_file)
for entry in json.loads(pipeline.read_text(encoding="utf-8")):
    params = {}
    for part in entry["params"].split(","):
        if "=" in part:
            name, value = (text.strip() for text in part.split("=", 1))
            try:
                params[name] = float(value)
            except ValueError:
                params[name] = value
    pp.transform(entry["input"], entry["function"], output=entry["output"], **params)
    print("OK:", entry["function"], "->", entry["output"])
print(pp.dataset.dataframe.head())
pp.export_workflow(user_plugin_dir("sequences") / (pipeline.stem + "_sequence.py"))
```

3. Run it with PhysPlot's Python from that folder: `python apply_pipeline.py` (Windows
   installer, PowerShell: `& "$env:LOCALAPPDATA\PhysPlot\venv\Scripts\python.exe" apply_pipeline.py`).
4. It prints one `OK:` line per entry and the first rows with the new columns, and saves
   the steps as `<pipeline name>_sequence.py` in `Documents/PhysPlot/config/sequences/`
   for **Protocol → Import Sequence.py** and **Run Sequence**.

## If PhysPlot shows an error

The script stops with a Python traceback; its last line is the error.

| Message contains | Cause and fix |
|---|---|
| `JSONDecodeError` (`Expecting value`, `Expecting ',' delimiter`, `Expecting property name enclosed in double quotes`) | Not valid JSON: a missing or extra comma, single quotes or a comment. |
| `KeyError: 'params'` (or another key) | An entry lacks one of the four keys. |
| `Unknown column '...'. Available columns: ...` | Wrong `"input"` name; pick one from the list. |
| `Unknown transformation '...'` | Not a built-in name and no transformation file with that name. |
| `got an unexpected keyword argument` | Wrong parameter name for that function (see the table). |
| `does not contain numeric values` | The input column holds text. |
| `FileNotFoundError`, `No such file or directory` | The pipeline or data file name in the script is wrong. |
