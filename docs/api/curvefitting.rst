Curve-Fitting Plugin API
========================

Curve-fitting plugins live in the top-level ``curvefitting`` folder. PhysPlot
reads these files to populate the curve-fitting configuration screen and to
choose the correct fitting routine.

Required Module Variables
-------------------------

``DISPLAY_NAME: str``
    The fit name shown in the GUI list.

``DEFAULT_LABEL: str``
    The default custom label text shown when a user selects custom labeling.

``KIND: str``
    The fitting family. Use ``"poly"`` for polynomial fits and ``"callable"``
    for fits that provide their own model function.

``LABEL_MODES: tuple[str, ...]``
    The allowed label modes. PhysPlot currently understands ``"Off"``,
    ``"Equation"``, and ``"Custom"``.

Polynomial Fit Variables
------------------------

``DEGREE: int``
    Required when ``KIND = "poly"``. PhysPlot passes this value to the
    polynomial fitter.

Callable Fit Function
---------------------

.. py:function:: function(x, *parameters) -> numpy.ndarray

   Evaluate a custom model for curve fitting.

   :param x: One-dimensional x-axis values from the selected data.
   :type x: array-like
   :param parameters: Numeric fit parameters estimated by the curve fitter.
   :type parameters: float
   :returns: Model y-values evaluated at ``x``.
   :rtype: numpy.ndarray

Included Fit Plugins
--------------------

.. list-table::
   :header-rows: 1
   :widths: 30 26 18 26

   * - File
     - Display name
     - Kind
     - Meaning
   * - ``curvefitting/01_linear.py``
     - ``Linear``
     - ``poly``
     - First-degree polynomial.
   * - ``curvefitting/02_quadratic.py``
     - ``Quadratic``
     - ``poly``
     - Second-degree polynomial.
   * - ``curvefitting/03_cubic.py``
     - ``Cubic``
     - ``poly``
     - Third-degree polynomial.
   * - ``curvefitting/04_fourth_degree.py``
     - ``4th degree``
     - ``poly``
     - Fourth-degree polynomial.
   * - ``curvefitting/05_fifth_degree.py``
     - ``5th degree``
     - ``poly``
     - Fifth-degree polynomial.
   * - ``curvefitting/06_sixth_degree.py``
     - ``6th degree``
     - ``poly``
     - Sixth-degree polynomial.
   * - ``curvefitting/07_seventh_degree.py``
     - ``7th degree``
     - ``poly``
     - Seventh-degree polynomial.
   * - ``curvefitting/08_eighth_degree.py``
     - ``8th degree``
     - ``poly``
     - Eighth-degree polynomial.
   * - ``curvefitting/09_ninth_degree.py``
     - ``9th degree``
     - ``poly``
     - Ninth-degree polynomial.
   * - ``curvefitting/10_tenth_degree.py``
     - ``10th degree``
     - ``poly``
     - Tenth-degree polynomial.
   * - ``curvefitting/11_exponential_decay.py``
     - ``A*exp(-bx)``
     - ``callable``
     - Exponential decay model.

Implementation Notes
--------------------

Keep fit files small. The file should describe one fit, not draw the plot or
change the GUI directly. PhysPlot handles selecting x/y data, calculating the
coefficients, drawing the fitted curve, and formatting labels.
