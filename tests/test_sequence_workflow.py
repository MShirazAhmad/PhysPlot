import subprocess
import sys

import pandas as pd

from physplot import PhysPlot
from physplot.steps import (
    DeleteColumnsStep,
    DeleteRowsStep,
    LoadDataStep,
    RenameColumnStep,
    SetCellValueStep,
    SetRoleStep,
    TransformColumnStep,
)
from physplot.workflow import load_workflow


def test_sequence_export_load_and_headless_run(tmp_path):
    data_path = tmp_path / "data.csv"
    data_path.write_text("Time,Voltage\n1,2\n2,4\n", encoding="utf-8")
    output_dir = tmp_path / "out"

    pp = PhysPlot()
    pp.workflow.append(LoadDataStep(path=str(data_path), loader="csv", dataset_name="data"))
    pp.workflow.append(SetRoleStep({"x": "Time", "y": "Voltage"}))
    pp.workflow.append(TransformColumnStep("Voltage", "multiply", "Voltage_mV", params={"factor": 1000}))
    workflow_path = tmp_path / "sequence.py"
    pp.save_workflow(workflow_path)
    assert pp.workflow_script() == workflow_path.read_text(encoding="utf-8")

    steps = load_workflow(workflow_path)
    assert len(steps) == 3

    subprocess.run(
        [sys.executable, str(workflow_path), "--output", str(output_dir)],
        check=True,
        cwd=tmp_path,
    )

    exported = pd.read_csv(output_dir / "data.csv")
    assert "Voltage_mV" in exported.columns


def test_sequence_replays_visible_blank_column_rename_and_edit(tmp_path):
    data_path = tmp_path / "data.csv"
    data_path.write_text("Time,Voltage\n1,2\n2,4\n", encoding="utf-8")

    pp = PhysPlot()
    pp.workflow.extend(
        [
            LoadDataStep(path=str(data_path), loader="csv", dataset_name="data"),
            RenameColumnStep("Column 5", "Comment", old_column_number=5),
            SetCellValueStep(1, "Comment", "kept from GUI", column_number=5),
        ]
    )
    workflow_path = tmp_path / "sequence.py"
    pp.save_workflow(workflow_path)

    runner = PhysPlot()
    runner.run_workflow(load_workflow(workflow_path), allow_column_number_fallback=True)

    assert list(runner.dataset.dataframe.columns)[:5] == ["Time", "Voltage", "Column 3", "Column 4", "Comment"]
    assert runner.dataset.dataframe.loc[0, "Comment"] == "kept from GUI"


def test_sequence_replays_manual_row_and_column_deletes(tmp_path):
    data_path = tmp_path / "data.csv"
    data_path.write_text("Time,Voltage,Error\n1,2,0.1\n2,4,0.2\n3,6,0.3\n", encoding="utf-8")

    pp = PhysPlot()
    pp.workflow.extend(
        [
            LoadDataStep(path=str(data_path), loader="csv", dataset_name="data"),
            DeleteRowsStep([2]),
            DeleteColumnsStep(["Column 5"], column_numbers=[5]),
            SetCellValueStep(1, "Column 4", "after delete", column_number=4),
        ]
    )
    workflow_path = tmp_path / "sequence.py"
    pp.save_workflow(workflow_path)

    runner = PhysPlot()
    runner.run_workflow(load_workflow(workflow_path), allow_column_number_fallback=True)

    assert runner.dataset.dataframe["Time"].tolist() == [1, 3]
    assert "Column 5" not in runner.dataset.dataframe.columns
    assert runner.dataset.dataframe.loc[0, "Column 4"] == "after delete"
