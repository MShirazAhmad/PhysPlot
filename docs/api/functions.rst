Function Plugin API
===================

Function plugins live in the top-level ``functions`` folder. PhysPlot loads
these files from disk, so their filenames may start with numbers for menu
ordering, but their public API should stay simple and predictable.

Required Module Variables
-------------------------

``DISPLAY_NAME: str``
    The name shown in the mathematical transformation dropdown.

Required Function
-----------------

.. py:function:: transform(values) -> numpy.ndarray

   Transform one numeric column and return the transformed values.

   :param values: One-dimensional numeric input values, usually a
      ``numpy.ndarray`` copied from the selected table column.
   :type values: array-like
   :returns: One-dimensional numeric output values with the same row order as
      the input.
   :rtype: numpy.ndarray

Plugin Files Included with PhysPlot
-----------------------------------

.. list-table::
   :header-rows: 1
   :widths: 28 32 40

   * - File
     - Display name
     - Core behavior
   * - ``functions/01_identity.py``
     - ``x``
     - Returns the input values unchanged.
   * - ``functions/02_square.py``
     - ``x^2``
     - Squares each value.
   * - ``functions/03_cube.py``
     - ``x^3``
     - Cubes each value.
   * - ``functions/04_reciprocal.py``
     - ``1/x``
     - Returns the reciprocal of each value.
   * - ``functions/05_log10.py``
     - ``log10(x)``
     - Applies base-10 logarithm.
   * - ``functions/06_log.py``
     - ``ln(x)``
     - Applies natural logarithm.
   * - ``functions/07_exponential.py``
     - ``e^x``
     - Applies the exponential function.
   * - ``functions/08_cos.py``
     - ``cos(x)``
     - Applies cosine.
   * - ``functions/09_sin.py``
     - ``sin(x)``
     - Applies sine.
   * - ``functions/10_tan.py``
     - ``tan(x)``
     - Applies tangent.
   * - ``functions/11_arccos.py``
     - ``arccos(x)``
     - Applies inverse cosine.
   * - ``functions/12_arcsin.py``
     - ``arcsin(x)``
     - Applies inverse sine.
   * - ``functions/13_arctan.py``
     - ``arctan(x)``
     - Applies inverse tangent.
   * - ``functions/14_xrd_baseline_remove.py``
     - ``XRD: Baseline Remove``
     - Estimates and subtracts a smooth baseline from diffraction-style data.

Implementation Notes
--------------------

Each function file should import only what it needs. For most transformations,
``numpy`` is enough. Avoid editing table widgets or figure-editor windows inside a
function plugin; PhysPlot handles reading the selected column, writing the
output column, and refreshing the plot.

Files with spaces in their names cannot be imported as normal Python modules.
Prefer filenames such as ``15_my_function.py``.
