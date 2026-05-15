"""Cosine transform for PhysPlot.

Input data structure:
    ``values`` is a one-dimensional NumPy-compatible sequence containing the
    selected table column, interpreted in radians.

Return type:
    Returns a NumPy array containing ``cos(values)``.

Optional main/runtime behavior:
    This file is loaded by the Functions menu and is not intended to be run
    directly.
"""

import numpy as np

DISPLAY_NAME = "cos(x)"
DEFAULT_LABEL = "cos(x)"


def transform(values):
    """transform(values) -> numpy.ndarray

    Calculate cosine for each input value.

    Parameters:
        values (Sequence[float]): One-dimensional selected table column in
            radians.

    Returns:
        numpy.ndarray: Cosine values.
    """
    return np.cos(values)
