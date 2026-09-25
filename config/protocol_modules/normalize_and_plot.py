"""Reusable protocol fragment: normalize the Y column and plot it against X.

Insert from *Protocol > Insert Protocol Module* or load headlessly with
``physplot.workflow.load_workflow``. Column numbers are used as a fallback so
the fragment works on any dataset where column 1 is X and column 2 is Y.

Only backend transformations (``physplot.core.transformations``) replay in
sequences; Simple Mode plugin functions from ``config/transformations`` are
not recorded as replayable steps yet.
"""

from __future__ import annotations

from physplot.steps import PlotModuleStep, SetRoleStep, TransformColumnStep

DISPLAY_NAME = "Normalize Y and Plot"
DESCRIPTION = "Scale column 2 to a maximum of 1 in a new column, assign roles, and draw a basic scatter plot."

WORKFLOW_STEPS = [
    TransformColumnStep(
        input_column="Column 2",
        input_column_number=2,
        function_name="normalize_max",
        output="Column 2_norm",
        output_column_number=3,
        params={},
    ),
    SetRoleStep(roles={"x": "Column 1", "y": "Column 2_norm"}),
    PlotModuleStep(plotter_id="basic", plot_type="scatter", config={}),
]
