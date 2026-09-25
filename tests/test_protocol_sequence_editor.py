import os

import pandas as pd
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PyQt6")

from physplot.qt_compat import QtWidgets
from physplot.steps import LoadDataStep, PlotModuleStep, SetRoleStep, TransformColumnStep
from physplot_gui.app.main_window import MainWindow


def test_protocol_code_editor_updates_table_and_deletes_update_code():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    window = MainWindow()
    window.mode_manager.set_mode("Advanced")

    source = """
from physplot.steps import PlotModuleStep, SetRoleStep

WORKFLOW_STEPS = [
    SetRoleStep(roles={'x': 'Time', 'y': 'Voltage'}),
    PlotModuleStep(plotter_id='basic', plot_type='scatter', config={}),
]
"""
    window.apply_sequence_code(source)

    assert [type(step) for step in window.state.pp.workflow] == [SetRoleStep, PlotModuleStep]
    assert len(window.state.timeline) == 2

    panel = window.mode_manager.panels["Advanced"].sequence_builder
    assert panel.apply_code_button.text() == "Apply Code to Table"
    assert panel.apply_code_button.isHidden()
    panel._set_view_mode(1)
    assert not panel.apply_code_button.isHidden()
    assert "PlotModuleStep" in panel.code_view.toPlainText()

    window.delete_timeline_step(1)

    assert len(window.state.pp.workflow) == 1
    assert "plotter_id='basic'" not in panel.code_view.toPlainText()
    assert "SetRoleStep" in panel.code_view.toPlainText()

    window.close()
    app.quit()


def test_deleting_protocol_step_replays_revised_sequence_on_table(tmp_path):
    data_path = tmp_path / "data.csv"
    data_path.write_text("Time,Voltage\n1,2\n2,4\n", encoding="utf-8")

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    window = MainWindow()
    window.mode_manager.set_mode("Advanced")
    window.state.pp.workflow = [
        LoadDataStep(path=str(data_path), loader="csv", dataset_name="data"),
        SetRoleStep(roles={"x": "Time", "y": "Voltage"}),
        TransformColumnStep("Voltage", "multiply", "Voltage_mV", params={"factor": 1000}),
    ]
    window.state.timeline = window._sequence_rows_from_steps(window.state.pp.workflow)

    window.apply_current_sequence()
    assert "Voltage_mV" in window.central_table.column_names()

    window.delete_timeline_step(1)

    assert [type(step) for step in window.state.pp.workflow] == [LoadDataStep, SetRoleStep]
    assert "Voltage_mV" not in window.central_table.column_names()
    assert window.central_table.to_dataframe()["Voltage"].tolist() == [2, 4]

    window.close()
    app.quit()


def test_bulk_panel_payload_is_sequence_driven():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    window = MainWindow()
    window.mode_manager.set_mode("Advanced")
    bulk_panel = window.mode_manager.panels["Advanced"].recorder.bulk

    payload = bulk_panel.payload()

    assert "plot_mode" not in payload
    assert "dpi" not in payload
    assert not hasattr(bulk_panel, "plot_mode")
    assert not hasattr(bulk_panel, "dpi")

    window.close()
    app.quit()


def _four_row_sequence(data_path):
    return [
        LoadDataStep(path=str(data_path), loader="csv", dataset_name="data"),
        TransformColumnStep("Volts", "multiply", "Voltage_mV", params={"factor": 1000}),
        TransformColumnStep("Time", "multiply", "Time_ms", params={"factor": 1000}),
        SetRoleStep(roles={"x": "Time_ms", "y": "Voltage_mV"}),
    ]


def test_failing_step_shows_status_per_row_and_keeps_table(tmp_path):
    data_path = tmp_path / "data.csv"
    data_path.write_text("Time,Voltage\n1,2\n2,4\n", encoding="utf-8")

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    window = MainWindow()
    window.mode_manager.set_mode("Advanced")
    window.state.pp.workflow = _four_row_sequence(data_path)
    window.state.timeline = window._sequence_rows_from_steps(window.state.pp.workflow)

    window.apply_current_sequence()

    panel = window.mode_manager.panels["Advanced"].sequence_builder
    assert panel.timeline.rowCount() == 4
    assert [panel.status_text(row) for row in range(4)] == ["ok", "failed", "skipped", "skipped"]
    assert "Volts" in panel.timeline.item(1, 4).toolTip()
    assert "row 2" in panel.timeline.item(2, 4).toolTip()
    title, error = window.last_error
    assert title == "Apply sequence failed"
    assert str(error).startswith("Row 2 failed (TransformColumnStep)")
    # The table shows the state reached before the failure: the loaded file.
    assert window.central_table.column_names()[:2] == ["Time", "Voltage"]

    window.close()
    app.quit()


def test_rerun_from_row_resumes_without_reloading(tmp_path):
    data_path = tmp_path / "data.csv"
    data_path.write_text("Time,Voltage\n1,2\n2,4\n", encoding="utf-8")

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    window = MainWindow()
    window.mode_manager.set_mode("Advanced")
    steps = _four_row_sequence(data_path)
    window.state.pp.workflow = steps
    window.state.timeline = window._sequence_rows_from_steps(steps)
    window.apply_current_sequence()

    load_calls = []
    original_apply = steps[0].apply
    steps[0].apply = lambda *args, **kwargs: load_calls.append(1) or original_apply(*args, **kwargs)
    steps[1] = TransformColumnStep("Voltage", "multiply", "Voltage_mV", params={"factor": 1000})

    window.rerun_from_timeline_step(1)

    panel = window.mode_manager.panels["Advanced"].sequence_builder
    assert load_calls == []
    assert [panel.status_text(row) for row in range(4)] == ["ok", "ok", "ok", "ok"]
    frame = window.central_table.to_dataframe()
    assert frame["Voltage_mV"].tolist() == [2000, 4000]
    assert frame["Time_ms"].tolist() == [1000, 2000]
    assert window.state.roles["Voltage_mV"] == "Y"

    window.close()
    app.quit()


def test_deleting_a_row_reports_failure_without_dialog(tmp_path):
    data_path = tmp_path / "data.csv"
    data_path.write_text("Time,Voltage\n1,2\n2,4\n", encoding="utf-8")

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    window = MainWindow()
    window.mode_manager.set_mode("Advanced")
    window.state.pp.workflow = [
        LoadDataStep(path=str(data_path), loader="csv", dataset_name="data"),
        TransformColumnStep("Voltage", "multiply", "Voltage_mV", params={"factor": 1000}),
        SetRoleStep(roles={"x": "Time", "y": "Voltage_mV"}),
    ]
    window.state.timeline = window._sequence_rows_from_steps(window.state.pp.workflow)
    window.apply_current_sequence()
    window.last_error = None

    window.delete_timeline_step(1)

    panel = window.mode_manager.panels["Advanced"].sequence_builder
    assert [panel.status_text(row) for row in range(2)] == ["ok", "failed"]
    assert window.last_error is None
    assert window.status.status.text().startswith("Status: Row 2 failed (SetRoleStep)")

    window.close()
    app.quit()


def test_simple_mode_plugin_transform_is_recorded_and_replays(tmp_path, monkeypatch):
    monkeypatch.setenv("PHYSPLOT_USER_DIR", str(tmp_path / "PhysPlotUser"))
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    window = MainWindow()
    window.state.load_dataframe(pd.DataFrame({"Time": [0, 1, 2], "Voltage": [1.0, 2.0, 3.0]}), name="sample")
    window.central_table.set_dataframe(window.state.dataframe, window.state.roles)
    window._refresh_all()

    panel = window.mode_manager.panels["Simple"]
    panel.input_column.setCurrentIndex(panel.input_column.findData("Voltage"))
    panel.function.setCurrentIndex(panel.function.findText("x^2"))
    panel.offset.setText("0.5")
    panel.output_column.setEditText("Voltage_sq")
    panel._apply()

    assert window.last_error is None
    (step,) = window.state.pp.workflow
    assert isinstance(step, TransformColumnStep)
    assert (step.input_column, step.function_name, step.output) == ("Voltage", "02_square", "Voltage_sq")
    assert step.params == {"multiplier": 1.0, "offset": 0.5}
    assert window.central_table.to_dataframe()["Voltage_sq"].tolist() == [1.5, 4.5, 9.5]
    assert window.state.timeline[-1]["details"] == "x^2"
    assert "'02_square'" in window.state.timeline[-1]["code"]
    assert "function_name='02_square'" in window.sequence_code_text()

    # Replaying on fresh data must recreate the plugin column from the sequence alone.
    window.state.load_dataframe(pd.DataFrame({"Time": [0, 1], "Voltage": [4.0, 5.0]}), name="fresh")
    window.central_table.set_dataframe(window.state.dataframe, window.state.roles)
    window.apply_current_sequence()

    assert window.last_error is None
    assert window.central_table.to_dataframe()["Voltage_sq"].tolist() == [16.5, 25.5]

    window.close()
    app.quit()
