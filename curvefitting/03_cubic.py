"""Cubic curve fit plugin for PhysPlot.

Definition structure:
    Polynomial fit with ``DEGREE = 3``. The application computes
    ``numpy.polyfit(x, y, DEGREE)`` using the selected plot X/Y arrays.

Input data structure:
    ``x`` and ``y`` are one-dimensional numeric arrays from the selected
    table columns.

Return type:
    This plugin file returns no value directly; it declares metadata consumed
    by the curve-fitting engine.

Optional main/runtime behavior:
    Loaded dynamically from the Curve Fitting tab; not intended to run as a
    standalone script.
"""

DISPLAY_NAME = "Cubic"
DEFAULT_LABEL = "Cubic"
KIND = "poly"
DEGREE = 3
LABEL_MODES = ["Off", "Equation", "Custom"]
