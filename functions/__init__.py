"""Editable function plugins for PhysPlot.

Input data structure:
    Function plugins receive one selected table column as a one-dimensional
    NumPy-compatible sequence.

Return type:
    Function plugins return an array-like sequence with the same length as the
    input column.

Optional main/runtime behavior:
    Package marker for dynamically discovered transformation plugins; not
    executable by itself.
"""

# Each module in this package should expose:
# - DISPLAY_NAME: label shown in the UI
# - DEFAULT_LABEL: default curve label
# - transform(values): callable applied to the x-data before scaling
