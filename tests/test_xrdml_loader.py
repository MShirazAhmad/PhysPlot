import os

import numpy as np
import pandas as pd
import pytest

from physplot import PhysPlot
from physplot.bulk import run_folder
from physplot.steps import SetRoleStep, TransformColumnStep

NS = "http://www.xrdml.com/XRDMeasurement/1.7"


def scan_xml(counts, start=10.0, end=10.2, attenuation=None, positions=None, counts_tag="intensities", axis="Gonio"):
    if positions is None:
        positions = (
            f'<positions axis="2Theta" unit="deg"><startPosition>{start}</startPosition>'
            f"<endPosition>{end}</endPosition></positions>"
            '<positions axis="Omega" unit="deg"><startPosition>5.0</startPosition><endPosition>5.1</endPosition></positions>'
        )
    factor = f"<commonBeamAttenuationFactor>{attenuation}</commonBeamAttenuationFactor>" if attenuation else ""
    return (
        f'<scan appendNumber="0" mode="Continuous" scanAxis="{axis}" status="Completed">'
        "<header><startTimeStamp>2025-03-06T10:00:00-06:00</startTimeStamp></header>"
        f"<dataPoints>{positions}{factor}<commonCountingTime unit=\"seconds\">0.5</commonCountingTime>"
        f'<{counts_tag} unit="counts">{" ".join(str(c) for c in counts)}</{counts_tag}></dataPoints></scan>'
    )


def write_xrdml(path, *scans):
    path.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>'
        f'<xrdMeasurements xmlns="{NS}" status="Completed">'
        '<sample type="To be analyzed"><id>S1</id><name>Test powder</name></sample>'
        '<xrdMeasurement measurementType="Scan" status="Completed">'
        '<usedWavelength intended="K-Alpha 1"><kAlpha1 unit="Angstrom">1.5405980</kAlpha1>'
        '<kAlpha2 unit="Angstrom">1.5444260</kAlpha2><ratioKAlpha2KAlpha1>0.5</ratioKAlpha2KAlpha1></usedWavelength>'
        "<incidentBeamPath><xRayTube><tension unit=\"kV\">45</tension><current unit=\"mA\">40</current>"
        "<anodeMaterial>Cu</anodeMaterial></xRayTube></incidentBeamPath>"
        + "".join(scans)
        + "</xrdMeasurement></xrdMeasurements>",
        encoding="utf-8",
    )
    return path


def test_single_scan_loads_angle_intensity_roles_and_metadata(tmp_path):
    path = write_xrdml(tmp_path / "scan.xrdml", scan_xml([5, 7, 9]))

    dataset = PhysPlot().load(path)
    dataset.apply_suggested_roles()

    frame = dataset.dataframe
    assert list(frame.columns) == ["2Theta", "Intensity"]
    assert frame["2Theta"].tolist() == pytest.approx([10.0, 10.1, 10.2])
    assert frame["Intensity"].tolist() == [5, 7, 9]
    assert dataset.column_roles == {"2Theta": "X", "Intensity": "Y"}
    meta = dataset.metadata["xrdml"]
    assert meta["schema"] == "1.7" and meta["sample_name"] == "Test powder" and meta["anode"] == "Cu"
    assert meta["wavelength_kAlpha1"] == pytest.approx(1.540598)
    assert meta["counting_time_s"] == 0.5 and meta["points"] == 3


def test_repeated_scans_are_summed_like_the_vendor_export(tmp_path):
    path = write_xrdml(tmp_path / "reps.xrdml", scan_xml([1, 2, 3]), scan_xml([10, 20, 30], attenuation="84.80"))

    dataset = PhysPlot().load(path)
    dataset.apply_suggested_roles()

    frame = dataset.dataframe
    assert list(frame.columns) == ["2Theta", "Intensity", "Intensity 1", "Intensity 2"]
    assert frame["Intensity"].tolist() == [11, 22, 33]
    assert dataset.metadata["xrdml"]["beam_attenuation_factors"] == [1.0, 84.8]
    assert dataset.column_roles["Intensity"] == "Y" and dataset.column_roles["Intensity 2"] == "Ignore"


def test_list_positions_counts_tag_and_omega_rocking_curve(tmp_path):
    positions = (
        '<positions axis="2Theta" unit="deg"><commonPosition>44.5</commonPosition></positions>'
        '<positions axis="Omega" unit="deg"><listPositions>21.9 22.0 22.3</listPositions></positions>'
    )
    path = write_xrdml(tmp_path / "rock.XRDML", scan_xml([4, 8, 2], positions=positions, counts_tag="counts", axis="Omega"))

    frame = PhysPlot().load(path).dataframe

    assert list(frame.columns) == ["Omega", "Intensity"]
    assert frame["Omega"].tolist() == [21.9, 22.0, 22.3]


def test_mismatched_scans_and_broken_xml_are_reported(tmp_path):
    mismatched = write_xrdml(tmp_path / "bad.xrdml", scan_xml([1, 2, 3]), scan_xml([1, 2, 3], end=11.0))
    broken = tmp_path / "broken.xrdml"
    broken.write_text("<xrdMeasurements><scan>", encoding="utf-8")

    with pytest.raises(ValueError, match="does not share the 2Theta range of scan 1"):
        PhysPlot().load(mismatched)
    with pytest.raises(ValueError, match="not a readable XRDML file"):
        PhysPlot().load(broken)


def test_bulk_run_processes_xrdml_files(tmp_path):
    folder = tmp_path / "scans"
    folder.mkdir()
    write_xrdml(folder / "a.xrdml", scan_xml([1, 2, 3]))
    write_xrdml(folder / "b.XRDML", scan_xml([4, 5, 6]))
    steps = [
        SetRoleStep({"x": "2Theta", "y": "Intensity"}),
        TransformColumnStep("Intensity", "multiply", "Doubled", params={"factor": 2}),
    ]

    outputs = run_folder(steps, folder, tmp_path / "out")

    assert sorted(path.name for path in outputs) == ["a", "b"]
    assert pd.read_csv(tmp_path / "out" / "b" / "data.csv")["Doubled"].tolist() == [8, 10, 12]


def test_gui_imports_xrdml_with_auto_loader(tmp_path, monkeypatch):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    pytest.importorskip("PyQt6")
    from physplot.qt_compat import QtWidgets
    from physplot_gui.app.main_window import MainWindow

    path = write_xrdml(tmp_path / "scan.xrdml", scan_xml([5, 7, 9]))
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    window = MainWindow()
    monkeypatch.setattr(QtWidgets.QFileDialog, "getOpenFileName", lambda *args, **kwargs: (str(path), ""))

    window.import_data("auto")

    assert window.last_error is None
    assert window.central_table.column_names()[:2] == ["2Theta", "Intensity"]
    assert window.state.roles["2Theta"] == "X" and window.state.roles["Intensity"] == "Y"
    assert np.allclose(window.central_table.to_dataframe()["Intensity"], [5, 7, 9])
    window.close()
    app.processEvents()


def test_gui_imports_hrf_with_auto_loader(monkeypatch):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    pytest.importorskip("PyQt6")
    from pathlib import Path

    from physplot.qt_compat import QtWidgets
    from physplot_gui.app.main_window import MainWindow

    path = Path(__file__).resolve().parents[1] / "test_data" / "OES" / "spectrum_1.HRF"
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    window = MainWindow()
    monkeypatch.setattr(QtWidgets.QFileDialog, "getOpenFileName", lambda *args, **kwargs: (str(path), ""))

    window.import_data("auto")

    assert window.last_error is None
    assert window.central_table.column_names()[:2] == ["Wavelength", "Intensity"]
    assert window.state.roles["Wavelength"] == "X" and window.state.roles["Intensity"] == "Y"
    window.close()
    app.processEvents()
