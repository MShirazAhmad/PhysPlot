"""Workflow step for manual spreadsheet row deletion."""

from __future__ import annotations

from .base import WorkflowStep
from .fields import field

MODULE_ID = "physplot.steps.delete_rows"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-06-05-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"



class DeleteRowsStep(WorkflowStep):
    display_name = "Delete Rows"

    def __init__(self, row_indices, enabled=True):
        self.row_indices = list(row_indices or [])
        self.enabled = enabled

    def apply(self, physplot, allow_column_number_fallback: bool = False):
        return physplot.delete_rows(self.row_indices)

    @classmethod
    def template(cls, columns=()):
        return cls([1])

    def _describe_fields(self) -> dict:
        return {
            "row_indices": field(
                self.row_indices,
                "literal",
                label="Rows",
                python_type=list,
                help="Row numbers as shown in the table, starting at 1. For example [1, 2].",
            ),
        }

    def to_code(self) -> str:
        return self._format_code([("row_indices", self.row_indices)])
