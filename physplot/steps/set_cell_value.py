"""Workflow step for manual spreadsheet cell edits."""

from __future__ import annotations

from .base import WorkflowStep

MODULE_ID = "physplot.steps.set_cell_value"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-06-05-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"


class SetCellValueStep(WorkflowStep):
    def __init__(self, row_index, column, value, column_number=None):
        self.row_index = row_index
        self.column = column
        self.value = value
        self.column_number = column_number

    def apply(self, physplot, allow_column_number_fallback: bool = False):
        reference = self.column
        dataset = physplot.dataset
        if (
            dataset is not None
            and self.column not in dataset.dataframe.columns
            and allow_column_number_fallback
            and self.column_number is not None
        ):
            reference = self.column_number
        return physplot.set_cell_value(self.row_index, reference, self.value)

    def to_code(self) -> str:
        return (
            "SetCellValueStep(\n"
            f"    row_index={self.row_index!r},\n"
            f"    column={self.column!r},\n"
            f"    value={self.value!r},\n"
            f"    column_number={self.column_number!r},\n"
            ")"
        )
