"""Every file shipped in test_data/ must keep loading."""

from pathlib import Path

import pytest

from physplot import PhysPlot
from physplot.bulk import run_folder
from physplot.steps import LoadDataStep, TransformColumnStep
from physplot.user_paths import bundled_plugin_dir

TEST_DATA = Path(__file__).resolve().parents[1] / "test_data"
OES_LOADER = bundled_plugin_dir("data_importers") / "oes_hrf_loader.py"

AUTO_LOADED = {
    "sample_linear.csv": ["Time", "Voltage", "Error", "Group"],
    "XRD/quick_scan.xrdml": ["2Theta", "Intensity"],
    "XRD/repeated_scans.xrdml": ["2Theta", "Intensity", "Intensity 1", "Intensity 2", "Intensity 3"],
    "XRD/schema1.5_scan.XRDML": ["2Theta", "Intensity"],
    "XRD/panalytical_export.csv": ["Angle", "Intensity"],
    "EDS/smartquant_spot.csv": ["Element", "Weight %", "Atomic %", "Error %"],
}


@pytest.mark.parametrize("name", sorted(AUTO_LOADED))
def test_sample_columns(name):
    columns = list(PhysPlot().load(TEST_DATA / name).dataframe.columns)

    assert columns[: len(AUTO_LOADED[name])] == AUTO_LOADED[name]


@pytest.mark.parametrize(
    "name",
    sorted(
        str(path.relative_to(TEST_DATA))
        for path in TEST_DATA.rglob("*")
        if path.is_file() and not path.name.startswith(".") and path.suffix.lower() != ".md"
    ),
)
def test_every_sample_has_numeric_data(name):
    frame = PhysPlot().load(TEST_DATA / name).dataframe

    numeric = [column for column in frame.columns if frame[column].dtype.kind in "if"]
    assert len(frame) >= 2 and len(numeric) >= 2


def test_oes_folder_bulk_run_with_the_hrf_loader_plugin(tmp_path):
    folder = TEST_DATA / "OES"
    steps = [
        LoadDataStep(path=str(folder / "spectrum_1.HRF"), loader="dataframe", loader_plugin=str(OES_LOADER)),
        TransformColumnStep("Intensity", "normalize_max", "Intensity_norm"),
    ]

    outputs = run_folder(steps, folder, tmp_path / "out")

    assert sorted(path.name for path in outputs) == ["spectrum_1", "spectrum_2", "spectrum_3"]


def test_auto_loader_opens_hrf_through_the_oes_plugin():
    dataset = PhysPlot().load(TEST_DATA / "OES" / "spectrum_1.HRF")
    dataset.apply_suggested_roles()

    assert list(dataset.dataframe.columns) == ["Wavelength", "Intensity"]
    assert dataset.column_roles == {"Wavelength": "X", "Intensity": "Y"}
    assert dataset.metadata["loader_plugin"].endswith("oes_hrf_loader.py")


def test_auto_loader_recorded_sequence_bulk_runs_hrf_folder(tmp_path):
    folder = TEST_DATA / "OES"
    steps = [
        LoadDataStep(path=str(folder / "spectrum_1.HRF"), loader="auto"),
        TransformColumnStep("Intensity", "normalize_max", "Intensity_norm"),
    ]

    outputs = run_folder(steps, folder, tmp_path / "out")

    assert sorted(path.name for path in outputs) == ["spectrum_1", "spectrum_2", "spectrum_3"]


def test_plugin_extensions_and_unknown_extension_message(monkeypatch, tmp_path):
    importers = tmp_path / "user" / "config" / "data_importers"
    importers.mkdir(parents=True)
    (importers / "pipe_loader.py").write_text(
        'title = "Pipe loader"\nFILE_EXTENSIONS = ["xyz"]\nCOLUMN_NAMES = ["a", "b"]\n'
        "def load_data(path):\n    return [[float(v) for v in line.split('|')] for line in open(path)]\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("PHYSPLOT_USER_DIR", str(tmp_path / "user"))
    data = tmp_path / "scan.XYZ"
    data.write_text("1|2\n3|4\n", encoding="utf-8")
    unknown = tmp_path / "scan.abc"
    unknown.write_text("1,2\n", encoding="utf-8")

    assert PhysPlot().load(data).dataframe["b"].tolist() == [2.0, 4.0]
    with pytest.raises(ValueError, match=r"No loader for '\.abc' files.*FILE_EXTENSIONS"):
        PhysPlot().load(unknown)
