"""Scatter plotting module."""

from __future__ import annotations

from .basic_plotter import BasicPlotter

MODULE_ID = "physplot.plotting_modules.scatter_plotter"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-06-05-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"


class ScatterPlotter(BasicPlotter):
    plotter_id = "scatter"
    name = "Scatter Plotter"
    supported_plot_types = ("scatter",)
