"""Subplot-grid plotting module."""

from __future__ import annotations

import math

import matplotlib.pyplot as plt

from .base import BasePlotter
from .utils import group_column, numeric_series, role_column

MODULE_ID = "physplot.plotting_modules.subplot_grid_plotter"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-06-05-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"


class SubplotGridPlotter(BasePlotter):
    plotter_id = "subplot_grid"
    name = "Subplot Grid Plotter"
    category = "General"
    supported_dataset_types = ("*",)
    supported_plot_types = ("subplots_by_group", "subplots_by_dataset")

    def plot(self, dataset, plot_type=None, config=None):
        plot_type = plot_type or "subplots_by_group"
        if plot_type not in self.supported_plot_types:
            raise ValueError(f"Subplot Grid Plotter does not support plot type '{plot_type}'.")
        x_col = role_column(dataset, "X")
        y_col = role_column(dataset, "Y")
        group_col = group_column(dataset)
        groups = list(dataset.dataframe.groupby(group_col, sort=False)) if group_col else [(dataset.name, dataset.dataframe)]
        cols = min(3, max(1, len(groups)))
        rows = math.ceil(len(groups) / cols)
        fig, axes = plt.subplots(rows, cols, squeeze=False, figsize=(4 * cols, 3 * rows))
        for ax in axes.ravel()[len(groups) :]:
            ax.set_visible(False)
        for ax, (name, group) in zip(axes.ravel(), groups):
            proxy = _GroupDataset(group, dataset)
            ax.plot(numeric_series(proxy, x_col), numeric_series(proxy, y_col), marker="o", linestyle="-")
            ax.set_title(str(name))
            ax.set_xlabel(x_col)
            ax.set_ylabel(y_col)
        fig.tight_layout()
        return fig


class _GroupDataset:
    def __init__(self, dataframe, source):
        self.dataframe = dataframe
        self.column_roles = source.column_roles
        self.column_metadata = source.column_metadata
        self.metadata = source.metadata
