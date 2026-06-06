"""Workflow step for manual column renames."""

from __future__ import annotations

from .base import WorkflowStep

MODULE_ID = "physplot.steps.rename_column"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-06-05-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"


class RenameColumnStep(WorkflowStep):
    def __init__(self, old_column, new_column, old_column_number=None):
        self.old_column = old_column
        self.new_column = new_column
        self.old_column_number = old_column_number

    def apply(self, physplot, allow_column_number_fallback: bool = False):
        reference = self.old_column
        dataset = physplot.dataset
        if (
            dataset is not None
            and self.old_column not in dataset.dataframe.columns
            and allow_column_number_fallback
            and self.old_column_number is not None
        ):
            reference = self.old_column_number
        return physplot.rename_column(reference, self.new_column)

    def to_code(self) -> str:
        return (
            "RenameColumnStep(\n"
            f"    old_column={self.old_column!r},\n"
            f"    new_column={self.new_column!r},\n"
            f"    old_column_number={self.old_column_number!r},\n"
            ")"
        )
