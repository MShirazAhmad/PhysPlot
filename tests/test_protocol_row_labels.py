import os
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PyQt6")

from physplot.qt_compat import QtWidgets
from physplot_gui.app.main_window import MainWindow

SAMPLE = Path(__file__).resolve().parents[1] / "test_data" / "sample_linear.csv"


def _texts(rows):
    return [(row["action"], row["details"], row["target"]) for row in rows]


def _record_session(window, monkeypatch):
    """Import, transform with a plugin, move the Y role and plot, as a user would."""
    monkeypatch.setattr(QtWidgets.QFileDialog, "getOpenFileName", staticmethod(lambda *a, **k: (str(SAMPLE), "")))
    monkeypatch.setattr(window, "_show_module_figure", lambda *args: None)
    window.import_data("auto")
    square = next(entry for entry in window.simple_function_entries() if entry.get("name") == "02_square")
    window.apply_backend_transform("Voltage", square, 1.0, 0.0, "Voltage_sq")
    window.set_column_role("Voltage_sq", "Y")
    window.generate_module_plot("line", "line")


def test_reopened_sequence_rows_read_like_the_recorded_rows(monkeypatch):
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    window = MainWindow()
    _record_session(window, monkeypatch)

    recorded = _texts(window.state.timeline)
    rebuilt = _texts(MainWindow._sequence_rows_from_steps(list(window.state.pp.workflow)))

    assert recorded == [
        ("File Loader", "Auto Loader (column names and role setup)", "sample_linear.csv"),
        ("Transform", "x^2", "Voltage -> Voltage_sq"),
        ("Set Y", "Set column as Y", "Voltage_sq"),
        ("Generate Plot", "Create line line", "Plotter Module"),
    ]
    assert rebuilt == recorded
    window.close()
    app.processEvents()


def test_role_change_row_appears_in_build_protocol_without_a_full_refresh(monkeypatch):
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    window = MainWindow()
    _record_session(window, monkeypatch)
    timeline = window.mode_manager.panels["Advanced"].sequence_builder.timeline
    rows_before = timeline.rowCount()

    window.set_column_role("Time", "Group")
    app.processEvents()

    assert timeline.rowCount() == rows_before + 1
    assert timeline.item(rows_before, 1).text() == "Set Group"
    window.close()
    app.processEvents()


def test_status_bar_counts_and_file_follow_the_data(monkeypatch):
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    window = MainWindow()
    # The blank start-up table holds no values.
    assert (window.state.row_count, window.state.column_count) == (0, 0)

    _record_session(window, monkeypatch)
    window.state.current_file = None
    window.apply_current_sequence()

    # Replaying the File Loader step reloads the file, which the status bar now names.
    assert window.state.current_file is not None and window.state.current_file.name == "sample_linear.csv"
    assert window.status.file.text() == "File: sample_linear.csv"
    window.close()
    app.processEvents()
