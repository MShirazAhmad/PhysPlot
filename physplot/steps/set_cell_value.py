"""Workflow step for manual spreadsheet cell edits."""

from __future__ import annotations

from .base import WorkflowStep
from .fields import field

MODULE_ID = "physplot.steps.set_cell_value"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-06-05-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"



class SetCellValueStep(WorkflowStep):
    display_name = "Edit Cell"

    def __init__(self, row_index, column, value, column_number=None, enabled=True):
        self.row_index = row_index
        self.column = column
        self.value = value
        self.column_number = column_number
        self.enabled = enabled

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

    @classmethod
    def template(cls, columns=()):
        columns = list(columns) or ["Column 1"]
        return cls(1, columns[0], "", 1)

    def _describe_fields(self) -> dict:
        return {
            "row_index": field(self.row_index, "int", label="Row", help="Row number as shown in the table, starting at 1."),
            "column": field(self.column, "column", label="Column", number_field="column_number"),
            "value": field(self.value, "value", label="Value", help="Numbers are stored as numbers; quote text such as '5' to keep it text."),
            "column_number": field(self.column_number, "int", label="Column number fallback", optional=True),
        }

    def to_code(self) -> str:
        return self._format_code(
            [
                ("row_index", self.row_index),
                ("column", self.column),
                ("value", self.value),
                ("column_number", self.column_number),
            ]
        )
