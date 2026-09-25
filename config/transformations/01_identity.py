"""Identity transform for PhysPlot.

Input data structure:
    ``values`` is a one-dimensional NumPy-compatible sequence containing the
    selected table column.

Return type:
    Returns the input values unchanged as an array-like sequence.

Optional main/runtime behavior:
    This file is loaded by the Functions menu and is not intended to be run
    directly.
"""

DISPLAY_NAME = "x"
DEFAULT_LABEL = "x"


def transform(values):
    """transform(values) -> Sequence[float]

    Return values unchanged.

    Parameters:
        values (Sequence[float]): One-dimensional selected table column.

    Returns:
        Sequence[float]: The original values.
    """
    return values
