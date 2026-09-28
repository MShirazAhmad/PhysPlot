"""UV-Vis absorbance: remove a constant baseline, normalize to the strongest peak, plot.

Input: a CSV with the columns "Wavelength (nm)" and "Absorbance".
Load the data with Import Data (GUI), Run Sequence (a folder), or
physplot run-workflow ... --input <file>.
"""

from physplot.steps import PlotModuleStep, SetRoleStep, TransformColumnStep

WORKFLOW_STEPS = [
    SetRoleStep(roles={"x": "Wavelength (nm)", "y": "Absorbance"}),
    TransformColumnStep(
        input_column="Absorbance",
        input_column_number=2,
        function_name="subtract",
        output="Absorbance_corr",
        params={"value": 0.02},
    ),
    TransformColumnStep(
        input_column="Absorbance_corr",
        input_column_number=3,
        function_name="normalize_max",
        output="Absorbance_norm",
        params={},
    ),
    SetRoleStep(roles={"y": "Absorbance_norm"}),
    PlotModuleStep(plotter_id="line", plot_type="line", config={}),
]
