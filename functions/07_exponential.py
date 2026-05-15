"""Exponential transform for PhysPlot.

Input data structure:
    ``values`` is a one-dimensional NumPy-compatible sequence containing the
    selected table column.

Return type:
    Returns a NumPy array containing ``e`` raised to each input value.

Optional main/runtime behavior:
    This file is loaded by the Functions menu and is not intended to be run
    directly.
"""

import numpy as np

DISPLAY_NAME = "e^x"
DEFAULT_LABEL = "e^x"


def transform(values):
    """transform(values) -> numpy.ndarray

    Calculate the exponential of each input value.

    Parameters:
        values (Sequence[float]): One-dimensional selected table column.

    Returns:
        numpy.ndarray: Values transformed as ``exp(values)``.
    """
    return np.exp(values)
