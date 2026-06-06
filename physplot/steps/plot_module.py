"""Workflow step for modular plot generation."""

from __future__ import annotations

from .base import WorkflowStep

MODULE_ID = "physplot.steps.plot_module"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-06-05-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"


class PlotModuleStep(WorkflowStep):
    def __init__(self, plotter_id, plot_type=None, config=None):
        self.plotter_id = plotter_id
        self.plot_type = plot_type
        self.config = config or {}

    def apply(self, physplot, allow_column_number_fallback: bool = False):
        return physplot.plot_with_module(
            self.plotter_id,
            self.plot_type,
            record=False,
            **self.config,
        )

    def to_code(self) -> str:
        return (
            "PlotModuleStep(\n"
            f"    plotter_id={self.plotter_id!r},\n"
            f"    plot_type={self.plot_type!r},\n"
            f"    config={self.config!r},\n"
            ")"
        )
