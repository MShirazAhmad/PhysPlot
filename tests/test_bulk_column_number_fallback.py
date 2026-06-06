import logging

import pandas as pd
import pytest

from physplot.bulk import run_folder
from physplot.steps import TransformColumnStep


def write_batch(tmp_path):
    input_folder = tmp_path / "input"
    input_folder.mkdir()
    pd.DataFrame({"Time": [1, 2], "Signal": [2.0, 4.0]}).to_csv(input_folder / "sample_001.csv", index=False)
    pd.DataFrame({"Time": [1, 2], "VoltageRenamed": [3.0, 6.0]}).to_csv(input_folder / "sample_002.csv", index=False)
    return input_folder


def test_bulk_default_does_not_fallback_silently(tmp_path):
    steps = [TransformColumnStep("Signal", "normalize_max", "Signal_norm", input_column_number=2)]
    with pytest.raises(ValueError, match="Signal"):
        run_folder(steps, write_batch(tmp_path), tmp_path / "output")


def test_bulk_fallback_can_use_same_column_number_and_logs(tmp_path, caplog):
    steps = [TransformColumnStep("Signal", "normalize_max", "Signal_norm", input_column_number=2)]
    caplog.set_level(logging.WARNING)
    outputs = run_folder(
        steps,
        write_batch(tmp_path),
        tmp_path / "output",
        allow_column_number_fallback=True,
    )
    assert len(outputs) == 2
    assert "used column number 2" in caplog.text


def test_bulk_out_of_range_fallback_fails_safely(tmp_path):
    steps = [TransformColumnStep("Signal", "normalize_max", "Signal_norm", input_column_number=20)]
    with pytest.raises(ValueError, match="out of range"):
        run_folder(
            steps,
            write_batch(tmp_path),
            tmp_path / "output",
            allow_column_number_fallback=True,
        )
