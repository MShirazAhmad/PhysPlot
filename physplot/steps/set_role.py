"""Workflow step for column role assignment."""

from __future__ import annotations

from .base import WorkflowStep

MODULE_ID = "physplot.steps.set_role"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-06-05-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"


class SetRoleStep(WorkflowStep):
    """Assign table column roles in a sequence.

    ``roles`` uses the public ``PhysPlot.set_roles`` keyword form, for example
    ``{"x": "Time", "y": "Voltage", "yerr": "Error"}``.
    """

    def __init__(self, roles=None):
        self.roles = roles or {}

    def apply(self, physplot, allow_column_number_fallback: bool = False):
        return physplot.set_roles(**self.roles)

    def to_code(self) -> str:
        return "SetRoleStep(\n" f"    roles={self.roles!r},\n" ")"
