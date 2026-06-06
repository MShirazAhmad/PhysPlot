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


def test_transform_coerces_numeric_spreadsheet_strings_with_blanks():
    pp = PhysPlot()
    pp.load(
        pd.DataFrame(
            {
                "Time": ["1", "2", "", ""],
                "Voltage": ["2", "4", "", ""],
                "Note": ["A", "B", "", ""],
            }
        ),
        loader="dataframe",
    )

    result = pp.transform("Time", "multiply", output="Time_scaled", factor=1.5)

    assert result.dropna().tolist() == [1.5, 3.0]
    assert pd.isna(result.iloc[2])
