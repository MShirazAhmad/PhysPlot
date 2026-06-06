"""Registry for modular plotters."""

from __future__ import annotations

from .base import BasePlotter
from .basic_plotter import BasicPlotter
from .errorbar_plotter import ErrorBarPlotter
from .histogram_plotter import HistogramPlotter
from .line_plotter import LinePlotter
from .nanoindentation_plotter import NanoindentationPlotter
from .oliver_pharr_plotter import OliverPharrPlotter
from .overlay_plotter import OverlayPlotter
from .scatter_plotter import ScatterPlotter
from .subplot_grid_plotter import SubplotGridPlotter

MODULE_ID = "physplot.plotting_modules.registry"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-06-05-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"


class PlotterRegistry:
    def __init__(self):
        self.plotters = {}

    def register(self, plotter: BasePlotter):
        self.plotters[plotter.plotter_id] = plotter
        return plotter

    def get(self, plotter_id):
        try:
            return self.plotters[plotter_id]
        except KeyError as exc:
            raise ValueError(f"Unknown plotter module '{plotter_id}'.") from exc

    def list_plotters(self, dataset=None):
        return [plotter for plotter in self.plotters.values() if plotter.can_plot(dataset)]

    def list_plot_types(self, plotter_id, dataset=None):
        return self.get(plotter_id).get_plot_types(dataset)

    @classmethod
    def default(cls):
        registry = cls()
        for plotter in (
            BasicPlotter(),
            HistogramPlotter(),
            ScatterPlotter(),
            LinePlotter(),
            ErrorBarPlotter(),
            OverlayPlotter(),
            SubplotGridPlotter(),
            NanoindentationPlotter(),
            OliverPharrPlotter(),
        ):
            registry.register(plotter)
        return registry
