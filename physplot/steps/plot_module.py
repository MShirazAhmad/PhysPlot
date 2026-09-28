"""Workflow step for modular plot generation."""

from __future__ import annotations

from .base import WorkflowStep
from .fields import field, safe_choices

MODULE_ID = "physplot.steps.plot_module"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-06-05-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"



class PlotModuleStep(WorkflowStep):
    display_name = "Generate Plot"

    def __init__(self, plotter_id, plot_type=None, config=None, enabled=True):
        self.plotter_id = plotter_id
        self.plot_type = plot_type
        self.config = config or {}
        self.enabled = enabled

    def apply(self, physplot, allow_column_number_fallback: bool = False):
        return physplot.plot_with_module(
            self.plotter_id,
            self.plot_type,
            record=False,
            **self.config,
        )

    @classmethod
    def template(cls, columns=()):
        return cls("basic", "scatter", {})

    def _describe_fields(self) -> dict:
        from physplot.plotting_modules import PlotterRegistry

        registry = safe_choices(lambda: [PlotterRegistry.default()])
        plotters = list(registry[0].plotters) if registry else []
        plot_types = safe_choices(lambda: registry[0].list_plot_types(self.plotter_id)) if registry else []
        return {
            "plotter_id": field(self.plotter_id, "choice", label="Plotter module", choices=plotters, editable=True),
            "plot_type": field(self.plot_type, "choice", label="Plot type", choices=plot_types, editable=True, optional=True),
            "config": field(
                self.config,
                "literal",
                label="Configuration",
                python_type=dict,
                help="Plotter options, for example {'lsq_fit': {'enabled': True, 'expression': 'a*x + b'}}.",
            ),
        }

    def to_code(self) -> str:
        return self._format_code([("plotter_id", self.plotter_id), ("plot_type", self.plot_type), ("config", self.config)])
