"""Histogram plotting module."""

from __future__ import annotations

import matplotlib.pyplot as plt

from .base import BasePlotter
from .utils import first_numeric_column, numeric_series, role_column

MODULE_ID = "physplot.plotting_modules.histogram_plotter"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-06-05-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"


class HistogramPlotter(BasePlotter):
    plotter_id = "histogram"
    name = "Histogram Plotter"
    category = "General"
    supported_dataset_types = ("*",)
    supported_plot_types = ("histogram", "density_histogram")

    def plot(self, dataset, plot_type=None, config=None):
        plot_type = plot_type or "histogram"
        if plot_type not in self.supported_plot_types:
            raise ValueError(f"Histogram Plotter does not support plot type '{plot_type}'.")
        column = role_column(dataset, "Y", required=False) or role_column(dataset, "X", required=False)
        column = column or first_numeric_column(dataset)
        values = numeric_series(dataset, column).dropna()
        fig, ax = plt.subplots()
        ax.hist(values, bins=20, density=plot_type == "density_histogram", edgecolor="#334155", alpha=0.75)
        ax.set_xlabel(column)
        ax.set_ylabel("Density" if plot_type == "density_histogram" else "Count")
        ax.set_title(column)
        fig.tight_layout()
        return fig
