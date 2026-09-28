"""Workflow step for formula-derived columns."""

from __future__ import annotations

from .base import WorkflowStep
from .fields import field

MODULE_ID = "physplot.steps.calculate_column"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-05-30-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"



class CalculateColumnStep(WorkflowStep):
    display_name = "Calculate Column"

    def __init__(
        self,
        formula,
        output,
        formula_original=None,
        source_columns=None,
        source_column_numbers=None,
        output_column_number=None,
        enabled=True,
    ):
        self.formula = formula
        self.output = output
        self.formula_original = formula_original or formula
        self.source_columns = source_columns or []
        self.source_column_numbers = source_column_numbers or []
        self.output_column_number = output_column_number
        self.enabled = enabled

    def apply(self, physplot, allow_column_number_fallback: bool = False):
        return physplot.calculate(self.formula_original, self.output, record=False)

    @classmethod
    def template(cls, columns=()):
        return cls(formula="col1 * 2", output="Calculated")

    def _describe_fields(self) -> dict:
        return {
            "formula_original": field(
                self.formula_original,
                "str",
                label="Formula",
                help="Use column names or col1, col2, ... for example col2 / col1.",
            ),
            "output": field(self.output, "str", label="Output column"),
        }

    def _set_field(self, name: str, value) -> None:
        super()._set_field(name, value)
        if name == "formula_original" and value != self.formula:
            # The stored normalized form and source columns describe the old
            # formula; they are refreshed the next time the step records.
            self.formula = value
            self.source_columns = []
            self.source_column_numbers = []

    def to_code(self) -> str:
        return self._format_code(
            [
                ("formula", self.formula),
                ("output", self.output),
                ("formula_original", self.formula_original),
                ("source_columns", self.source_columns),
                ("source_column_numbers", self.source_column_numbers),
                ("output_column_number", self.output_column_number),
            ]
        )
