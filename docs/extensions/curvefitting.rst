Curve-Fitting Plugins
=====================

What Curve-Fitting Plugins Do
-----------------------------

Curve-fitting plugins define mathematical models that can be fitted to the
active plot's X and Y data. In the configuration window, the user chooses a
label mode and then selects a fit type from the visible curve-fit list.

PhysPlot supports two plugin kinds:

``poly``
   Polynomial fits using ``numpy.polyfit``.

``callable``
   Custom model functions fitted using ``scipy.optimize.curve_fit``.

Layman Example
--------------

If your plotted data looks like a line, choose a linear fit. If your plotted
data follows exponential decay, choose an exponential model. A curve-fitting
plugin is simply a small file that tells PhysPlot what equation to use.

Required File Location
----------------------

Put new curve-fitting files in:

.. code-block:: text

   curvefitting/

Use numbered filenames to control display order:

.. code-block:: text

   curvefitting/12_gaussian.py

Polynomial Template
-------------------

.. code-block:: python

   """Quadratic curve fit plugin for PhysPlot."""

   DISPLAY_NAME = "Quadratic"
   DEFAULT_LABEL = "Quadratic"
   KIND = "poly"
   DEGREE = 2
   LABEL_MODES = ["Off", "Equation", "Custom"]

For polynomial fits, PhysPlot calculates the model with:

.. code-block:: python

   coefficients = numpy.polyfit(x, y, DEGREE)

Callable Template
-----------------

.. code-block:: python

   """Gaussian curve fit plugin for PhysPlot."""

   import numpy as np

   DISPLAY_NAME = "Gaussian"
   DEFAULT_LABEL = "Gaussian"
   KIND = "callable"
   INITIAL_GUESS = [1.0, 0.0, 1.0]
   LABEL_MODES = ["Off", "Equation", "Custom"]


   def function(x, amplitude, center, width):
       """function(x, amplitude, center, width) -> numpy.ndarray

       Evaluate a Gaussian model.

       Parameters:
           x (numpy.ndarray): One-dimensional X data array.
           amplitude (float): Peak height.
           center (float): Peak center position.
           width (float): Peak width.

       Returns:
           numpy.ndarray: Model Y values for the input X array.
       """
       return amplitude * np.exp(-((x - center) / width) ** 2)

Required Fields
---------------

``DISPLAY_NAME``
   Text shown in the curve-fit list.

``DEFAULT_LABEL``
   Default custom-label text.

``KIND``
   Either ``"poly"`` or ``"callable"``.

``LABEL_MODES``
   Label choices shown in the configuration window, usually ``["Off",
   "Equation", "Custom"]``.

``DEGREE``
   Required only for ``KIND = "poly"``.

``function(x, ...)``
   Required only for ``KIND = "callable"``.

``INITIAL_GUESS``
   Optional but strongly recommended for callable fits. It gives SciPy a
   starting point for the unknown parameters.

Practical Rules
---------------

- Use polynomial plugins for simple polynomial equations.
- Use callable plugins for physical models such as Gaussian, Lorentzian,
  exponential decay, or instrument response functions.
- Keep the function vectorized: it should accept a NumPy array ``x`` and return
  a NumPy array.
- If fitting fails, try better ``INITIAL_GUESS`` values.

Existing Examples
-----------------

See:

- ``curvefitting/01_linear.py``
- ``curvefitting/10_tenth_degree.py``
- ``curvefitting/11_exponential_decay.py``
