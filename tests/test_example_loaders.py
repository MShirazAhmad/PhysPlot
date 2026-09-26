"""The bundled example loader plugins documented in docs/extensions/fileloading.rst."""

import importlib.util
import os
from pathlib import Path

import pytest

from physplot import PhysPlot

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "test_data"


def _plugin(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "config" / "data_importers" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_rigaku_ras_applies_the_attenuator_factor_and_auto_loader_uses_it():
    pp = PhysPlot()
    pp.load(DATA / "XRD" / "smartlab_si_powder.ras")
    df = pp.dataset.dataframe

    assert list(df.columns) == ["2Theta", "Intensity"]
    assert len(df) == 3001
    assert pp.dataset.metadata["loader_plugin"].endswith("rigaku_ras_loader.py")
    assert {column: pp.dataset.column_metadata[column]["suggested_role"] for column in df.columns} == {
        "2Theta": "X",
        "Intensity": "Y",
    }
    raw = next(
        line.split()
        for line in (DATA / "XRD" / "smartlab_si_powder.ras").read_text(encoding="latin-1").splitlines()
        if line.startswith("28.3000 ")
    )
    row = df[df["2Theta"].round(4) == 28.3]
    assert float(raw[2]) > 1
    assert row["Intensity"].iloc[0] == pytest.approx(float(raw[1]) * float(raw[2]))


def test_rigaku_ras_without_scan_block_is_a_clear_error(tmp_path):
    path = tmp_path / "empty.ras"
    path.write_text('*RAS_DATA_START\n*RAS_HEADER_START\n*FILE_SAMPLE "x"\n*RAS_HEADER_END\n', encoding="latin-1")
    with pytest.raises(ValueError, match="RAS_INT_START"):
        _plugin("rigaku_ras_loader").load_data(path)


def test_ta_instruments_export_names_columns_drops_markers_and_adds_weight_percent():
    table = _plugin("ta_instruments_loader").load_data(DATA / "Thermal" / "tga_calcium_oxalate.txt")

    assert list(table.columns) == [
        "Time (min)",
        "Temperature (°C)",
        "Weight (%)",
        "Weight (mg)",
        "Balance Purge Flow (mL/min)",
        "Sample Purge Flow (mL/min)",
    ]
    assert len(table) == 1740
    assert table["Time (min)"].min() > 0  # the -3 and -1 segment markers are gone
    assert table["Weight (%)"].iloc[0] == pytest.approx(100, abs=0.1)
    assert table["Weight (%)"].iloc[-1] == pytest.approx(38.4, abs=0.3)  # CaO residue


def test_ta_instruments_export_also_reads_utf8_and_dsc_runs(tmp_path):
    path = tmp_path / "dsc.txt"
    path.write_text(
        "Instrument\tDSC Q20\nSize\t5.0\tmg\nNsig\t3\nSig1\tTime (min)\nSig2\tTemperature (°C)\n"
        "Sig3\tHeat Flow (W/g)\nStartOfData\n-3\t1\t0\n0.1\t25.0\t-0.02\n0.2\t26.0\t-0.03\n",
        encoding="utf-8",
    )
    table = _plugin("ta_instruments_loader").load_data(path)
    assert list(table.columns) == ["Time (min)", "Temperature (°C)", "Heat Flow (W/g)"]
    assert table.shape == (2, 3)


def test_jcamp_dx_scales_values_and_builds_the_x_axis():
    pp = PhysPlot()
    pp.load(DATA / "FTIR" / "polystyrene_film.jdx")
    df = pp.dataset.dataframe

    assert list(df.columns) == ["Wavenumber (1/cm)", "Transmittance"]
    assert len(df) == 1801
    assert df["Wavenumber (1/cm)"].iloc[0] == pytest.approx(400)
    assert df["Wavenumber (1/cm)"].iloc[-1] == pytest.approx(4000)
    assert df["Wavenumber (1/cm)"].diff().dropna().round(6).unique().tolist() == [2.0]
    assert df["Transmittance"].between(0, 1).all()  # YFACTOR=0.0001 applied
    assert pp.dataset.metadata["loader_plugin"].endswith("jcamp_dx_loader.py")


def test_jcamp_dx_compressed_data_is_a_clear_error(tmp_path):
    path = tmp_path / "compressed.jdx"
    path.write_text(
        "##TITLE=x\n##XUNITS=1/CM\n##YUNITS=ABSORBANCE\n##FIRSTX=400\n##LASTX=402\n##NPOINTS=2\n"
        "##XYDATA=(X++(Y..Y))\n400@A\n##END=\n",
        encoding="latin-1",
    )
    with pytest.raises(ValueError, match="compressed"):
        _plugin("jcamp_dx_loader").load_data(path)


def test_gui_imports_ta_export_with_menu_loader_and_lists_plugin_types(monkeypatch):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    pytest.importorskip("PyQt6")
    from physplot.qt_compat import QtWidgets
    from physplot_gui.app.main_window import MainWindow, data_file_filter

    assert "*.ras" in data_file_filter() and "*.jdx" in data_file_filter()

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    window = MainWindow()
    path = DATA / "Thermal" / "tga_calcium_oxalate.txt"
    monkeypatch.setattr(QtWidgets.QFileDialog, "getOpenFileName", staticmethod(lambda *a, **k: (str(path), "")))
    entry = next(e for e in window.backend_loader_entries() if e["display_name"] == "TA Instruments TGA/DSC Loader")
    window.import_data(entry)

    assert window.state.roles["Temperature (°C)"] == "X"
    assert window.state.roles["Weight (%)"] == "Y"
    assert window.state.timeline[0]["details"] == "TA Instruments TGA/DSC Loader (column names and role setup)"
    window.close()
    app.processEvents()
