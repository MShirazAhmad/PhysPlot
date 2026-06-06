"""Example PhysPlot workflow with column-number metadata."""

from physplot.steps import CalculateColumnStep, TransformColumnStep

WORKFLOW_STEPS = [
    TransformColumnStep(
        input_column="Voltage",
        input_column_number=2,
        function_name="normalize_max",
        output="Voltage_norm",
        output_column_number=5,
        params={},
    ),
    CalculateColumnStep(
        formula="Voltage / Time",
        output="Voltage_per_Time",
        formula_original="C2 / C1",
        source_columns=["Voltage", "Time"],
        source_column_numbers=[2, 1],
        output_column_number=6,
    ),
]
