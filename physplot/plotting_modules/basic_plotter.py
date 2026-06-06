"""Basic X/Y plotting module."""

from __future__ import annotations

import matplotlib.pyplot as plt

from .base import BasePlotter
from .utils import numeric_series, role_column

MODULE_ID = "physplot.plotting_modules.basic_plotter"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-06-05-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"


class BasicPlotter(BasePlotter):
    plotter_id = "basic"
    name = "Basic Plotter"
    category = "General"
    supported_dataset_types = ("*",)
    supported_plot_types = ("scatter", "line", "scatter_line")

    def plot(self, dataset, plot_type=None, config=None):
        plot_type = plot_type or "scatter"
        if plot_type not in self.supported_plot_types:
            raise ValueError(f"Basic Plotter does not support plot type '{plot_type}'.")
        x_col = role_column(dataset, "X")
        y_col = role_column(dataset, "Y")
        x = numeric_series(dataset, x_col)
        y = numeric_series(dataset, y_col)
        fig, ax = plt.subplots()
        if plot_type == "scatter":
            ax.scatter(x, y)
        elif plot_type == "line":
            ax.plot(x, y, linestyle="-")
        else:
            ax.plot(x, y, marker="o", linestyle="-")
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.set_title(f"{y_col} vs {x_col}")
        fig.tight_layout()
        return fig
