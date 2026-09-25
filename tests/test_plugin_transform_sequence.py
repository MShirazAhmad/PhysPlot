import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from physplot import PhysPlot
from physplot.bulk import run_folder
from physplot.core.transformations import discover_plugin_transforms, get_transform
from physplot.steps import LoadDataStep, TransformColumnStep
from physplot.workflow import load_workflow_source

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def user_dir(monkeypatch, tmp_path):
    """Isolate from the real Documents/PhysPlot so only bundled plugins load."""
    root = tmp_path / "PhysPlotUser"
    monkeypatch.setenv("PHYSPLOT_USER_DIR", str(root))
    return root


def test_sequence_with_plugin_transform_runs_headlessly(user_dir):
    pp = PhysPlot()
    pp.load(pd.DataFrame({"Time": [0, 1, 2], "Voltage": [1.0, 2.0, 3.0]}), loader="dataframe")

    pp.run_workflow(
        [TransformColumnStep("Voltage", "02_square", "Voltage_sq", params={"multiplier": 2.0, "offset": 0.5})]
    )

    assert pp.dataset.dataframe["Voltage_sq"].tolist() == [2.5, 8.5, 18.5]
    assert pp.dataset.column_metadata["Voltage_sq"]["transformation"]["function"] == "02_square"


def test_plugin_transform_resolves_by_display_name(user_dir):
    pp = PhysPlot()
    pp.load(pd.DataFrame({"Angle": [0.0, np.pi / 2]}), loader="dataframe")

    values = pp.transform("Angle", "sin(x)", output="Angle_sin")

    assert values.tolist() == pytest.approx([0.0, 1.0])


def test_user_plugin_overrides_bundled_plugin_on_replay(user_dir):
    folder = user_dir / "config" / "transformations"
    folder.mkdir(parents=True)
    (folder / "02_square.py").write_text(
        "DISPLAY_NAME = 'x^2 (edited)'\n"
        "def transform(values):\n"
        "    return values * 10\n",
        encoding="utf-8",
    )
    (folder / "custom_shift.py").write_text(
        "DISPLAY_NAME = 'Shift by 100'\n"
        "def transform(values, amount=100):\n"
        "    return values + amount\n",
        encoding="utf-8",
    )

    pp = PhysPlot()
    pp.load(pd.DataFrame({"Signal": [1.0, 2.0]}), loader="dataframe")
    pp.transform("Signal", "02_square", output="Scaled")
    pp.transform("Signal", "Shift by 100", output="Shifted", amount=5)

    assert pp.dataset.dataframe["Scaled"].tolist() == [10.0, 20.0]
    assert pp.dataset.dataframe["Shifted"].tolist() == [6.0, 7.0]
    names = {entry["name"]: entry for entry in discover_plugin_transforms()}
    assert names["02_square"]["path"] == folder / "02_square.py"
    assert names["custom_shift"]["display_name"] == "Shift by 100"


def test_registered_transforms_win_and_unknown_names_fail(user_dir):
    folder = user_dir / "config" / "transformations"
    folder.mkdir(parents=True)
    (folder / "log.py").write_text("def transform(values):\n    return values * 0\n", encoding="utf-8")

    assert get_transform("log").__name__ == "log"
    assert "log" not in {entry["name"] for entry in discover_plugin_transforms()}
    with pytest.raises(ValueError, match="Unknown transformation 'not_a_plugin'"):
        get_transform("not_a_plugin")


def test_plugin_must_return_one_value_per_row(user_dir):
    folder = user_dir / "config" / "transformations"
    folder.mkdir(parents=True)
    (folder / "bad_length.py").write_text("def transform(values):\n    return values[:1]\n", encoding="utf-8")
    pp = PhysPlot()
    pp.load(pd.DataFrame({"Signal": [1.0, 2.0]}), loader="dataframe")

    with pytest.raises(ValueError, match="returned 1 values for a column of 2 rows"):
        pp.transform("Signal", "bad_length", output="Out")


def test_plugin_step_code_round_trips(user_dir):
    step = TransformColumnStep("Voltage", "09_sin", "Voltage_sin", params={"multiplier": 1.0, "offset": 0.0})
    source = f"from physplot.steps import TransformColumnStep\nWORKFLOW_STEPS = [{step.to_code()}]\n"

    (loaded,) = load_workflow_source(source)

    assert loaded.function_name == "09_sin"
    assert loaded.params == {"multiplier": 1.0, "offset": 0.0}


def test_bulk_run_applies_plugin_transform(user_dir, tmp_path):
    input_folder = tmp_path / "input"
    input_folder.mkdir()
    pd.DataFrame({"Time": [1, 2], "Signal": [2.0, 3.0]}).to_csv(input_folder / "a.csv", index=False)
    pd.DataFrame({"Time": [1, 2], "Signal": [4.0, 5.0]}).to_csv(input_folder / "b.csv", index=False)

    outputs = run_folder(
        [TransformColumnStep("Signal", "02_square", "Signal_sq", params={"multiplier": 1.0, "offset": 1.0})],
        input_folder,
        tmp_path / "output",
    )

    results = {path.name: pd.read_csv(path / "data.csv")["Signal_sq"].tolist() for path in outputs}
    assert results == {"a": [5.0, 10.0], "b": [17.0, 26.0]}


def test_exported_plugin_sequence_runs_in_fresh_process(user_dir, tmp_path):
    data_path = tmp_path / "data.csv"
    data_path.write_text("Time,Voltage\n1,2\n2,3\n", encoding="utf-8")
    pp = PhysPlot()
    pp.workflow = [
        LoadDataStep(path=str(data_path), loader="csv", dataset_name="data"),
        TransformColumnStep("Voltage", "03_cube", "Voltage_cube", params={"multiplier": 1.0, "offset": 0.0}),
    ]
    sequence_path = pp.export_workflow(tmp_path / "Sequence.py")
    output_dir = tmp_path / "run"

    subprocess.run(
        [sys.executable, "-c", "import runpy, sys; runpy.run_path(sys.argv[1])['run'](output_dir=sys.argv[2])",
         str(sequence_path), str(output_dir)],
        cwd=REPO_ROOT,
        env={**os.environ, "PHYSPLOT_USER_DIR": str(user_dir), "MPLBACKEND": "Agg"},
        check=True,
    )

    assert pd.read_csv(output_dir / "data.csv")["Voltage_cube"].tolist() == [8.0, 27.0]
