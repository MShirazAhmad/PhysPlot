"""Workflow step for manual spreadsheet column deletion."""

from __future__ import annotations

from .base import WorkflowStep
from .fields import field

MODULE_ID = "physplot.steps.delete_columns"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-06-05-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"



class DeleteColumnsStep(WorkflowStep):
    display_name = "Delete Columns"

    def __init__(self, columns, column_numbers=None, enabled=True):
        self.columns = list(columns or [])
        self.column_numbers = list(column_numbers or [])
        self.enabled = enabled

    def apply(self, physplot, allow_column_number_fallback: bool = False):
        references = list(self.columns)
        dataset = physplot.dataset
        if allow_column_number_fallback and dataset is not None:
            references = [
                number if column not in dataset.dataframe.columns and index < len(self.column_numbers) else column
                for index, (column, number) in enumerate(zip(self.columns, self.column_numbers))
            ]
            if len(self.columns) > len(references):
                references.extend(self.columns[len(references) :])
        return physplot.delete_columns(references)

    @classmethod
    def template(cls, columns=()):
        columns = list(columns)
        if not columns:
            return cls(["Column 1"], [1])
        return cls([columns[-1]], [len(columns)])

    def _describe_fields(self) -> dict:
        return {
            "columns": field(self.columns, "literal", label="Columns", python_type=list, help="For example ['Time', 'Error']."),
            "column_numbers": field(
                self.column_numbers,
                "literal",
                label="Column numbers",
                python_type=list,
                help="Used when a named column is missing and column-number fallback is on.",
            ),
        }

    def to_code(self) -> str:
        return self._format_code([("columns", self.columns), ("column_numbers", self.column_numbers)])
