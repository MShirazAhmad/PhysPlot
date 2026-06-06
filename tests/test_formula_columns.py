import pandas as pd
import pytest

from physplot import PhysPlot


def make_pp():
    pp = PhysPlot()
    pp.load(pd.DataFrame({"Time": [1.0, 2.0], "Voltage": [4.0, 8.0], "Current": [2.0, 4.0]}), loader="dataframe")
    return pp


def test_formula_name_and_column_number_forms():
    for formula in ["Voltage / Current", "C2 / C1", "col2 / col1", "#2 / #1"]:
        pp = make_pp()
        pp.calculate(formula, output="Result")
        expected = [4.0, 4.0] if "C1" in formula or "col1" in formula or "#1" in formula else [2.0, 2.0]
        assert list(pp.dataset.dataframe["Result"]) == expected
        meta = pp.get_column_metadata("Result")
        assert meta["formula_original"] == formula
        assert meta["source_columns"]
        assert meta["source_column_numbers"]


def test_formula_records_sources_for_named_formula():
    pp = make_pp()
    pp.calculate("Voltage / Current", output="Resistance")
    meta = pp.get_column_metadata("Resistance")
    assert meta["source_columns"] == ["Voltage", "Current"]
    assert meta["source_column_numbers"] == [2, 3]
    assert meta["formula"] == "Voltage / Current"


def test_unsafe_formula_rejected():
    pp = make_pp()
    with pytest.raises(ValueError, match="unsafe|unsupported"):
        pp.calculate("__import__('os').system('echo nope')", output="Bad")
