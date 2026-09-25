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


def test_figure_editor_process_gets_the_physplot_icon(monkeypatch):
    import importlib.util
    import subprocess

    from physplot_gui.app.main_window import MainWindow

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    window = MainWindow()
    launched = {}

    class FakeProcess:
        def poll(self):
            return None

    def fake_popen(args, **kwargs):
        launched.update(args=args, env=kwargs["env"])
        return FakeProcess()

    monkeypatch.setattr(importlib.util, "find_spec", lambda name, *a: object() if name == "FigureForge" else None)
    monkeypatch.setattr(MainWindow, "_install_figureforge_plugins", staticmethod(lambda: None))
    monkeypatch.setattr(subprocess, "Popen", fake_popen)
    from matplotlib.figure import Figure

    window._open_figureforge_editor(Figure())

    assert launched["env"]["PHYSPLOT_APP_ICON"] == str(LOGO_ICON)
    assert "setWindowIcon" in launched["args"][2]
    for _, temp_path in window._figureforge_processes:
        temp_path.unlink(missing_ok=True)
    window.close()
