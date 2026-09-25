"""Arctan transform for PhysPlot.

Input data structure:
    ``values`` is a one-dimensional NumPy-compatible sequence containing the
    selected table column.

Return type:
    Returns a NumPy array containing ``arctan(values)`` in radians.

Optional main/runtime behavior:
    This file is loaded by the Functions menu and is not intended to be run
    directly.
"""

import numpy as np

DISPLAY_NAME = "arctan(x)"
DEFAULT_LABEL = "arctan(x)"


def transform(values):
    """transform(values) -> numpy.ndarray

    Calculate inverse tangent for each input value.

    Parameters:
        values (Sequence[float]): One-dimensional selected table column.

    Returns:
        numpy.ndarray: Inverse tangent values in radians.
    """
    return np.arctan(values)
