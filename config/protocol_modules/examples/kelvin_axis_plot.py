"""Protocol module: plot resistance against temperature in kelvin.

For tables with the columns "Temperature_C" (column 1) and "Resistance_ohm".
Appends three steps to the current protocol.
"""

from physplot.steps import PlotModuleStep, SetRoleStep, TransformColumnStep

DISPLAY_NAME = "Resistance vs Temperature (K)"
DESCRIPTION = "Add 273.15 to Temperature_C as a new column Temperature_K, plot Resistance_ohm against it."

WORKFLOW_STEPS = [
    TransformColumnStep(
        input_column="Temperature_C",
        input_column_number=1,
        function_name="add",
        output="Temperature_K",
        params={"value": 273.15},
    ),
    SetRoleStep(roles={"x": "Temperature_K", "y": "Resistance_ohm"}),
    PlotModuleStep(plotter_id="basic", plot_type="scatter_line", config={}),
]
