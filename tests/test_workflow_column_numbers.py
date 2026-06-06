import pandas as pd

from physplot import PhysPlot
from physplot.workflow import load_workflow


def test_workflow_records_exports_and_imports_column_numbers(tmp_path):
    pp = PhysPlot()
    pp.load(pd.DataFrame({"Time": [1, 2], "Voltage": [2.0, 4.0], "Current": [1.0, 2.0]}), loader="dataframe")
    pp.transform(2, "normalize_max", output="Voltage_norm")
    pp.calculate("C2 / C3", output="Resistance")

    assert pp.workflow[0].input_column_number == 2
    workflow_path = tmp_path / "workflow.py"
    pp.export_workflow(workflow_path)
    text = workflow_path.read_text()
    assert "input_column_number=2" in text
    assert "source_column_numbers=[2, 3]" in text

    pp2 = PhysPlot()
    pp2.load(pd.DataFrame({"Time": [1, 2], "Voltage": [3.0, 6.0], "Current": [1.0, 2.0]}), loader="dataframe")
    pp2.run_workflow(load_workflow(workflow_path))
    assert "Voltage_norm" in pp2.dataset.dataframe
    assert "Resistance" in pp2.dataset.dataframe
