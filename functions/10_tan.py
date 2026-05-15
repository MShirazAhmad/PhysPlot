"""Tangent transform for PhysPlot.

Input data structure:
    ``values`` is a one-dimensional NumPy-compatible sequence containing the
    selected table column, interpreted in radians.

Return type:
    Returns a NumPy array containing ``tan(values)``.

Optional main/runtime behavior:
    This file is loaded by the Functions menu and is not intended to be run
    directly.
"""

import numpy as np

DISPLAY_NAME = "tan(x)"
DEFAULT_LABEL = "tan(x)"


def transform(values):
    """transform(values) -> numpy.ndarray

    Calculate tangent for each input value.

    Parameters:
        values (Sequence[float]): One-dimensional selected table column in
            radians.

    Returns:
        numpy.ndarray: Tangent values.
    """
    return np.tan(values)
