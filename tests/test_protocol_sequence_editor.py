import os

import pandas as pd
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PyQt6")

from physplot.qt_compat import QtCore, QtWidgets
from physplot.steps import LoadDataStep, PlotModuleStep, SetRoleStep, TransformColumnStep
from physplot_gui.app.main_window import MainWindow
from physplot_gui.panels.recorder_mode_panel import STATUS_COLUMN


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
    assert "Volts" in panel.timeline.item(1, STATUS_COLUMN).toolTip()
    assert "row 2" in panel.timeline.item(2, STATUS_COLUMN).toolTip()
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


def test_code_view_syntax_error_explains_line_and_keeps_sequence(monkeypatch):
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    window = MainWindow()
    window.mode_manager.set_mode("Advanced")
    window.apply_sequence_code(
        "from physplot.steps import SetRoleStep\nWORKFLOW_STEPS = [SetRoleStep(roles={'x': 'Time'})]\n"
    )
    panel = window.mode_manager.panels["Advanced"].sequence_builder
    panel._set_view_mode(1)
    panel.code_view.setPlainText("from physplot.steps import SetRoleStep\nWORKFLOW_STEPS = [SetRoleStep(\n")
    messages = []
    monkeypatch.setattr(QtWidgets.QMessageBox, "warning", lambda parent, title, text: messages.append(text))

    panel.apply_code_button.click()

    assert len(messages) == 1
    assert "Python syntax error on line 2" in messages[0]
    assert "WORKFLOW_STEPS = [SetRoleStep(" in messages[0]
    assert "not changed" in messages[0]
    assert panel.code_view.textCursor().selectedText() == "WORKFLOW_STEPS = [SetRoleStep("
    assert [type(step) for step in window.state.pp.workflow] == [SetRoleStep]

    window.close()
    app.quit()


def test_bulk_failure_names_the_input_file(tmp_path):
    input_folder = tmp_path / "input"
    input_folder.mkdir()
    pd.DataFrame({"Voltage": [1.0, 2.0]}).to_csv(input_folder / "a_good.csv", index=False)
    pd.DataFrame({"Voltage": ["high", "low"]}).to_csv(input_folder / "b_text.csv", index=False)
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    window = MainWindow()
    window.state.pp.workflow = [TransformColumnStep("Voltage", "multiply", "V2", params={"factor": 2})]

    window.run_bulk_workflow({"input_folder": str(input_folder), "workflow_file": "", "output_folder": str(tmp_path / "out")})

    title, error = window.last_error
    assert title == "Bulk run failed"
    assert str(error).startswith("Bulk run stopped at b_text.csv: Column 'Voltage' does not contain numeric values")
    assert (tmp_path / "out" / "a_good" / "data.csv").exists()

    window.close()
    app.quit()


def test_plugin_with_clashing_display_name_stays_in_function_menu(tmp_path, monkeypatch):
    folder = tmp_path / "PhysPlotUser" / "config" / "transformations"
    folder.mkdir(parents=True)
    (folder / "50_scaled_log.py").write_text("DISPLAY_NAME = 'log10'\ndef transform(values):\n    return values\n")
    monkeypatch.setenv("PHYSPLOT_USER_DIR", str(tmp_path / "PhysPlotUser"))
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    window = MainWindow()

    labels = {entry["display_name"]: entry for entry in window.simple_function_entries()}

    assert labels["log10"].get("function_name") == "log10"
    assert labels["log10 (50_scaled_log)"]["name"] == "50_scaled_log"

    window.close()
    app.quit()


def test_long_status_message_does_not_widen_window():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    window = MainWindow()
    window.resize(1200, 800)
    window.show()
    app.processEvents()
    width_before = window.width()
    minimum_before = window.minimumSizeHint().width()
    message = "Row 2 failed (TransformColumnStep): " + "very long error detail " * 40

    window.status.set_message(message)
    app.processEvents()

    assert window.width() == width_before
    assert window.minimumSizeHint().width() == minimum_before
    assert window.status.status.text() == f"Status: {message.strip()}"
    assert window.status.status.toolTip() == f"Status: {message.strip()}"

    window.close()
    app.quit()


def test_main_window_fits_laptop_screens_and_simple_mode_scrolls():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.processEvents()
    panel = window.mode_manager.panels["Simple"]

    assert window.minimumSizeHint().width() <= 1280
    window.resize(1100, 800)
    app.processEvents()
    assert window.width() == 1100
    assert panel._needs_scroll
    assert window.mode_manager.stack.height() == panel.fitted_height()

    window.resize(2400, 800)
    app.processEvents()
    assert not panel._needs_scroll
    assert window.mode_manager.stack.height() == panel.fitted_height()

    window.close()
    app.quit()


def test_simple_mode_area_fits_styled_panels_without_a_resize():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    window = MainWindow()
    window.resize(2400, 900)
    window.show()
    for _ in range(3):
        app.processEvents()
    panel = window.mode_manager.panels["Simple"]

    assert window.mode_manager.stack.height() >= panel._content.sizeHint().height()

    window.close()
    app.quit()


def test_simple_mode_input_defaults_to_y_column_and_function_labels(tmp_path, monkeypatch):
    from pathlib import Path

    from physplot.qt_compat import QtCore

    hrf = Path(__file__).resolve().parents[1] / "test_data" / "OES" / "spectrum_1.HRF"
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    window = MainWindow()
    panel = window.mode_manager.panels["Simple"]
    monkeypatch.setattr(QtWidgets.QFileDialog, "getOpenFileName", lambda *args, **kwargs: (str(hrf), ""))

    window.import_data("auto")

    assert panel.input_column.currentData() == "Intensity"

    # A choice survives new output columns; only new data resets it.
    panel.input_column.setCurrentIndex(panel.input_column.findData("Wavelength"))
    panel.function.setCurrentIndex(panel.function.findText("x^2"))
    panel.output_column.setEditText("Wavelength_sq")
    panel._apply()
    assert window.last_error is None
    assert panel.input_column.currentData() == "Wavelength"

    index = panel.function.findText("subtract first value")
    assert panel.function.itemData(index)["function_name"] == "baseline_subtract"
    tooltip = panel.function.itemData(index, QtCore.Qt.ItemDataRole.ToolTipRole)
    assert "XRD: Baseline Remove" in tooltip
    square = panel.function.findText("x^2")
    assert "02_square.py" in panel.function.itemData(square, QtCore.Qt.ItemDataRole.ToolTipRole)
    assert panel.function.findText("baseline_subtract") == -1

    window.close()
    app.quit()


# -- Phase 2: editable, reorderable, and disableable rows --------------------


def _window_with(steps):
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    window = MainWindow()
    window.mode_manager.set_mode("Advanced")
    window.state.pp.workflow = list(steps)
    window.state.timeline = window._sequence_rows_from_steps(window.state.pp.workflow)
    window.apply_current_sequence()
    panel = window.mode_manager.panels["Advanced"].sequence_builder
    return app, window, panel


def _csv(tmp_path):
    data_path = tmp_path / "data.csv"
    data_path.write_text("Time,Voltage\n1,2\n2,4\n3,8\n", encoding="utf-8")
    return data_path


def test_step_editor_changes_function_and_updates_code_and_table(tmp_path):
    from physplot_gui.widgets.step_editor import StepEditorDialog

    load = LoadDataStep(path=str(_csv(tmp_path)), loader="csv", dataset_name="data")
    app, window, panel = _window_with(
        [
            load,
            TransformColumnStep("Voltage", "multiply", "V_out", params={"factor": 1000}, input_column_number=2),
            SetRoleStep(roles={"x": "Time", "y": "V_out"}),
        ]
    )
    assert window.central_table.to_dataframe()["V_out"].tolist() == [2000, 4000, 8000]

    dialog = StepEditorDialog(window._steps_for_row(window.state.timeline[1]), window._table_columns())
    fields = dialog.widgets[0]
    fields["function_name"].setCurrentText("divide")
    fields["params"].setText("{'divisor': 2}")
    fields["input_column"].setCurrentText("Time")
    assert fields["input_column_number"].text() == "1"  # number fallback follows the column
    fields["input_column"].setCurrentText("Voltage")

    load_calls = []
    original_apply = load.apply
    load.apply = lambda *args, **kwargs: load_calls.append(1) or original_apply(*args, **kwargs)
    window.apply_step_edits(1, dialog.validated_values())

    code = panel.code_view.toPlainText()
    assert "function_name='divide'" in code
    assert "params={'divisor': 2}" in code
    assert window.central_table.to_dataframe()["V_out"].tolist() == [1, 2, 4]
    assert panel.timeline.item(1, 3).text() == "divide"
    assert [panel.status_text(row) for row in range(3)] == ["ok", "ok", "ok"]
    assert load_calls == []  # resumed from the edited row, the file was not reloaded

    window.close()
    app.quit()


def test_step_editor_reports_invalid_values_without_closing():
    from physplot_gui.widgets.step_editor import StepEditorDialog

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    step = TransformColumnStep("Voltage", "multiply", "V_out", params={"factor": 1000})
    dialog = StepEditorDialog([step], ["Time", "Voltage"])
    dialog.widgets[0]["params"].setText("[1, 2]")

    dialog._try_accept()

    assert dialog.result_values is None
    assert not dialog.error_label.isHidden()
    assert "Parameters must be a dict" in dialog.error_label.text()
    assert step.params == {"factor": 1000}
    app.quit()


def test_disabled_row_is_skipped_and_round_trips_through_sequence_code(tmp_path):
    app, window, panel = _window_with(
        [
            LoadDataStep(path=str(_csv(tmp_path)), loader="csv", dataset_name="data"),
            TransformColumnStep("Voltage", "multiply", "V_mV", params={"factor": 1000}),
            SetRoleStep(roles={"x": "Time", "y": "Voltage"}),
        ]
    )
    assert "V_mV" in window.central_table.column_names()

    # Untick the checkbox the way a user would; the change is applied on the next event loop turn.
    panel.timeline.item(1, 0).setCheckState(QtCore.Qt.CheckState.Unchecked)
    app.processEvents()

    assert window.state.pp.workflow[1].enabled is False
    assert [panel.status_text(row) for row in range(3)] == ["ok", "skipped", "ok"]
    assert panel.timeline.item(1, STATUS_COLUMN).toolTip().startswith("Disabled")
    assert panel.enabled_state(1) is False
    assert "V_mV" not in window.central_table.column_names()
    assert "enabled=False" in panel.code_view.toPlainText()

    exported = tmp_path / "sequence.py"
    window.state.pp.save_workflow(exported)
    window.apply_sequence_code(exported.read_text(encoding="utf-8"))
    assert [step.enabled for step in window.state.pp.workflow] == [True, False, True]
    assert panel.enabled_state(1) is False

    window.set_timeline_row_enabled(1, True)
    assert "V_mV" in window.central_table.column_names()
    assert panel.status_text(1) == "ok"

    window.close()
    app.quit()


def test_moving_roles_below_plot_reports_failure_status_without_dialog(tmp_path):
    app, window, panel = _window_with(
        [
            LoadDataStep(path=str(_csv(tmp_path)), loader="csv", dataset_name="data"),
            TransformColumnStep("Voltage", "multiply", "V_mV", params={"factor": 1000}),
            SetRoleStep(roles={"x": "Time", "y": "V_mV"}),
            PlotModuleStep(plotter_id="basic", plot_type="scatter", config={}),
        ]
    )
    assert [panel.status_text(row) for row in range(4)] == ["ok"] * 4
    window.last_error = None

    assert not window.can_move_timeline_row(0, 1)  # the Load Data row is pinned first
    assert not window.can_move_timeline_row(1, -1)  # nothing moves above it
    assert not window.can_move_timeline_row(3, 1)
    window.move_timeline_row(2, 1)

    assert [type(step) for step in window.state.pp.workflow] == [LoadDataStep, TransformColumnStep, PlotModuleStep, SetRoleStep]
    assert [panel.timeline.item(row, 2).text() for row in range(4)] == ["File Loader", "Transform", "Generate Plot", "Set Roles"]
    assert [panel.status_text(row) for row in range(4)] == ["ok", "ok", "failed", "skipped"]
    assert "No column has role 'X'" in panel.timeline.item(2, STATUS_COLUMN).toolTip()
    assert window.last_error is None
    assert window.status.status.text().startswith("Status: Row 3 failed (PlotModuleStep)")
    assert panel.timeline.selectionModel().selectedRows()[0].row() == 3

    window.move_timeline_row(3, -1)
    assert [panel.status_text(row) for row in range(4)] == ["ok"] * 4

    window.close()
    app.quit()


def test_insert_steps_and_protocol_modules_after_selected_row(tmp_path):
    app, window, panel = _window_with(
        [
            LoadDataStep(path=str(_csv(tmp_path)), loader="csv", dataset_name="data"),
            SetRoleStep(roles={"x": "Time", "y": "Voltage"}),
        ]
    )
    # Load Data and its role setup share one row.
    assert panel.timeline.rowCount() == 1

    window.insert_steps([TransformColumnStep("Voltage", "multiply", "V_mV", params={"factor": 1000})], after_row=0)
    assert [panel.timeline.item(row, 2).text() for row in range(2)] == ["File Loader", "Transform"]
    assert window.central_table.to_dataframe()["V_mV"].tolist() == [2000, 4000, 8000]

    module = tmp_path / "time_ms.py"
    module.write_text(
        "from physplot.steps import TransformColumnStep\n"
        "WORKFLOW_STEPS = [TransformColumnStep('Time', 'multiply', 'T_ms', params={'factor': 1000})]\n",
        encoding="utf-8",
    )
    window.insert_protocol_module(module, after_row=0)
    assert [panel.timeline.item(row, 3).text() for row in range(3)] == ["CSV Loader (column names and role setup)", "multiply", "multiply"]
    assert window.state.pp.workflow[2].output == "T_ms"
    assert window.state.pp.workflow[3].output == "V_mV"

    # With no row selected, inserting appends; nothing goes above the Load Data row.
    window.insert_steps([SetRoleStep(roles={"x": "T_ms", "y": "V_mV"})])
    window.insert_steps([TransformColumnStep("Time", "add", "T_plus", params={"value": 1})], after_row=None)
    assert type(window.state.pp.workflow[0]) is LoadDataStep
    assert [panel.status_text(row) for row in range(panel.timeline.rowCount())] == ["ok"] * 5
    assert window.state.roles["T_ms"] == "X"

    window.close()
    app.quit()


def test_protocol_menu_offers_insert_step():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    window = MainWindow()
    labels = [action.text() for action in window.protocol_menu.actions()]
    assert "Insert Step..." in labels
    window.close()
    app.quit()
