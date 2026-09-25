"""Base-10 logarithm transform for PhysPlot.

Input data structure:
    ``values`` is a one-dimensional NumPy-compatible sequence containing the
    selected table column.

Return type:
    Returns a NumPy array containing ``log10(values)``.

Optional main/runtime behavior:
    This file is loaded by the Functions menu and is not intended to be run
    directly.
"""

import numpy as np

DISPLAY_NAME = "log10(x)"
DEFAULT_LABEL = "log10(x)"


def transform(values):
    """transform(values) -> numpy.ndarray

    Calculate the base-10 logarithm of each input value.

    Parameters:
        values (Sequence[float]): One-dimensional selected table column.

    Returns:
        numpy.ndarray: Base-10 logarithm values.
    """
    return np.log10(values)
