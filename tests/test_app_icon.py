import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PyQt6")

from physplot.qt_compat import QtWidgets
from physplot_gui.app import runner
from physplot_gui.app.main_window import LOGO_ICON


def test_app_icon_is_set_for_every_window(monkeypatch):
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    monkeypatch.setattr(QtWidgets.QApplication, "exec_", lambda self: 0, raising=False)
    monkeypatch.setattr(QtWidgets.QApplication, "exec", lambda self: 0, raising=False)

    assert runner.run_app() == 0

    assert LOGO_ICON.stat().st_size < 1_000_000
    assert not app.windowIcon().isNull()
    assert not QtWidgets.QWidget().windowIcon().isNull()
    runner._WINDOW.close()


def test_figure_editor_window_gets_the_physplot_icon():
    from matplotlib.figure import Figure

    from physplot_gui.app.main_window import MainWindow

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    window = MainWindow()
    editor = window._open_figure_editor(Figure())

    assert not editor.windowIcon().isNull()
    assert editor.plugin_menu.title() == "Figure Editor"
    editor.close()
    window.close()


def test_dialog_exec_compat_and_about_dialog_open_and_close():
    from physplot.qt_compat import QtCore
    from physplot_gui.app.main_window import MainWindow

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    box = QtWidgets.QMessageBox()
    QtCore.QTimer.singleShot(50, box.accept)
    assert box.exec_() == QtWidgets.QDialog.DialogCode.Accepted.value

    window = MainWindow()
    closed = []

    def close_about():
        dialog = app.activeModalWidget()
        closed.append(dialog.windowTitle() if dialog else None)
        if dialog:
            dialog.accept()

    QtCore.QTimer.singleShot(100, close_about)
    window.show_about_dialog()
    assert closed == ["About PhysPlot"]
    window.close()
