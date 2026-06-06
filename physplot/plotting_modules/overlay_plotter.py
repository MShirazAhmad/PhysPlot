"""Overlay plotting module."""

from __future__ import annotations

import matplotlib.pyplot as plt

from .base import BasePlotter
from .utils import group_column, numeric_series, role_column

MODULE_ID = "physplot.plotting_modules.overlay_plotter"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-06-05-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"


class OverlayPlotter(BasePlotter):
    plotter_id = "overlay"
    name = "Overlay Plotter"
    category = "General"
    supported_dataset_types = ("*",)
    supported_plot_types = ("overlay_by_group", "overlay_by_dataset")

    def plot(self, dataset, plot_type=None, config=None):
        plot_type = plot_type or "overlay_by_group"
        if plot_type not in self.supported_plot_types:
            raise ValueError(f"Overlay Plotter does not support plot type '{plot_type}'.")
        x_col = role_column(dataset, "X")
        y_col = role_column(dataset, "Y")
        group_col = group_column(dataset)
        fig, ax = plt.subplots()
        if group_col:
            for name, group in dataset.dataframe.groupby(group_col, sort=False):
                ax.plot(
                    numeric_series(_GroupDataset(group, dataset), x_col),
                    numeric_series(_GroupDataset(group, dataset), y_col),
                    marker="o",
                    linestyle="-",
                    label=str(name),
                )
            ax.legend()
        else:
            ax.plot(numeric_series(dataset, x_col), numeric_series(dataset, y_col), marker="o", linestyle="-")
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.set_title(f"{y_col} vs {x_col}")
        fig.tight_layout()
        return fig


class _GroupDataset:
    def __init__(self, dataframe, source):
        self.dataframe = dataframe
        self.column_roles = source.column_roles
        self.column_metadata = source.column_metadata
        self.metadata = source.metadata
