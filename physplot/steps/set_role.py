"""Workflow step for column role assignment."""

from __future__ import annotations

from .base import WorkflowStep
from .fields import field

MODULE_ID = "physplot.steps.set_role"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-06-05-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"



ROLE_FIELDS = (
    ("x", "X column"),
    ("y", "Y column"),
    ("xerr", "X error column"),
    ("yerr", "Y error column"),
    ("group", "Group column"),
    ("label", "Label column"),
    ("y2", "Y2 column"),
    ("z", "Z column"),
    ("u", "U column"),
    ("v", "V column"),
    ("w", "W column"),
)


class SetRoleStep(WorkflowStep):
    """Assign table column roles in a sequence.

    ``roles`` uses the public ``PhysPlot.set_roles`` keyword form, for example
    ``{"x": "Time", "y": "Voltage", "yerr": "Error"}``. In the step editor
    each role is its own column field; leaving one blank removes that role
    from the step.
    """

    display_name = "Set Roles"

    def __init__(self, roles=None, enabled=True):
        self.roles = roles or {}
        self.enabled = enabled

    def apply(self, physplot, allow_column_number_fallback: bool = False):
        return physplot.set_roles(record=False, **self.roles)

    @classmethod
    def template(cls, columns=()):
        columns = list(columns)
        roles = {}
        if columns:
            roles["x"] = columns[0]
        if len(columns) > 1:
            roles["y"] = columns[1]
        return cls(roles)

    def _describe_fields(self) -> dict:
        fields = {
            key: field(self.roles.get(key), "column", label=label, optional=True)
            for key, label in ROLE_FIELDS
        }
        for key, value in self.roles.items():
            if key not in fields:
                fields[key] = field(value, "column", label=f"{key} column", optional=True)
        return fields

    def _set_field(self, name: str, value) -> None:
        if name == "enabled":
            super()._set_field(name, value)
            return
        roles = dict(self.roles)
        if value is None:
            roles.pop(name, None)
        else:
            roles[name] = value
        self.roles = roles

    def to_code(self) -> str:
        return self._format_code([("roles", self.roles)])
