"""Exponential decay curve fit plugin for PhysPlot.

Definition structure:
    Callable fit with ``KIND = "callable"``. The application passes
    ``function`` to ``scipy.optimize.curve_fit`` with ``INITIAL_GUESS``.

Input data structure:
    ``function(x, a, b)`` receives ``x`` as a one-dimensional numeric array
    and scalar fit parameters ``a`` and ``b``.

Return type:
    ``function`` returns a NumPy array for the model ``a * exp(-b * x)``.

Optional main/runtime behavior:
    Loaded dynamically from the Curve Fitting tab; not intended to run as a
    standalone script.
"""

import numpy as np


DISPLAY_NAME = "A*exp(-bx)"
DEFAULT_LABEL = "Ae^(-bx)"
KIND = "callable"
INITIAL_GUESS = [1.0, 1.0]
LABEL_MODES = ["Off", "Equation", "Custom"]


def function(x, a, b):
    """function(x, a, b) -> numpy.ndarray

    Evaluate the exponential decay model.

    Parameters:
        x (numpy.ndarray): One-dimensional X data array.
        a (float): Amplitude parameter.
        b (float): Decay-rate parameter.

    Returns:
        numpy.ndarray: Model values ``a * exp(-b * x)``.
    """
    return a * np.exp(-b * x)
