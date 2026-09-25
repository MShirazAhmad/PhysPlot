"""Example user plotter module.

Copy this file, rename it, and change ``PLOTTER_ID``/``NAME``. The plotter is
picked up automatically from ``config/plotter_modules`` on the next start or
after *File > Reload Config Modules*.

Headless replay::

    PlotModuleStep(plotter_id="example_xy", plot_type="xy_markers", config={})
"""

from __future__ import annotations

import matplotlib.pyplot as plt

PLOTTER_ID = "example_xy"
NAME = "Example XY Plotter"
CATEGORY = "User"
PLOT_TYPES = ["xy_markers", "xy_line"]


def plot(dataset, plot_type=None, config=None):
    """Return a Matplotlib figure for the current X/Y role columns."""
    config = dict(config or {})
    roles = {role.lower(): column for column, role in dataset.column_roles.items()}
    x_column = roles.get("x") or roles.get("x-axis")
    y_column = roles.get("y") or roles.get("y-axis")
    if x_column is None or y_column is None:
        raise ValueError("Assign one X and one Y column before using the Example XY Plotter.")

    frame = dataset.dataframe
    figure, axes = plt.subplots(figsize=config.get("figsize", (6, 4)))
    style = "o" if plot_type == "xy_markers" else "-"
    axes.plot(frame[x_column], frame[y_column], style, label=config.get("label", y_column))
    axes.set_xlabel(config.get("x_label", x_column))
    axes.set_ylabel(config.get("y_label", y_column))
    if config.get("grid", True):
        axes.grid(True, linestyle=":", alpha=0.6)
    axes.legend()
    figure.tight_layout()
    return figure
