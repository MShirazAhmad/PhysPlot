"""Small reusable helpers for PhysPlot.

Input data structure:
    Helpers accept Qt table widgets, numeric row/column indexes, curve-fit
    option arrays, coefficient arrays, and custom label strings.

Return type:
    ``table_item_float`` returns a float. ``fit_label`` returns the legend
    label string for a fitted curve.

Optional main/runtime behavior:
    Imported by the application at startup; not intended to be run directly.
"""


def table_item_float(table, row, column):
    """table_item_float(table, row, column) -> float

    Return a numeric value from a QTableWidget cell.

    Parameters:
        table (QTableWidget): Table containing user-entered numeric data.
        row (int): Zero-based row index.
        column (int): Zero-based column index.

    Returns:
        float: Parsed cell value. Blank, missing, or invalid cells return
        ``0.0``.
    """
    item = table.item(row, column)
    if item is None:
        return 0.0
    try:
        return float(item.text())
    except (TypeError, ValueError):
        return 0.0


def fit_label(fit_options, index, coefficients, custom_label):
    """fit_label(fit_options, index, coefficients, custom_label) -> str

    Build the legend label for a fitted curve.

    :param fit_options: Boolean-like matrix where each row stores fit settings.
        Column 1 means label off, column 2 means equation label, and column 3
        means custom label.
    :type fit_options: numpy.ndarray
    :param index: Row index in ``fit_options`` for the active fit.
    :type index: int
    :param coefficients: Polynomial coefficients or optimized callable-fit
        parameters.
    :type coefficients: Sequence[float]
    :param custom_label: User-provided label shown when custom labeling is
        enabled.
    :type custom_label: str
    :returns: Empty string for no label, ``custom_label`` for custom mode, or a
        compact coefficient summary for equation mode.
    :rtype: str
    """
    if fit_options[index, 1]:
        return ""
    if fit_options[index, 3]:
        return custom_label
    if fit_options[index, 2]:
        labels = "abcdefghijklmnopqrstuvwxyz"
        parts = [
            f"{labels[position]}={value:2.2g}"
            for position, value in enumerate(coefficients)
        ]
        return "fit: " + ", ".join(parts)
    return ""
