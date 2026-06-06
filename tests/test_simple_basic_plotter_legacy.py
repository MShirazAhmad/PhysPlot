import os

import pandas as pd
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PyQt6")

from physplot.qt_compat import QtWidgets
from physplot_gui.app.main_window import MainWindow


def test_basic_plotter_generate_opens_legacy_formatter(monkeypatch):
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    window = MainWindow()
    window.state.load_dataframe(pd.DataFrame({"Time": [0, 1], "Voltage": [1.0, 2.0]}), name="sample")
    window.state.pp.set_roles(x="Time", y="Voltage")
    window.central_table.set_dataframe(window.state.dataframe, window.state.roles)

    calls = {"legacy": 0, "module": 0}
    monkeypatch.setattr(window, "_open_legacy_plot_windows", lambda: calls.__setitem__("legacy", calls["legacy"] + 1))
    monkeypatch.setattr(window, "_show_module_figure", lambda *args: calls.__setitem__("module", calls["module"] + 1))

    window.generate_module_plot("basic", "scatter")

    assert calls == {"legacy": 1, "module": 0}
    assert window.state.timeline[-1]["details"] == "Create basic scatter"
    app.processEvents()
