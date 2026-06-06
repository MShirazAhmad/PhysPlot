import pandas as pd
import pytest

from physplot.core.column_resolver import resolve_column
from physplot.core.dataset import Dataset


def dataset(columns=("Time", "Voltage", "Error", "Group")):
    return Dataset("test", pd.DataFrame([[1, 2, 0.1, "A"]], columns=list(columns)))


def test_column_resolver_forms():
    ds = dataset()
    assert resolve_column(ds, "Voltage") == "Voltage"
    assert resolve_column(ds, 2) == "Voltage"
    assert resolve_column(ds, "2") == "Voltage"
    assert resolve_column(ds, "Column 2") == "Voltage"
    assert resolve_column(ds, "Col2") == "Voltage"
    assert resolve_column(ds, "C2") == "Voltage"
    assert resolve_column(ds, "#2") == "Voltage"


def test_actual_numeric_column_name_wins():
    ds = Dataset("numeric", pd.DataFrame([[10, 20]], columns=["A", "2"]))
    assert resolve_column(ds, "2") == "2"
    assert resolve_column(ds, 2) == "2"


def test_column_resolver_errors_are_clear():
    ds = dataset()
    with pytest.raises(ValueError, match="out of range"):
        resolve_column(ds, 99)
    with pytest.raises(ValueError, match="Unknown column"):
        resolve_column(ds, "missing")
    with pytest.raises(ValueError, match="None"):
        resolve_column(ds, None)
