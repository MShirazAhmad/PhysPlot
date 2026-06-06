"""Workflow step for formula-derived columns."""

from __future__ import annotations

from .base import WorkflowStep

MODULE_ID = "physplot.steps.calculate_column"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-05-30-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"


class CalculateColumnStep(WorkflowStep):
    def __init__(
        self,
        formula,
        output,
        formula_original=None,
        source_columns=None,
        source_column_numbers=None,
        output_column_number=None,
    ):
        self.formula = formula
        self.output = output
        self.formula_original = formula_original or formula
        self.source_columns = source_columns or []
        self.source_column_numbers = source_column_numbers or []
        self.output_column_number = output_column_number

    def apply(self, physplot, allow_column_number_fallback: bool = False):
        return physplot.calculate(self.formula_original, self.output, record=False)

    def to_code(self) -> str:
        return (
            "CalculateColumnStep(\n"
            f"    formula={self.formula!r},\n"
            f"    output={self.output!r},\n"
            f"    formula_original={self.formula_original!r},\n"
            f"    source_columns={self.source_columns!r},\n"
            f"    source_column_numbers={self.source_column_numbers!r},\n"
            f"    output_column_number={self.output_column_number!r},\n"
            ")"
        )
