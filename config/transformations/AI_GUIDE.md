# Mathematical Transformations: guide for AI assistants

> **PhysPlot users:** attach this file to a chat with any AI assistant (ChatGPT, Claude, Gemini, Copilot, ...), together with the formula you want and two or three example values (an input number and the result you expect). Then describe what you want. The assistant replies with one complete file: save it in `Documents/PhysPlot/config/transformations/` and choose **File → Reload Config Modules** in PhysPlot. Step-by-step help: https://physplot.readthedocs.io/en/latest/extensions/ai_assistant.html

## Your task

Write exactly one Python file that adds a function to the **Function** list of the
Simple Mode panel **2. Mathematical Transformation** in PhysPlot. The function turns one
table column into new values, one output value per row.

- PhysPlot loads every `*.py` file in `Documents/PhysPlot/config/transformations/` and in
  its bundled `config/transformations/`, and calls the file's `transform(values)`.
- Name the file `NN_short_name.py`: two digits, an underscore, then lowercase words joined
  by underscores, for example `20_wavenumber_to_wavelength.py`. Use only `a-z`, `0-9` and `_`.
- Plugin functions are listed after the built-in functions, sorted by file name as text.
  PhysPlot's own files use `01_` to `14_`, so start at `20_` and always use two digits.
- The file name without `.py` (the stem, here `20_wavenumber_to_wavelength`) is the name a
  saved protocol sequence records. Renaming the file later breaks every saved sequence that
  uses it, so choose a lasting name.
- Do not reuse a bundled file name (`01_identity.py` to `14_xrd_baseline_remove.py`): a user
  file with the same name replaces the bundled one. Do not name the file after a built-in
  transformation (`normalize_max`, `multiply`, `add`, `subtract`, `divide`, `log`, `log10`,
  `baseline_subtract`); PhysPlot skips such files.
- A transformation sees one column only. If the calculation needs two or more columns (for
  example sample divided by reference), tell the user that a transformation file cannot do
  it instead of writing one.

## Ask the user first

If the request does not already say, ask for the missing items in one short message.
Ask briefly rather than guess.

1. The formula or operation, the unit of the input column and the unit of the result.
2. What to do with zeros, negative values and blank cells: give `NaN` (an empty cell) for
   those rows, or stop with an error message.
3. Two or three example input values and the results they expect. Check your formula
   against them before you reply.
4. The label for the **Function** list (`DISPLAY_NAME`), if they have a preference.
5. Whether a constant in the formula (path length, temperature, calibration factor) is
   fixed, or should be changeable later.

## The file PhysPlot expects

| Name | Required | Type | Meaning |
| --- | --- | --- | --- |
| `transform(values)` | yes | function | Receives the column and returns the new values. |
| `DISPLAY_NAME` | no | `str` | Label in the **Function** list. Default: the stem with `_` replaced by spaces, in title case (`20 Wavenumber To Wavelength`). |
| module docstring | no | `str` | Its first line, followed by the file name, is the tooltip of the list entry. |
| `DEFAULT_LABEL` | no | `str` | Kept for older PhysPlot windows. The current window ignores it; it does not name the output column. |

How PhysPlot calls `transform`:

- `values` is a one-dimensional NumPy array of `float64`: a copy of the **Input** column, so
  changing it in place is safe. Blank and non-numeric cells arrive as `NaN`. It is not a
  pandas Series. PhysPlot refuses a column with no numbers before calling `transform`.
- The return value is converted with `numpy.asarray(result, dtype=float)`. It must hold
  exactly one number per row: a 1-D array, list or Series of the same length (an `(n, 1)`
  column is also accepted). A single number is copied to every row.
- The stored result is `transform(values) * multiplier + offset`. `offset` is the number in
  the panel's **+** box (default `0`); `multiplier` is always `1` in Simple Mode. Do not
  add an offset or factor of your own for these.
- The result goes to the **Output** column the user picks or types. If **Output** is left
  empty, the new column is named `<input column>_<DISPLAY_NAME>`, for example
  `Wavenumber_cm^-1 to nm`.
- Applying it records a `TransformColumnStep` with `function_name` set to the stem and
  `params={"multiplier": 1.0, "offset": <the + value>}`. **Apply This Sequence**, exported
  `Sequence.py` files, the `physplot` command line and bulk runs find the file by its stem
  and replay it without the GUI. They load the file again each time, so an edited file
  changes later replays.

## Rules

- Import only NumPy, pandas, SciPy, Matplotlib and the Python standard library. Prefer NumPy.
- Start `transform` with `values = np.asarray(values, dtype=float)`. Use vectorised NumPy
  operations, not a Python loop over rows.
- Return exactly one value per input row, in the same order. Never drop, sort or add rows.
  Blank cells stay blank: a `NaN` input gives a `NaN` output.
- For a row with no valid result (for example the logarithm of a negative number), return
  `NaN`. Never return `inf`. Prevent it with a mask or `np.where`, or compute inside
  `with np.errstate(divide="ignore", invalid="ignore"):` and replace non-finite results with
  `NaN`. NumPy warnings only reach the terminal, so the user never sees them.
- If the whole column is unusable (for example no positive values for a logarithm), raise
  `ValueError` with a message that names the function and tells the user what to do.
- Return real numbers only: no text, no `None`, no complex values.
- Put constants in UPPER_CASE names near the top, with their unit in the name or a comment.
  If the user wants to change a constant later, make it a keyword argument with a default,
  for example `def transform(values, path_length_cm=1.0):`. The panel always uses the
  default; another value can be set in the step's `params` in the Build Protocol **Code**
  view. Never name a parameter `series`, `multiplier` or `offset`.
- At the top level the file may only import modules and define constants and functions.
  PhysPlot runs the file each time it builds the Function list and each time a sequence
  replays. No file or network access, no printing, no GUI code (Qt, dialogs, plots), no
  `input()`, no `sys.exit()`.
- Write a module docstring whose first line says what the function does, with units.
- Keep `DISPLAY_NAME` short (under about 25 characters) and different from the existing
  labels: `x`, `x^2`, `x^3`, `1/x`, `log10(x)`, `log(x)`, `e^x`, `cos(x)`, `sin(x)`,
  `tan(x)`, `arccos(x)`, `arcsin(x)`, `arctan(x)`, `XRD: Baseline Remove` and the built-in
  names. A duplicate label is shown as `<label> (<stem>)`.
- Trigonometric functions in NumPy use radians; convert degrees with `np.deg2rad`.

## Complete working example

The user asked: "Convert my FTIR X column from wavenumber in cm^-1 to wavelength in nm.
Zero and negative values should become empty cells." File name:
`20_wavenumber_to_wavelength.py`

```python
"""Convert wavenumber in cm^-1 to wavelength in nm (wavelength = 1e7 / wavenumber).

Input: one table column of wavenumbers in cm^-1, for example the X column of an
FTIR or Raman spectrum. Output: wavelength in nm, one value per row.
Blank cells, zero and negative wavenumbers give NaN (an empty cell).
"""

import numpy as np

DISPLAY_NAME = "cm^-1 to nm"
DEFAULT_LABEL = "Wavelength (nm)"

NM_PER_CM = 1.0e7


def transform(values):
    """Return the wavelength in nm for each wavenumber in cm^-1."""
    wavenumber = np.asarray(values, dtype=float)
    positive = wavenumber > 0  # NaN compares as False, so blank cells stay NaN
    if not positive.any():
        raise ValueError(
            "cm^-1 to nm: the input column has no positive wavenumbers. "
            "Choose the column that holds wavenumbers in cm^-1."
        )
    wavelength = np.full(wavenumber.shape, np.nan)
    wavelength[positive] = NM_PER_CM / wavenumber[positive]
    return wavelength
```

Check: 4000 cm^-1 gives 2500 nm, 2000 cm^-1 gives 5000 nm, 0 and blank give an empty cell.

## Reply format

```
Reply with:
1. The file name on its own line, for example `20_wavenumber_to_wavelength.py`.
2. The complete file in one code block. Never shorten it or leave placeholders such as "..." or "rest unchanged".
3. Two or three short sentences: what the module does and anything the user should check.
If you change the file after the user reports an error, send the complete corrected file again.
```

## How the user tests it

1. Save the file in `Documents/PhysPlot/config/transformations/` with exactly the name
   given. It must end in `.py`, not `.py.txt`. **File → Open Config Folder** opens
   `Documents/PhysPlot/config/`.
2. In PhysPlot choose **File → Reload Config Modules** (`Ctrl+Shift+R`), or restart PhysPlot.
3. In Simple Mode, panel **2. Mathematical Transformation**, open **Function**. The new
   label is near the end of the list. Hover over it to see the docstring line.
4. Choose the **Input** column, leave **+** at `0`, type a new column name in **Output**
   (for example `Wavelength (nm)`) and press **Apply**.
5. Check that the status bar says *Transformation applied*, that the new column matches
   the example values, and that blank cells stayed blank. In Advanced Mode, Build Protocol
   now has a *Transform* row.

Optional check in Python (a terminal or notebook that uses PhysPlot's Python). It uses the
same lookup as a replayed sequence and shows the real error if the file cannot load:

```python
import numpy as np
import pandas as pd
from physplot.core.transformations import get_transform

f = get_transform("20_wavenumber_to_wavelength")  # the same lookup a saved sequence uses
print(f(pd.Series([4000.0, 2000.0, 0.0, np.nan])).tolist())
# expected: [2500.0, 5000.0, nan, nan]
```

## If PhysPlot shows an error

The user pastes the message. Find the cause below, fix the file, and send the complete
corrected file.

| The user sees | Cause and fix |
| --- | --- |
| The label is not in **Function** after Reload | The file did not load. PhysPlot prints `Skipping transformation plugin <path>: <reason>` only to the terminal. Causes: wrong folder, name not ending in `.py`, a syntax error, an error or failing import at the top level, no `transform` function, or a built-in name as the stem. The Python check shows the reason. |
| *Transformation failed*: `Transformation '<stem>' failed: <ErrorType>: <text>` | `transform` raised an error. If it is your own `ValueError`, the user probably chose the wrong column; otherwise fix the code. |
| `... returned an array of shape (k,) for a column of n rows; return one value per row.` | The result has a different length. Do not drop `NaN` rows; pad the ends after `np.diff` or a `"valid"` convolution. |
| `... returned None; transform(values) must return the new values.` | `transform` has no `return`. |
| `... returned non-numeric values: ...` | The result contains text or other objects. Return floats. |
| `... failed: TypeError: transform() got an unexpected keyword argument '<name>'` | The step's `params` name a parameter that `transform` does not accept. Add it as a keyword argument with a default, or remove it from `params`. |
| `Column '<name>' does not contain numeric values for transformation.` | The Input column has no numbers. Not a file problem: choose another column. |
| `Unknown transformation '<stem>'. ... no plugin file '<stem>.py' ... was found ...` | A saved sequence names a file that was renamed, deleted or is missing on this computer. Restore the file under its old name, or change `function_name` in the Build Protocol **Code** view. |
| A Python error such as `expected ':' (20_name.py, line 12)` when a sequence replays | The file exists but cannot load. Fix the line named in the message. |
| Cells show `inf`, or wrong numbers | Division by zero or a wrong formula or unit. Return `NaN` for invalid rows and compare with the user's example values. |
