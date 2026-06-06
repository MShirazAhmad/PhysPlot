import os

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
