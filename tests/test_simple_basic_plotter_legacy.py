import os
from pathlib import Path

import pandas as pd
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PyQt6")

from physplot.qt_compat import QtWidgets
from physplot_gui.plot_styles import apply_style_module, save_style_module
from physplot_gui.app.main_window import MainWindow


def test_basic_plotter_generate_opens_figureforge_editor(monkeypatch):
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    window = MainWindow()
    window.state.load_dataframe(pd.DataFrame({"Time": [0, 1], "Voltage": [1.0, 2.0]}), name="sample")
    window.state.pp.set_roles(x="Time", y="Voltage")
    window.central_table.set_dataframe(window.state.dataframe, window.state.roles)

    calls = {"figureforge": 0, "module": 0}
    monkeypatch.setattr(window, "_open_figureforge_editor", lambda figure: calls.__setitem__("figureforge", calls["figureforge"] + 1))
    monkeypatch.setattr(window, "_show_module_figure", lambda *args: calls.__setitem__("module", calls["module"] + 1))

    window.generate_module_plot("basic", "scatter")

    assert calls == {"figureforge": 1, "module": 0}
    assert window.state.timeline[-1]["details"] == "Create basic scatter"
    app.processEvents()


def test_figureforge_editor_prepares_missing_editable_artists():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    window = MainWindow()
    window.state.load_dataframe(pd.DataFrame({"Time": [0, 1], "Voltage": [1.0, 2.0]}), name="sample")
    window.state.pp.set_roles(x="Time", y="Voltage")
    figure = window.state.pp.plot_with_module("basic", "scatter", record=False)

    window._prepare_figureforge_figure(figure)
    class_names = set()

    def collect(obj):
        class_names.add(obj.__class__.__name__)
        if hasattr(obj, "get_children"):
            for child in obj.get_children():
                collect(child)

    collect(figure)

    assert {"Annotation", "Legend", "Line2D", "PathCollection"}.issubset(class_names)
    assert figure.axes[0].get_legend() is not None
    window.close()
    app.processEvents()


def test_style_module_can_be_saved_and_applied(tmp_path, monkeypatch):
    monkeypatch.setenv("PHYSPLOT_STYLE_DIR", str(tmp_path))
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    window = MainWindow()
    window.state.load_dataframe(pd.DataFrame({"Time": [0, 1], "Voltage": [1.0, 2.0]}), name="sample")
    window.state.pp.set_roles(x="Time", y="Voltage")
    source = window.state.pp.plot_with_module("basic", "scatter", record=False)
    source.axes[0].set_facecolor("#eeeeee")
    source.axes[0].collections[0].set_facecolor("#ff0000")

    style_path = save_style_module(source, "Red Scatter")
    target = window.state.pp.plot_with_module("basic", "scatter", record=False)
    apply_style_module(target, style_path)

    assert style_path.exists()
    assert window.style_module_entries()[1]["name"] == "Red Scatter"
    assert target.axes[0].get_facecolor()[:3] == pytest.approx((0.933333, 0.933333, 0.933333), abs=1e-5)
    assert target.axes[0].collections[0].get_facecolors()[0][:3] == pytest.approx((1.0, 0.0, 0.0))
    window.close()
    app.processEvents()


def test_style_selection_survives_simple_mode_refresh(tmp_path, monkeypatch):
    monkeypatch.setenv("PHYSPLOT_STYLE_DIR", str(tmp_path))
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    window = MainWindow()
    window.state.load_dataframe(pd.DataFrame({"Time": [0, 1], "Voltage": [1.0, 2.0]}), name="sample")
    window.state.pp.set_roles(x="Time", y="Voltage")
    figure = window.state.pp.plot_with_module("basic", "scatter", record=False)
    style_path = str(save_style_module(figure, "Keep Selected"))
    panel = window.mode_manager.panels["Simple"]
    panel.refresh_styles()
    panel.style_module.setCurrentIndex(panel.style_module.findData(style_path))

    window._refresh_all()

    assert panel.current_style_module() == style_path
    window.close()
    app.processEvents()


def test_figureforge_template_plugin_menu_name():
    plugin_source = Path("physplot_gui/figureforge_plugins/physplot_save_style_module.py").read_text(encoding="utf-8")
    assert 'name = "Save as Template"' in plugin_source


def test_style_module_applies_legend_title_to_unlabeled_scatter(tmp_path, monkeypatch):
    monkeypatch.setenv("PHYSPLOT_STYLE_DIR", str(tmp_path))
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    window = MainWindow()
    window.state.load_dataframe(pd.DataFrame({"Time": [0, 1], "Voltage": [1.0, 2.0]}), name="sample")
    window.state.pp.set_roles(x="Time", y="Voltage")
    source = window.state.pp.plot_with_module("basic", "scatter", record=False)
    source.axes[0].legend([], [], title="Styled Legend")
    style_path = save_style_module(source, "Legend Style")
    target = window.state.pp.plot_with_module("basic", "scatter", record=False)

    apply_style_module(target, style_path)

    legend = target.axes[0].get_legend()
    assert legend is not None
    assert legend.get_visible()
    assert legend.get_title().get_text() == "Styled Legend"
    window.close()
    app.processEvents()


def test_blank_simple_transform_is_status_noop(monkeypatch):
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    window = MainWindow()

    warnings = []
    monkeypatch.setattr(QtWidgets.QMessageBox, "warning", lambda *args: warnings.append(args))

    window.apply_backend_transform("Column 1", "identity", 1.0, 0.0, "Column 2")

    assert warnings == []
    assert window.state.transformations == []
    assert window.status.status.text() == "Status: Enter or import data before applying a transformation"
    window.close()
    app.processEvents()
