import pandas as pd

from physplot import PhysPlot


def test_rename_column_preserves_role_and_metadata():
    pp = PhysPlot()
    pp.load(pd.DataFrame({"Column 1": [1, 2], "Column 2": [3, 4]}), loader="dataframe")
    pp.set_roles(x="Column 1", y="Column 2")

    pp.rename_column("Column 1", "Time")

    assert "Time" in pp.dataset.dataframe.columns
    assert "Column 1" not in pp.dataset.dataframe.columns
    assert pp.dataset.column_roles["Time"] == "X"
    assert pp.get_column_metadata("Time")["column_number"] == 1
