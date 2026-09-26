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

PhysPlot discovers function files at startup.

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
   Function that receives a one-dimensional numeric sequence and returns a
   sequence of the same length.

Optional:

``DISPLAY_NAME``
   Text shown in the Function dropdown (default: the file name).

``DEFAULT_LABEL``
   Default label used by the app when a label is needed.

The first line of the module docstring is shown as the menu tooltip.

Minimal Template
----------------

.. code-block:: python

   """Normalize transform for PhysPlot."""

   import numpy as np

   DISPLAY_NAME = "Normalize"
   DEFAULT_LABEL = "Normalized"


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
3. Define ``DEFAULT_LABEL`` for generated labels (optional).
4. Implement ``transform(values)`` and return one value per input row.
5. Choose **File > Reload Config Modules** (or restart PhysPlot) so the function appears in the Function dropdown.

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
