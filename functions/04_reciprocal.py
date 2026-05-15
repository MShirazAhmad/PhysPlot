"""Reciprocal transform for PhysPlot.

Input data structure:
    ``values`` is a one-dimensional NumPy-compatible sequence containing the
    selected table column.

Return type:
    Returns an array-like sequence containing ``1 / values``.

Optional main/runtime behavior:
    This file is loaded by the Functions menu and is not intended to be run
    directly.
"""

DISPLAY_NAME = "1/x"
DEFAULT_LABEL = "1/x"


def transform(values):
    """transform(values) -> Sequence[float]

    Calculate the reciprocal of each input value.

    Parameters:
        values (Sequence[float]): One-dimensional selected table column.

    Returns:
        Sequence[float]: Values transformed as ``1 / values``.
    """
    return 1 / values
