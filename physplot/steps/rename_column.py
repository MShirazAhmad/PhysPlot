"""Workflow step for manual column renames."""

from __future__ import annotations

from .base import WorkflowStep
from .fields import field

MODULE_ID = "physplot.steps.rename_column"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-06-05-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"



class RenameColumnStep(WorkflowStep):
    display_name = "Rename Column"

    def __init__(self, old_column, new_column, old_column_number=None, enabled=True):
        self.old_column = old_column
        self.new_column = new_column
        self.old_column_number = old_column_number
        self.enabled = enabled

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

    @classmethod
    def template(cls, columns=()):
        columns = list(columns) or ["Column 1"]
        return cls(columns[0], f"{columns[0]}_renamed", 1)

    def _describe_fields(self) -> dict:
        return {
            "old_column": field(self.old_column, "column", label="Column", number_field="old_column_number"),
            "new_column": field(self.new_column, "str", label="New name"),
            "old_column_number": field(self.old_column_number, "int", label="Column number fallback", optional=True),
        }

    def to_code(self) -> str:
        return self._format_code(
            [
                ("old_column", self.old_column),
                ("new_column", self.new_column),
                ("old_column_number", self.old_column_number),
            ]
        )
