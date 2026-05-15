Function Plugins
================

What Function Plugins Do
------------------------

Function plugins transform one selected table column into another table column.
In the main window, the user selects:

- an input column,
- an output column,
- a function from the Functions dropdown,
- an optional multiplier and offset.

PhysPlot reads the input column as a one-dimensional numeric array, calls the
plugin's ``transform(values)`` function, then writes the returned values into
the output column.

Where Functions Appear in the UI
--------------------------------

Discovered function plugins are available in:

- The top-bar **Functions** menu
- The transform dropdown in the data-manipulation controls

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

   functions/

Use a clear filename, for example:

.. code-block:: text

   functions/15_normalize.py

Required Structure
------------------

Every function plugin should define:

``DISPLAY_NAME``
   Text shown in the PhysPlot Functions dropdown.

``DEFAULT_LABEL``
   Default label used by the app when a label is needed.

``transform(values)``
   Function that receives a one-dimensional numeric sequence and returns a
   sequence of the same length.

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

1. Create a new file in ``functions/`` (for example
   ``functions/15_normalize.py``).
2. Define ``DISPLAY_NAME`` for the GUI entry.
3. Define ``DEFAULT_LABEL`` for generated labels.
4. Implement ``transform(values)`` and return one value per input row.
5. Restart PhysPlot so the function appears in the menu and dropdown.

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
- Handle edge cases such as blank columns, zeros, or repeated values.

Existing Examples
-----------------

See:

- ``functions/01_identity.py``
- ``functions/05_log10.py``
- ``functions/14_xrd_baseline_remove.py``
