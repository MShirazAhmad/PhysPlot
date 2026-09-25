"""Square transform for PhysPlot.

Input data structure:
    ``values`` is a one-dimensional NumPy-compatible sequence containing the
    selected table column.

Return type:
    Returns a NumPy array with each value squared.

Optional main/runtime behavior:
    This file is loaded by the Functions menu and is not intended to be run
    directly.
"""

import numpy as np

DISPLAY_NAME = "x^2"
DEFAULT_LABEL = "x^2"


def transform(values):
    """transform(values) -> numpy.ndarray

    Square each input value.

    Parameters:
        values (Sequence[float]): One-dimensional selected table column.

    Returns:
        numpy.ndarray: Squared values.
    """
    return np.power(values, 2)
