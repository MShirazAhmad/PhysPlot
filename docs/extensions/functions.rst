Function Plugins
================

What Function Plugins Do
------------------------

Function plugins transform one selected table column into another table column.
In the main window, the user selects:

- an input column,
- an output column,
- a function from the Functions dropdown,
- an optional offset.

PhysPlot reads the input column as a one-dimensional numeric array, calls the
plugin's ``transform(values)`` function, then writes the returned values into
the output column.

Where Functions Appear in the UI
--------------------------------

Discovered function plugins are available in:

- Simple Mode's **2. Mathematical Transformation** panel.
- The transform dropdown used when building replayable workflow steps.

PhysPlot discovers function files at startup and again on **File → Reload Config
Modules**.

Layman Example
--------------

If column 1 contains time and column 2 contains voltage, a function plugin can
create a new column containing ``voltage squared`` or ``baseline removed
voltage``. The plugin only needs to know how to transform one list of numbers.

Required File Location
----------------------

Put new function files in:

.. code-block:: text

   config/transformations/

Use a clear filename, for example:

.. code-block:: text

   config/transformations/15_normalize.py

Required Structure
------------------

Every function plugin must define:

``transform(values)``
   Function that receives the input column as a one-dimensional ``float`` NumPy
   array (a copy; blank or text cells are ``NaN``) and returns one value per row.

Optional:

``DISPLAY_NAME``
   Text shown in the Function dropdown (default: the file name).

``DEFAULT_LABEL``
   Read only by the legacy plot window. It does not name the output column; leave
   **Output** empty and PhysPlot names it ``<input>_<DISPLAY_NAME>``.

The first line of the module docstring is shown as the menu tooltip.

Minimal Template
----------------

.. code-block:: python

   """Normalize transform for PhysPlot."""

   import numpy as np

   DISPLAY_NAME = "Normalize"


   def transform(values):
       """transform(values) -> numpy.ndarray

       Normalize the selected table column between 0 and 1.

       Parameters:
           values (Sequence[float]): One-dimensional selected table column.

       Returns:
           numpy.ndarray: Normalized values with the same length as input.
       """
       values = np.asarray(values, dtype=float)
       minimum = np.nanmin(values)
       maximum = np.nanmax(values)
       if maximum == minimum:
           return np.zeros_like(values)
       return (values - minimum) / (maximum - minimum)

Step-by-Step: Build a New Function
----------------------------------

1. Create a new file in ``config/transformations/`` (for example
   ``config/transformations/15_normalize.py``).
2. Define ``DISPLAY_NAME`` for the GUI entry (optional).
3. Implement ``transform(values)`` and return one value per input row.
4. Choose **File → Reload Config Modules** (or restart PhysPlot) so the function
   appears in the Function dropdown.

Let an AI Assistant Write It
----------------------------

You can get a finished function without writing code. The guide file
`config/transformations/AI_GUIDE.md
<https://github.com/MShirazAhmad/PhysPlot/blob/indevelopment/config/transformations/AI_GUIDE.md>`_
tells an AI assistant exactly what PhysPlot expects and includes a complete, tested
example. :doc:`ai_assistant` explains the method for every kind of module.

1. **Download the guide.** Open the link above and click **Download raw file** (the ↓
   button).
2. **Start a new chat** with ChatGPT, Claude, Gemini, Copilot or another assistant, and
   attach ``AI_GUIDE.md``. Give it:

   - the formula, with the units of the input and of the result;
   - two or three example inputs with the results you expect, so it can check itself;
   - optionally a few rows of the column.

3. **Say what you want**, for example:

   .. code-block:: text

      My FTIR spectra have the X column in wavenumber (cm^-1). I want a transformation
      that converts it to wavelength in nm so I can compare with UV-Vis data. Zero or
      negative values should become empty cells. For example, 4000 cm^-1 should give
      2500 nm. Please call it "cm^-1 to nm" in the menu.

4. **Save the reply** in ``Documents/PhysPlot/config/transformations/`` under the file
   name the assistant gives, such as ``20_wavenumber_to_wavelength.py`` (**File → Open
   Config Folder** opens the ``config`` folder). Choose **File → Reload Config
   Modules**, pick the function in **Function**, click **Apply** and check a few values.
5. **If PhysPlot shows an error**, paste the whole message into the chat. The assistant
   sends a corrected complete file; save it over the old one and reload.

Keep the file name once you use the function: saved sequences refer to it by name.
A transformation sees one column, so a calculation that combines two columns (sample
divided by reference, for example) needs a different approach; the assistant will say so.

Function Categories
-------------------

Common categories used by PhysPlot plugins include:

- **Identity/basic**: pass-through operations.
- **Power/reciprocal**: ``x^2``, ``x^3``, ``1/x``.
- **Log/exp**: ``log10``, ``ln``, ``e^x``.
- **Trigonometric**: ``sin``, ``cos``, ``tan``, inverse trig.
- **Domain-specific**: custom transforms such as baseline correction.

Practical Rules
---------------

- Return the same number of values that you received.
- Use ``numpy.asarray(values, dtype=float)`` if you need NumPy operations.
- Avoid changing files, opening windows, or modifying the table directly.
- Handle edge cases such as blank columns, zeros, or repeated values. Blank or
  non-numeric cells arrive as ``NaN``.
- Do not name a file after a built-in transformation (``normalize_max``,
  ``multiply``, ``add``, ``subtract``, ``divide``, ``log``, ``log10``,
  ``baseline_subtract``); such files are skipped. Keep the ``NN_`` prefix.

Sequences and Headless Runs
---------------------------

Applying a function plugin records a ``TransformColumnStep`` in the protocol
sequence. Its ``function_name`` is the file stem, and the Simple Mode offset
(and multiplier) are stored as parameters:

.. code-block:: python

   TransformColumnStep(
       input_column="Voltage",
       function_name="02_square",
       output="Voltage_sq",
       params={"multiplier": 1.0, "offset": 0.5},
   )

The step computes ``transform(values) * multiplier + offset``. The backend
resolves the name against the same folders the GUI uses (``Documents/PhysPlot/
config/transformations`` first, then the bundled ``config/transformations``),
so **Apply This Sequence**, exported ``Sequence.py`` files and bulk runs replay
the plugin without the GUI. Notebooks can call it directly by file stem or
``DISPLAY_NAME``:

.. code-block:: python

   pp.transform("Voltage", "02_square", output="Voltage_sq")
   pp.transform("Voltage", "x^2", output="Voltage_sq")

Extra keyword arguments are passed to ``transform(values, **params)``. Renaming
or deleting a plugin file breaks saved sequences that use it.

Existing Examples
-----------------

See:

- ``config/transformations/01_identity.py``
- ``config/transformations/05_log10.py``
- ``config/transformations/14_xrd_baseline_remove.py``
