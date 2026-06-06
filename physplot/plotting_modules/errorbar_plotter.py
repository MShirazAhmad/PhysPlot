"""Error-bar plotting module."""

from __future__ import annotations

import matplotlib.pyplot as plt

from .base import BasePlotter
from .utils import numeric_series, role_column

MODULE_ID = "physplot.plotting_modules.errorbar_plotter"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-06-05-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"


class ErrorBarPlotter(BasePlotter):
    plotter_id = "errorbar"
    name = "Error Bar Plotter"
    category = "General"
    supported_dataset_types = ("*",)
    supported_plot_types = ("x_y_errorbar", "y_errorbar")

    def plot(self, dataset, plot_type=None, config=None):
        plot_type = plot_type or "y_errorbar"
        if plot_type not in self.supported_plot_types:
            raise ValueError(f"Error Bar Plotter does not support plot type '{plot_type}'.")
        x_col = role_column(dataset, "X")
        y_col = role_column(dataset, "Y")
        xerr_col = role_column(dataset, "X Error", required=False)
        yerr_col = role_column(dataset, "Y Error", required=False)
        xerr = numeric_series(dataset, xerr_col) if xerr_col and plot_type == "x_y_errorbar" else None
        yerr = numeric_series(dataset, yerr_col) if yerr_col else None
        fig, ax = plt.subplots()
        ax.errorbar(
            numeric_series(dataset, x_col),
            numeric_series(dataset, y_col),
            xerr=xerr,
            yerr=yerr,
            marker="o",
            linestyle="-",
            capsize=3,
        )
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.set_title(f"{y_col} vs {x_col}")
        fig.tight_layout()
        return fig
