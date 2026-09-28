"""Workflow step for transformation-derived columns."""

from __future__ import annotations

import logging

from .base import WorkflowStep
from .fields import field, safe_choices

MODULE_ID = "physplot.steps.transform_column"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-05-30-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"

LOGGER = logging.getLogger(__name__)



class TransformColumnStep(WorkflowStep):
    display_name = "Transform Column"

    def __init__(
        self,
        input_column,
        function_name,
        output,
        params=None,
        input_column_number=None,
        output_column_number=None,
        enabled=True,
    ):
        self.input_column = input_column
        self.function_name = function_name
        self.output = output
        self.params = params or {}
        self.input_column_number = input_column_number
        self.output_column_number = output_column_number
        self.enabled = enabled

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

    @classmethod
    def template(cls, columns=()):
        columns = list(columns) or ["Column 1"]
        return cls(columns[0], "multiply", f"{columns[0]}_multiply", {"factor": 1}, 1)

    def _describe_fields(self) -> dict:
        from physplot.core.transformations import discover_plugin_transforms, list_transforms

        functions = safe_choices(list_transforms)
        functions += [entry["name"] for entry in safe_choices(discover_plugin_transforms) if entry["name"] not in functions]
        return {
            "input_column": field(self.input_column, "column", label="Input column", number_field="input_column_number"),
            "function_name": field(
                self.function_name,
                "choice",
                label="Function",
                choices=functions,
                editable=True,
                help="A built-in transformation or a config/transformations file name.",
            ),
            "output": field(self.output, "str", label="Output column"),
            "params": field(
                self.params,
                "literal",
                label="Parameters",
                python_type=dict,
                help="Keyword arguments, for example {'factor': 1000}.",
            ),
            "input_column_number": field(self.input_column_number, "int", label="Input column number fallback", optional=True),
            "output_column_number": field(self.output_column_number, "int", label="Output column number", optional=True),
        }

    def to_code(self) -> str:
        return self._format_code(
            [
                ("input_column", self.input_column),
                ("input_column_number", self.input_column_number),
                ("function_name", self.function_name),
                ("output", self.output),
                ("output_column_number", self.output_column_number),
                ("params", self.params),
            ]
        )
