import pandas as pd
from matplotlib.figure import Figure

from physplot import PhysPlot
from physplot.workflow import load_workflow


def test_plot_module_step_exports_imports_and_runs(tmp_path):
    pp = PhysPlot()
    pp.load(pd.DataFrame({"Time": [0, 1, 2], "Voltage": [1.0, 2.0, 3.0]}), loader="dataframe")
    pp.set_roles(x="Time", y="Voltage")
    pp.plot_with_module("basic", "line")

    path = tmp_path / "workflow.py"
    pp.save_workflow(path)
    steps = load_workflow(path)

    runner = PhysPlot()
    runner.load(pd.DataFrame({"Time": [0, 1, 2], "Voltage": [1.0, 2.0, 3.0]}), loader="dataframe")
    runner.set_roles(x="Time", y="Voltage")
    runner.run_workflow(steps)

    assert isinstance(runner.last_figure, Figure)
