"""Workflow step for manual spreadsheet column deletion."""

from __future__ import annotations

from .base import WorkflowStep

MODULE_ID = "physplot.steps.delete_columns"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-06-05-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"


class DeleteColumnsStep(WorkflowStep):
    def __init__(self, columns, column_numbers=None):
        self.columns = list(columns or [])
        self.column_numbers = list(column_numbers or [])

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

    def to_code(self) -> str:
        return (
            "DeleteColumnsStep(\n"
            f"    columns={self.columns!r},\n"
            f"    column_numbers={self.column_numbers!r},\n"
            ")"
        )
