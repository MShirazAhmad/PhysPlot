# Curve-Fit Models: guide for AI assistants

> **PhysPlot users:** attach this file to a chat with any AI assistant (ChatGPT, Claude, Gemini, Copilot, ...), together with the model equation you want to fit and, if you can, a few rows of your X and Y data. Then describe what you want. The assistant replies with one complete file: save it in `Documents/PhysPlot/config/fit_functions/` and restart PhysPlot (**File → Reload Config Modules** does not re-read this folder). Most fits need no file: type the model, for example `a*x + b`, in Simple Mode's **LSQ fit** or the Figure Editor's **Add Fit Function**. Step-by-step help: https://physplot.readthedocs.io/en/latest/extensions/ai_assistant.html

## Your task

Know first where these files are used today:

- Files in `config/fit_functions/` fill the **legacy** curve-fit list: the *Curve Fitting*
  tab of PhysPlot's older plot-configuration window (module `physplot/app.py`). The current
  PhysPlot window never opens that legacy window. A new file here therefore does not appear
  anywhere in the current GUI, and it is not part of protocol sequences or bulk runs.
- Fitting in current PhysPlot needs no file. In Simple Mode, panel **3. Plotter Module**, the
  user ticks **LSQ fit**, types the model in **Fit Function** (for example `a*x + b`), and
  types the parameter names and starting values in **Params / Initial**. The Figure Editor's
  **Fitting → Add Fit Function** takes the same entries. The Simple Mode LSQ fit is saved in
  the protocol sequence and replays in bulk runs.

Do both of these:

1. Write exactly one Python file for the legacy list, named `NN_short_name.py`: two
   digits, an underscore, then lowercase words joined by underscores, for example
   `20_exp_decay_offset.py`. The bundled files use `01_` to `11_`, so start at `20_`. A
   user file with the same name as a bundled file replaces it. The list is sorted by file
   name as text.
2. Also give the typed-expression version of the same model (see Rules). It is what the
   user can use right now.

## Ask the user first

If the request does not already say, ask for the missing items in one short message.
Ask briefly rather than guess.

1. The model equation, and what x and y are, with units.
2. The meaning of each fit parameter, and any that must stay positive (such as a lifetime).
3. Rough starting values for the parameters, or a few rows of their X and Y data so you can
   estimate them.
4. The label for the fit list (`DISPLAY_NAME`) and the default legend text (`DEFAULT_LABEL`),
   if they have a preference.
5. Whether the model is simply a polynomial. Then use `KIND = "poly"`.

## The file PhysPlot expects

| Name | Required | Type | Meaning |
| --- | --- | --- | --- |
| `DISPLAY_NAME` | yes | `str` | Text in the legacy curve-fit list. |
| `DEFAULT_LABEL` | yes | `str` | Default legend text in the *Custom* label mode. |
| `KIND` | yes | `"poly"` or `"callable"` | Polynomial fit, or a model function fitted by SciPy. |
| `DEGREE` | if `KIND == "poly"` | `int` | Polynomial degree, 1 or more. |
| `function(x, p1, p2, ...)` | if `KIND == "callable"` | function | The model. `x` first, then one float argument per fit parameter. |
| `INITIAL_GUESS` | no, but recommended | list of `float` | One starting value per parameter, in the order of `function`. Without it SciPy starts every parameter at `1.0`. |
| `LABEL_MODES` | no | list of `str` | Legend modes offered. Default and recommended: `["Off", "Equation", "Custom"]`. |
| module docstring | no | `str` | Not shown in the GUI. Use it to state the equation and units. |

How PhysPlot uses the file:

- When the legacy module is first imported, it imports every `*.py` file in
  `Documents/PhysPlot/config/fit_functions/` and the bundled `config/fit_functions/`,
  sorted by file name. Other files, such as this guide, are ignored. The list is read once
  per PhysPlot session, so a new or edited file needs a restart.
- Errors are not caught: a missing required name, a wrong `KIND` or a syntax error in any
  one file stops the whole legacy module from loading.
- `x` and `y` are one-dimensional `float` NumPy arrays of the X and Y columns.
- `KIND = "poly"`: `coefficients = numpy.polyfit(x, y, DEGREE)`, drawn with
  `numpy.poly1d(coefficients)(x)`. Coefficients run from the highest power down.
- `KIND = "callable"`: `popt, pcov = scipy.optimize.curve_fit(function, x, y, p0=INITIAL_GUESS)`
  with no bounds, then the line `function(x, *popt)` is drawn at the data's x values.
- The *Equation* legend names the fitted values `a`, `b`, `c`, ... in order, for example
  `fit: a= 5, b=2.5, c=0.81`, not by your argument names.

## Rules

- Import only NumPy, SciPy, pandas, Matplotlib and the Python standard library. A model
  normally needs only NumPy.
- `function` must accept a NumPy array `x` and return an array of the same shape. Start
  with `x = np.asarray(x, dtype=float)` and use vectorised NumPy (`np.exp`, `np.where`),
  never a Python `if` on arrays or a loop over points.
- The parameters after `x`, the values in `INITIAL_GUESS` and the typed **Params** list use
  the same order and the same count.
- Choose starting values that are physically sensible and close to the data, for example
  an amplitude near the range of y and a time constant near a third of the x range. A poor
  start can give a flat or wrong curve without any error.
- `curve_fit` has no bounds here. Write the model so that the natural parameter is positive
  (for example `exp(-x / tau)` with `tau > 0`) and start it on the right side of zero.
- `function` must not print, raise on purpose, or read files: SciPy calls it many times with
  trial values.
- For a polynomial use `KIND = "poly"` with `DEGREE`; do not write a callable. Do not copy the
  bundled `01_linear.py` to `11_exponential_decay.py` (degrees 1 to 10 and `A*exp(-bx)`).
- At the top level the file may only import modules and define constants and the function.
  No file or network access, no printing, no GUI code, no `sys.exit()`.
- Typed-expression version for **LSQ fit** and **Add Fit Function**: `x` is the X column;
  powers use `**` (never `^`); available names are `exp`, `log` (natural), `log10`, `sqrt`,
  `abs`, `sin`, `cos`, `tan`, `arcsin`, `arccos`, `arctan`, `sinh`, `cosh`, `tanh` and `np`
  (write `np.pi`, not `pi`). Parameter names must not be `x`, `np` or one of those names.
  **Params** and **Initial** are comma-separated lists of the same length.

## Complete working example

The user asked: "Fit capacitor discharge voltage against time. It decays exponentially
towards a small offset." File name: `20_exp_decay_offset.py`

```python
"""Exponential decay with a constant background: y = A * exp(-x / tau) + C.

Typical uses: capacitor discharge, fluorescence or phosphorescence decay,
radioactive decay counts on top of a background. x is time, tau has the same
unit as x, and A and C have the unit of y.
"""

import numpy as np

DISPLAY_NAME = "A*exp(-x/tau) + C"
DEFAULT_LABEL = "Exponential decay fit"
KIND = "callable"
INITIAL_GUESS = [1.0, 1.0, 0.0]  # A, tau, C in the order of function()
LABEL_MODES = ["Off", "Equation", "Custom"]


def function(x, amplitude, tau, background):
    """Return A * exp(-x / tau) + C for every value in the array x."""
    x = np.asarray(x, dtype=float)
    return amplitude * np.exp(-x / tau) + background
```

Typed-expression version: **Fit Function** `A*exp(-x/tau) + C`, **Params / Initial**
`A,tau,C` and `1,1,0`.

A polynomial model needs no function. A complete quadratic file:

```python
"""Quadratic fit: y = a*x**2 + b*x + c."""

DISPLAY_NAME = "Quadratic (a*x^2 + b*x + c)"
DEFAULT_LABEL = "Quadratic fit"
KIND = "poly"
DEGREE = 2
LABEL_MODES = ["Off", "Equation", "Custom"]
```

## Reply format

```
Reply with:
1. The file name on its own line, for example `20_exp_decay_offset.py`.
2. The complete file in one code block. Never shorten it or leave placeholders such as "..." or "rest unchanged".
3. Two or three short sentences: what the module does and anything the user should check.
If you change the file after the user reports an error, send the complete corrected file again.
```

After the sentences, add one line with the typed-expression version, for example:
`LSQ fit: Fit Function A*exp(-x/tau) + C | Params A,tau,C | Initial 1,1,0`.

## How the user tests it

1. Save the file in `Documents/PhysPlot/config/fit_functions/` with exactly the name given.
   It must end in `.py`, not `.py.txt`. **File → Open Config Folder** opens
   `Documents/PhysPlot/config/`.
2. Restart PhysPlot. Nothing new appears in the current window; that is expected.
3. Try the model on real data with the typed expression: import the data, set the X and Y
   roles, and in Simple Mode panel **3. Plotter Module** choose **Basic Plotter**, tick
   **LSQ fit**, enter the **Fit Function** and **Params / Initial** from the reply, then
   press **Generate Plot**. The fitted line is labelled
   `LSQ fit: <expression> (A=..., tau=..., C=...)`. Check that the values make physical sense.
4. Check the file itself with the loader the legacy window uses (a terminal or notebook that
   uses PhysPlot's Python):

```python
import numpy as np
from scipy.optimize import curve_fit
from physplot import app as legacy  # reads every file in config/fit_functions

models = {d["path"].name: d for d in legacy.CURVE_FIT_DEFINITIONS}
model = models["20_exp_decay_offset.py"]  # KeyError: file not found in config/fit_functions
x = np.linspace(0, 10, 50)
y = model["function"](x, 5.0, 2.5, 0.8)  # made-up data with A=5, tau=2.5, C=0.8
popt, _ = curve_fit(model["function"], x, y, p0=model["initial_guess"])
print(model["display_name"], np.round(popt, 3))  # expect [5.  2.5 0.8]
# For KIND = "poly" use: print(np.polyfit(x, y, model["degree"]))
```

## If PhysPlot shows an error

The user pastes the message. Find the cause below, fix the file, and send the complete
corrected file.

| The user sees | Cause and fix |
| --- | --- |
| `AttributeError: <file> must define DISPLAY_NAME` (or `DEFAULT_LABEL`, `KIND`) | A required name is missing. Add it. |
| `AttributeError: <file> must define DEGREE` or `must define function(x, ...)` | `KIND = "poly"` needs `DEGREE`; `KIND = "callable"` needs `function`. |
| `ValueError: <file> KIND must be 'poly' or 'callable'` | Fix the spelling of `KIND`. |
| `SyntaxError` or `ModuleNotFoundError` naming the file | Fix the line named, or use only the allowed packages. |
| `KeyError: '<file name>'` in the Python check | The file is not in `config/fit_functions/`, or its name differs. |
| `TypeError: function() missing 1 required positional argument` or `takes 3 positional arguments but 4 were given` | `INITIAL_GUESS` (or **Initial**) has a different count from the parameters. |
| `Optimal parameters not found: ...` | The fit did not converge. Give better starting values. |
| A flat or clearly wrong fitted line | Starting values are far off, or a parameter has the wrong sign. |
| *Plot failed*: `LSQ initial guesses must match the parameter list.` | **Params** and **Initial** have different lengths. |
| *Plot failed*: `Not enough numeric points for the requested LSQ fit.` | Fewer rows with numbers in both X and Y than there are parameters. |
| *Plot failed*: `No column has role 'X'.` (or `'Y'`) | Set the X and Y roles in the dropdowns above the table. |
| *Plot failed*: `name 'pi' is not defined` (or another name) | The typed expression uses a name that is not available. Use `np.pi`, `np.<function>` or the names listed in Rules. |
| *Plot failed*: `ufunc 'bitwise_xor' not supported ...` | The typed expression uses `^`. Use `**` for powers. |
