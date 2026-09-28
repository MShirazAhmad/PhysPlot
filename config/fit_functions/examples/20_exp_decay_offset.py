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
