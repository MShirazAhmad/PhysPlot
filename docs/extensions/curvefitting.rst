Curve Fitting and Fit-Model Files
=================================

Fitting Today: Type the Model
-----------------------------

Fitting in PhysPlot needs no file. Type the model instead:

- **Simple Mode**, panel **3. Plotter Module**: choose **Basic Plotter**, tick **LSQ
  fit**, type the model in **Fit Function** (for example ``a*x + b``) and the parameter
  names and starting values in **Params / Initial**, then click **Generate Plot**. The
  fit is saved in the protocol sequence, so it replays in bulk runs.
- **Figure Editor → Fitting → Add Fit Function** takes the same entries for a figure
  that is already open.

Expression syntax: ``x`` is the X column; write powers with ``**`` (never ``^``); the
names ``exp``, ``log`` (natural), ``log10``, ``sqrt``, ``abs``, ``sin``, ``cos``,
``tan``, ``arcsin``, ``arccos``, ``arctan``, ``sinh``, ``cosh``, ``tanh`` and ``np``
are available (write ``np.pi``, not ``pi``). **Params** and **Initial** are
comma-separated lists of the same length, for example ``A,tau,C`` and ``5,2,0``.

Let an AI Assistant Set Up a Fit
--------------------------------

If you know the physics but not the syntax, an AI assistant can turn your model into
the entries above. Attach the guide file `config/fit_functions/AI_GUIDE.md
<https://github.com/MShirazAhmad/PhysPlot/blob/indevelopment/config/fit_functions/AI_GUIDE.md>`_
(click **Download raw file** on that page) to a new chat with ChatGPT, Claude, Gemini,
Copilot or another assistant, add a few rows of your X and Y data if you can, and
describe the model, for example:

.. code-block:: text

   I measure the voltage of a discharging capacitor against time in seconds. It decays
   exponentially towards a small offset: V = A*exp(-t/tau) + C. Please make a curve-fit
   model for it. Typical values are A about 5 V, tau about 2 s and C about 0.1 V.
   Also tell me what to type in LSQ fit.

The reply gives the **Fit Function**, **Params** and **Initial** entries, plus a
legacy fit-model file (see below). If PhysPlot shows a *Plot failed* message, paste it
into the chat for a corrected version. :doc:`ai_assistant` explains the method for
every kind of module.

Legacy Fit-Model Files
----------------------

Files in ``config/fit_functions/`` fill the curve-fit list of PhysPlot's older
plot-configuration window (``physplot/app.py``). The current main window does not open
that window, so these files are only needed by scripts that still use it. Each file
defines one model of one of two kinds:

``poly``
   Polynomial fits using ``numpy.polyfit``.

``callable``
   Custom model functions fitted using ``scipy.optimize.curve_fit``.

The list is built once, when that module is first imported: restart PhysPlot after
adding a file (**File → Reload Config Modules** does not re-read this folder).

Required File Location
----------------------

Put new curve-fitting files in:

.. code-block:: text

   config/fit_functions/

Use numbered filenames to control display order:

.. code-block:: text

   config/fit_functions/12_gaussian.py

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

Step-by-Step: Build a New Curve-Fit Plugin
------------------------------------------

1. Create a new file in ``config/fit_functions/`` (for example
   ``config/fit_functions/12_gaussian.py``).
2. Add ``DISPLAY_NAME``, ``DEFAULT_LABEL`` and ``KIND``.
3. For ``KIND = "poly"``, add ``DEGREE``.
4. For ``KIND = "callable"``, implement ``function(x, ...)`` and optionally
   add ``INITIAL_GUESS``.
5. Restart PhysPlot so the new fit appears in the legacy curve-fit list.

Required Fields
---------------

``DISPLAY_NAME``
   Text shown in the curve-fit list.

``DEFAULT_LABEL``
   Default custom-label text.

``KIND``
   Either ``"poly"`` or ``"callable"``.

``LABEL_MODES``
   Optional. Label choices shown in the configuration window; the default is
   ``["Off", "Equation", "Custom"]``.

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

- ``config/fit_functions/01_linear.py``
- ``config/fit_functions/10_tenth_degree.py``
- ``config/fit_functions/11_exponential_decay.py``
