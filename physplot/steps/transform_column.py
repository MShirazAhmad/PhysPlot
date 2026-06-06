"""Workflow step for transformation-derived columns."""

from __future__ import annotations

import logging

from .base import WorkflowStep

MODULE_ID = "physplot.steps.transform_column"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-05-30-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"

LOGGER = logging.getLogger(__name__)


class TransformColumnStep(WorkflowStep):
    def __init__(
        self,
        input_column,
        function_name,
        output,
        params=None,
        input_column_number=None,
        output_column_number=None,
    ):
        self.input_column = input_column
        self.function_name = function_name
        self.output = output
        self.params = params or {}
        self.input_column_number = input_column_number
        self.output_column_number = output_column_number

    def apply(self, physplot, allow_column_number_fallback: bool = False):
        reference = self.input_column
        dataset = physplot.dataset
        if dataset is not None and self.input_column not in dataset.dataframe.columns:
            if allow_column_number_fallback and self.input_column_number is not None:
                source = dataset.source_path.name if dataset.source_path is not None else dataset.name
                LOGGER.warning(
                    "Column '%s' not found in %s; used column number %s instead.",
                    self.input_column,
                    source,
                    self.input_column_number,
                )
                reference = self.input_column_number
            else:
                raise ValueError(f"Column '{self.input_column}' not found.")
        return physplot.transform(reference, self.function_name, output=self.output, record=False, **self.params)

    def to_code(self) -> str:
        return (
            "TransformColumnStep(\n"
            f"    input_column={self.input_column!r},\n"
            f"    input_column_number={self.input_column_number!r},\n"
            f"    function_name={self.function_name!r},\n"
            f"    output={self.output!r},\n"
            f"    output_column_number={self.output_column_number!r},\n"
            f"    params={self.params!r},\n"
            ")"
        )
