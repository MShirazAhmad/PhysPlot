import pandas as pd

from physplot import PhysPlot


def test_transform_provenance_by_name_and_number():
    pp = PhysPlot()
    pp.load(pd.DataFrame({"Time": [1, 2], "Voltage": [2.0, 4.0]}), loader="dataframe")
    pp.transform("Voltage", "normalize_max", output="Voltage_norm")
    meta = pp.get_column_metadata("Voltage_norm")
    assert meta["source_columns"] == ["Voltage"]
    assert meta["source_column_numbers"] == [2]
    assert meta["column_number"] == 3
    assert meta["derived"] is True

    pp.transform(2, "multiply", output="Voltage_mV", factor=1000)
    meta = pp.get_column_metadata("Voltage_mV")
    assert meta["transformation"] == {"function": "multiply", "params": {"factor": 1000}}
    assert meta["source_column_numbers"] == [2]
    assert meta["column_number"] == 4
