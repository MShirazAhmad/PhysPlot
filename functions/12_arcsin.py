"""Arcsin transform for PhysPlot.

Input data structure:
    ``values`` is a one-dimensional NumPy-compatible sequence containing the
    selected table column. Values should generally be within ``[-1, 1]``.

Return type:
    Returns a NumPy array containing ``arcsin(values)`` in radians.

Optional main/runtime behavior:
    This file is loaded by the Functions menu and is not intended to be run
    directly.
"""

import numpy as np

DISPLAY_NAME = "arcsin(x)"
DEFAULT_LABEL = "arcsin(x)"


def transform(values):
    """transform(values) -> numpy.ndarray

    Calculate inverse sine for each input value.

    Parameters:
        values (Sequence[float]): One-dimensional selected table column,
            normally within ``[-1, 1]``.

    Returns:
        numpy.ndarray: Inverse sine values in radians.
    """
    return np.arcsin(values)
