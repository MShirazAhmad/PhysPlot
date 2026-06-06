"""Workflow step for manual spreadsheet row deletion."""

from __future__ import annotations

from .base import WorkflowStep

MODULE_ID = "physplot.steps.delete_rows"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-06-05-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"


class DeleteRowsStep(WorkflowStep):
    def __init__(self, row_indices):
        self.row_indices = list(row_indices or [])

    def apply(self, physplot, allow_column_number_fallback: bool = False):
        return physplot.delete_rows(self.row_indices)

    def to_code(self) -> str:
        return "DeleteRowsStep(\n" f"    row_indices={self.row_indices!r},\n" ")"
