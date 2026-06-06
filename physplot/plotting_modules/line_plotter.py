"""Line plotting module."""

from __future__ import annotations

from .basic_plotter import BasicPlotter

MODULE_ID = "physplot.plotting_modules.line_plotter"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-06-05-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"


class LinePlotter(BasicPlotter):
    plotter_id = "line"
    name = "Line Plotter"
    supported_plot_types = ("line",)
