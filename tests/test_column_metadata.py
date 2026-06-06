import pandas as pd

from physplot import PhysPlot
from physplot.core.dataset import Dataset


def test_dataset_metadata_and_describe_columns():
    ds = Dataset("test", pd.DataFrame({"Time": [1.0], "Voltage": [2.0]}))
    assert set(ds.column_metadata) == {"Time", "Voltage"}
    assert ds.column_metadata["Time"]["column_number"] == 1
    assert ds.column_metadata["Voltage"]["dtype"] == "float64"
    assert ds.column_roles["Time"] == "Ignore"
    described = ds.describe_columns()
    assert list(described.columns) == [
        "column_number",
        "column_name",
        "role",
        "dtype",
        "unit",
        "derived",
        "suggested_role",
        "source_label",
    ]


def test_derived_column_gets_new_column_number():
    pp = PhysPlot()
    pp.load(pd.DataFrame({"Time": [1, 2], "Voltage": [2, 4]}), loader="dataframe")
    pp.transform(2, "normalize_max", output="Voltage_norm")
    assert pp.get_column_metadata("Voltage_norm")["column_number"] == 3
    assert pp.get_column_metadata("Column 3")["derived"] is True
