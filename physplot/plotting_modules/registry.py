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
from .user_modules import load_plot_type_presets, load_user_plotters

MODULE_ID = "physplot.plotting_modules.registry"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-06-05-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"


class PlotterRegistry:
    def __init__(self):
        self.plotters = {}
        self.plot_type_presets = {}

    def register(self, plotter: BasePlotter):
        self.plotters[plotter.plotter_id] = plotter
        return plotter

    def register_plot_type_preset(self, preset: dict):
        """Register a named plot-type preset for one plotter module."""
        key = (str(preset["plotter_id"]), str(preset["plot_type"]))
        self.plot_type_presets[key] = preset
        return preset

    def resolve_plot_type(self, plotter_id, plot_type, config=None):
        """Return ``(base_plot_type, merged_config)`` for a plot type name.

        Preset plot types from ``config/plot_types`` map onto a base plot type
        of the plotter and merge their stored configuration underneath any
        explicit configuration passed by the caller.
        """
        merged = dict(config or {})
        preset = self.plot_type_presets.get((str(plotter_id), str(plot_type))) if plot_type is not None else None
        if preset is None:
            return plot_type, merged
        merged = {**dict(preset.get("config") or {}), **merged}
        return preset.get("base_plot_type") or plot_type, merged

    def get(self, plotter_id):
        try:
            return self.plotters[plotter_id]
        except KeyError as exc:
            raise ValueError(f"Unknown plotter module '{plotter_id}'.") from exc

    def list_plotters(self, dataset=None):
        return [plotter for plotter in self.plotters.values() if plotter.can_plot(dataset)]

    def list_plot_types(self, plotter_id, dataset=None):
        plot_types = list(self.get(plotter_id).get_plot_types(dataset))
        for (preset_plotter_id, plot_type) in self.plot_type_presets:
            if preset_plotter_id == plotter_id and plot_type not in plot_types:
                plot_types.append(plot_type)
        return plot_types

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
        for plotter in load_user_plotters():
            registry.register(plotter)
        for preset in load_plot_type_presets():
            if preset["plotter_id"] in registry.plotters:
                registry.register_plot_type_preset(preset)
        return registry
