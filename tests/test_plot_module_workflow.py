import pandas as pd
import pytest
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


def test_plot_module_step_replays_lsq_fit_overlay(tmp_path):
    pp = PhysPlot()
    pp.load(pd.DataFrame({"Time": [0, 1, 2, 3], "Voltage": [1.0, 3.0, 5.0, 7.0]}), loader="dataframe")
    pp.set_roles(x="Time", y="Voltage")
    pp.plot_with_module(
        "basic",
        "scatter",
        lsq_fit={
            "enabled": True,
            "expression": "a*x + b",
            "parameters": "a,b",
            "initial": "1,0",
            "label": "Linear LSQ",
            "line_style": ":",
            "line_width": 3.0,
            "show_legend": True,
        },
    )

    path = tmp_path / "workflow.py"
    pp.save_workflow(path)
    steps = load_workflow(path)

    runner = PhysPlot()
    runner.load(pd.DataFrame({"Time": [0, 1, 2, 3], "Voltage": [1.0, 3.0, 5.0, 7.0]}), loader="dataframe")
    runner.set_roles(x="Time", y="Voltage")
    runner.run_workflow(steps)

    assert isinstance(runner.last_figure, Figure)
    assert len(runner.last_figure.axes[0].lines) == 1
    line = runner.last_figure.axes[0].lines[0]
    assert line.get_label() == "Linear LSQ"
    assert line.get_linestyle() == ":"
    assert line.get_linewidth() == pytest.approx(3.0)
    assert runner.fit_result["method"] == "lsq"
    assert runner.fit_result["parameters"]["a"] == pytest.approx(2.0)
    assert runner.fit_result["parameters"]["b"] == pytest.approx(1.0)

    runner.plot_with_module("basic", "scatter")
    assert runner.fit_result is None
