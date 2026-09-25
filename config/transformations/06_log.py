"""Natural logarithm transform for PhysPlot.

Input data structure:
    ``values`` is a one-dimensional NumPy-compatible sequence containing the
    selected table column.

Return type:
    Returns a NumPy array containing the natural logarithm of each value.

Optional main/runtime behavior:
    This file is loaded by the Functions menu and is not intended to be run
    directly.
"""

import numpy as np

DISPLAY_NAME = "log(x)"
DEFAULT_LABEL = "log(x)"


def transform(values):
    """transform(values) -> numpy.ndarray

    Calculate the natural logarithm of each input value.

    Parameters:
        values (Sequence[float]): One-dimensional selected table column.

    Returns:
        numpy.ndarray: Natural logarithm values.
    """
    return np.log(values)
