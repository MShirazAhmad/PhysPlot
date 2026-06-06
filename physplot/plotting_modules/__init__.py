"""Modular plotting interface for PhysPlot."""

from .base import BasePlotter
from .registry import PlotterRegistry

__all__ = ["BasePlotter", "PlotterRegistry"]
