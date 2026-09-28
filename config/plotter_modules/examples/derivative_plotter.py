"""Derivative Plotter: normalized curve and dY/dX of the Y column against X.

Headless replay: PlotModuleStep(plotter_id="derivative", plot_type="derivative", config={})
Optional config keys: title, x_label, y_label, grid, marker, figsize,
normalize_by ("max" or "range"), smooth_points (moving average before dY/dX).
"""

import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PLOTTER_ID = "derivative"
NAME = "Derivative Plotter"
CATEGORY = "User"
PLOT_TYPES = ["normalized", "derivative"]


def _role_column(dataset, role):
    """Return the name of the column that has this role, or None."""
    for column, column_role in dataset.column_roles.items():
        if column_role == role and column in dataset.dataframe.columns:
            return column
    return None


def _name_and_unit(column):
    """Split 'Current (mA)' into ('Current', 'mA'); no unit gives None."""
    match = re.match(r"^\s*(.*?)\s*[\(\[]([^\)\]]+)[\)\]]\s*$", str(column))
    return (match.group(1) or str(column), match.group(2)) if match else (str(column), None)


def plot(dataset, plot_type=None, config=None):
    config = dict(config or {})
    plot_type = plot_type or PLOT_TYPES[0]
    if plot_type not in PLOT_TYPES:
        raise ValueError(f"Derivative Plotter has no plot type '{plot_type}'. Use one of: {', '.join(PLOT_TYPES)}.")

    x_col = _role_column(dataset, "X")
    y_col = _role_column(dataset, "Y")
    if x_col is None or y_col is None:
        raise ValueError("Derivative Plotter needs one column with role X and one with role Y.")

    frame = dataset.dataframe
    data = pd.DataFrame({"x": pd.to_numeric(frame[x_col], errors="coerce"),
                         "y": pd.to_numeric(frame[y_col], errors="coerce")}).dropna()
    # Sort by X and average repeated X values, so dY/dX is defined everywhere.
    data = data.groupby("x", as_index=False)["y"].mean()
    if len(data) < 3:
        raise ValueError(f"Derivative Plotter needs at least 3 rows with numbers in '{x_col}' and '{y_col}'.")
    x = data["x"].to_numpy(dtype=float)
    y = data["y"].to_numpy(dtype=float)
    x_name, x_unit = _name_and_unit(x_col)
    y_name, y_unit = _name_and_unit(y_col)

    if plot_type == "normalized":
        if config.get("normalize_by", "max") == "range":
            span = y.max() - y.min()
            if span == 0:
                raise ValueError(f"Cannot normalize '{y_col}': all values are equal.")
            values = (y - y.min()) / span
        else:
            peak = np.max(np.abs(y))
            if peak == 0:
                raise ValueError(f"Cannot normalize '{y_col}': all values are zero.")
            values = y / peak
        default_y_label = f"{y_name} (normalized)"
    else:
        window = int(config.get("smooth_points", 1))
        if window > 1:
            y = pd.Series(y).rolling(window, center=True, min_periods=1).mean().to_numpy()
        values = np.gradient(y, x)
        unit = f"{y_unit or 1}/{x_unit}" if x_unit else y_unit
        default_y_label = f"d({y_name})/d({x_name})" + (f" ({unit})" if unit else "")

    fig, ax = plt.subplots(figsize=tuple(config.get("figsize", (6.0, 4.0))))
    ax.plot(x, values, marker=config.get("marker", "o"), markersize=3, linestyle="-")
    if plot_type == "derivative":
        ax.axhline(0.0, color="0.6", linewidth=0.8)
    ax.set_xlabel(config.get("x_label", x_col))
    ax.set_ylabel(config.get("y_label", default_y_label))
    ax.set_title(config.get("title", str(dataset.name)))
    if config.get("grid", True):
        ax.grid(True, linestyle=":", alpha=0.6)
    fig.tight_layout()
    return fig
