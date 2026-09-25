"""Modular plotting interface for PhysPlot."""

from .base import BasePlotter
from .registry import PlotterRegistry
from .user_modules import CallablePlotter, load_plot_type_presets, load_user_plotters

__all__ = ["BasePlotter", "CallablePlotter", "PlotterRegistry", "load_plot_type_presets", "load_user_plotters"]
