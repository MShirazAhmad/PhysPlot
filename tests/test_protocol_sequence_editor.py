import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PyQt6")

from physplot.qt_compat import QtWidgets
from physplot.steps import PlotModuleStep, SetRoleStep
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
