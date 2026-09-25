"""Loading real-world instrument exports (synthetic copies of their layouts)."""

import runpy

import pandas as pd
import pytest

from physplot import PhysPlot
from physplot.bulk import run_folder
from physplot.steps import LoadDataStep, TransformColumnStep


def load(path):
    return PhysPlot().load(path)


def test_panalytical_xrd_csv_skips_measurement_conditions(tmp_path):
    path = tmp_path / "scan.csv"
    path.write_bytes(
        b"[Measurement conditions]\r\n"
        b"Sample identification,\r\n"
        b'Comment - 1,"Configuration=Reflection-transmission spinner, Owner=User-1"\r\n'
        b'Comment - 2,"Goniometer=Theta/Theta; Minimum step size 2Theta:0.0001"\r\n'
        b"[Scan points]\r\n"
        b"Angle,Intensity\r\n15.0065,159.0\r\n15.0197,162.0\r\n15.0328,136.0\r\n"
    )

    dataset = load(path)

    assert list(dataset.dataframe.columns) == ["Angle", "Intensity"]
    assert dataset.dataframe["Intensity"].tolist() == [159.0, 162.0, 136.0]
    assert dataset.metadata["header_lines"][0] == "[Measurement conditions]"


def test_edax_eds_csv_with_metadata_and_trailing_commas(tmp_path):
    path = tmp_path / "Spectrum_1.csv"
    path.write_text(
        "Path     :, C:\\EDAX\\map.spd,\t\t,Date\n"
        "Matrix:     :, 3 x 2, ,KV     :, 15, ,WD(mm)    :, 10.76,\n"
        "Dwell(us)    :, 50, ,Frames    :, 32,\t\t\n"
        "\n"
        "X/Y    , 1,2,3,\n"
        "1,4,5,6,\n"
        "2,7,8,9,\n",
        encoding="utf-8",
    )

    frame = load(path).dataframe

    assert list(frame.columns) == ["X/Y", "1", "2", "3"]
    assert frame["3"].tolist() == [6, 9]


def test_tab_separated_csv_with_row_labels(tmp_path):
    path = tmp_path / "peaks.csv"
    path.write_text(
        "\ty0\ty0\txc\txc\n"
        "\tValue\tStandard Error\tValue\tStandard Error\n"
        "Peak1(Subtracted_Data Y1)\t2.675\t0.042\t35.911\t9.1E-5\n"
        "Peak2(Subtracted_Data Y1)\t2.675\t0.042\t41.711\t1.4E-4\n",
        encoding="utf-8",
    )

    frame = load(path).dataframe

    assert list(frame.columns)[1:] == ["Value", "Standard Error", "Value.1", "Standard Error.1"]
    assert frame["Value.1"].tolist() == [35.911, 41.711]


def test_phi_xps_spectrum_stored_as_rows_is_transposed(tmp_path):
    energies = [1200 - 0.8 * i for i in range(30)]
    counts = [14000 + i for i in range(30)]
    path = tmp_path / "scan1.csv"
    path.write_text(
        "1\nno area description\nSu1s\n1,1\n"
        + ",".join(f"{value:.2f}" for value in energies) + "\n"
        + ",".join(f"{value:.4f}" for value in counts) + "\n",
        encoding="utf-8",
    )

    frame = load(path).dataframe

    assert frame.shape == (30, 2)
    assert frame["Column 1"].iloc[0] == 1200.0
    assert frame["Column 2"].iloc[-1] == 14029.0


def test_quoted_eds_quant_table(tmp_path):
    path = tmp_path / "Spot 1.csv"
    path.write_text(
        '\ufeff"eZAF Smart Quant Results",""\r\n"kV","20"\r\n"",""\r\n'
        '"Element","Weight %","Atomic %","Error %"\r\n'
        '"C  K","7.74","45.51","12.49"\r\n"Nb L","13.26","10.08","9.13"\r\n"Mo L","12.51","9.21","9.72"\r\n',
        encoding="utf-8",
    )

    frame = load(path).dataframe

    assert list(frame.columns) == ["Element", "Weight %", "Atomic %", "Error %"]
    assert frame["Weight %"].tolist() == [7.74, 13.26, 12.51]
    assert frame["Element"].tolist() == ["C  K", "Nb L", "Mo L"]


def test_binary_and_empty_files_get_clear_errors(tmp_path):
    binary = tmp_path / "afm.dat"
    binary.write_bytes(b"\x00\x01\xab\xcd" * 64)
    empty = tmp_path / "peaks.txt"
    empty.write_text("")

    with pytest.raises(ValueError, match="binary file, not a text table"):
        load(binary)
    with pytest.raises(ValueError, match="is empty"):
        load(empty)


def test_tsv_files_load(tmp_path):
    path = tmp_path / "scan.tsv"
    path.write_text("Angle\tIntensity\n10.0\t5\n10.1\t7\n", encoding="utf-8")

    assert load(path).dataframe["Intensity"].tolist() == [5, 7]


def test_plain_csv_with_text_column_is_unchanged(tmp_path):
    path = tmp_path / "plain.csv"
    path.write_text("Time,Voltage,Group\n1,2,A\n2,4,B\n", encoding="utf-8")

    frame = load(path).dataframe

    assert list(frame.columns) == ["Time", "Voltage", "Group"]
    assert frame["Group"].tolist() == ["A", "B"]


PLUGIN_LOADER = '''
import numpy as np
title = "Two-number loader"
COLUMN_NAMES = ["Wavelength", "Intensity"]
def load_data(file_path):
    rows = [line.split("|") for line in open(file_path) if "|" in line]
    return np.array(rows, dtype=float)
'''


def plugin_sequence(tmp_path):
    loader = tmp_path / "pipe_loader.py"
    loader.write_text(PLUGIN_LOADER, encoding="utf-8")
    folder = tmp_path / "spectra"
    folder.mkdir()
    (folder / "a.HRF").write_text("header\n400|1\n401|2\n", encoding="utf-8")
    (folder / "b.HRF").write_text("header\n400|3\n401|4\n", encoding="utf-8")
    (folder / "notes.csv").write_text("x,y\n1,2\n", encoding="utf-8")
    steps = [
        LoadDataStep(path=str(folder / "a.HRF"), loader="dataframe", loader_plugin=str(loader)),
        TransformColumnStep("Intensity", "multiply", "Scaled", params={"factor": 10}),
    ]
    return folder, steps


def test_bulk_run_reuses_the_sequence_loader_plugin(tmp_path):
    folder, steps = plugin_sequence(tmp_path)

    outputs = run_folder(steps, folder, tmp_path / "out")

    assert sorted(path.name for path in outputs) == ["a", "b"]
    assert pd.read_csv(tmp_path / "out" / "b" / "data.csv")["Scaled"].tolist() == [30.0, 40.0]


def test_exported_run_reuses_the_sequence_loader_plugin(tmp_path):
    folder, steps = plugin_sequence(tmp_path)
    pp = PhysPlot()
    pp.workflow = steps
    sequence = pp.export_workflow(tmp_path / "Sequence.py")

    result = runpy.run_path(str(sequence))["run"](input_path=str(folder / "b.HRF"), output_dir=str(tmp_path / "run"))

    assert result.dataset.dataframe["Scaled"].tolist() == [30.0, 40.0]
