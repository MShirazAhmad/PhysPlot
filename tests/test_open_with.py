import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PyQt6")

from physplot.qt_compat import QtWidgets
from physplot_gui.app.main_window import MainWindow, data_file_extensions
from physplot_gui.app.runner import _command_line_files


APP = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


def _window(monkeypatch):
    window = MainWindow()
    monkeypatch.setattr(window, "_open_figure_editor", lambda figure, canvas=None: None)
    errors = []
    monkeypatch.setattr(window, "_error", lambda title, exc: errors.append((title, exc)))
    return window, errors


def test_open_and_plot_loads_and_plots_xy_file(tmp_path, monkeypatch):
    data = tmp_path / "scan.csv"
    data.write_text("x,y\n1,2\n2,4\n3,6\n")
    window, errors = _window(monkeypatch)
    plotted = []
    monkeypatch.setattr(window, "generate_plot", lambda: plotted.append(True))

    window.open_and_plot(data)

    assert not errors
    assert window.state.current_file == data
    assert len(window.state.dataframe) == 3
    assert {"X", "Y"} <= set(window.state.roles.values())
    assert plotted


def test_open_and_plot_reports_unreadable_file(tmp_path, monkeypatch):
    window, errors = _window(monkeypatch)
    window.open_and_plot(tmp_path / "missing.csv")
    assert errors and errors[0][0] == "Import failed"


def test_command_line_files_skip_flags_and_missing(tmp_path):
    data = tmp_path / "a.csv"
    data.write_text("x,y\n1,2\n")
    assert _command_line_files(["prog", "-psn_0_123", str(data), str(tmp_path / "nope.csv")]) == [str(data)]


def test_data_file_extensions_include_plugins():
    extensions = data_file_extensions()
    assert extensions[0] == ".csv"
    assert ".ras" in extensions and ".jdx" in extensions


def test_plots_open_in_plot_window_with_advanced_styling_button(tmp_path, monkeypatch):
    data = tmp_path / "scan.csv"
    data.write_text("x,y\n1,2\n2,4\n3,6\n")
    window, errors = _window(monkeypatch)
    sent = []
    monkeypatch.setattr(window, "_open_figure_editor", lambda figure, canvas=None: sent.append(figure))

    window.open_and_plot(data)

    assert not errors
    dialog = window._module_plot_dialogs[-1]
    button = next(b for b in dialog.findChildren(QtWidgets.QPushButton) if "Advanced Styling" in b.text())
    button.click()
    assert len(sent) == 1


def test_figure_editor_is_the_bundled_copy_and_loads_physplot_plugins_in_place(monkeypatch):
    from physplot_gui.app.main_window import FIGURE_EDITOR_PACKAGE_DIR, figure_editor_version

    assert (FIGURE_EDITOR_PACKAGE_DIR / "LICENSE").exists()
    assert figure_editor_version() == "0.3.3"
    window, _ = _window(monkeypatch)
    monkeypatch.undo()  # use the real _open_figure_editor
    from matplotlib.figure import Figure

    editor = window._open_figure_editor(Figure())
    plugin_names = []

    def walk(menu):
        for action in menu.actions():
            if action.menu():
                walk(action.menu())
            else:
                plugin_names.append(action.text())

    walk(editor.plugin_menu)
    assert "Add Fit Function" in plugin_names and "Save as Template" in plugin_names
    assert not list((FIGURE_EDITOR_PACKAGE_DIR / "plugins").glob("physplot_*.py"))
    editor.close()


def test_figure_editor_edits_the_plot_window_figure_live_and_gives_it_back(tmp_path, monkeypatch):
    data = tmp_path / "scan.csv"
    data.write_text("x,y\n1,2\n2,4\n3,6\n")
    window, errors = _window(monkeypatch)
    monkeypatch.undo()
    window.open_and_plot(data)
    assert not errors
    dialog = window._module_plot_dialogs[-1]
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

    plot_canvas = dialog.findChildren(FigureCanvasQTAgg)[0]
    figure = plot_canvas.figure
    button = next(b for b in dialog.findChildren(QtWidgets.QPushButton) if "Advanced Styling" in b.text())

    button.click()
    editor = window._figure_editors[id(figure)]
    assert editor.fm.figure is figure  # same object, not a copy
    assert editor.tab_widget.tabBarAutoHide()  # no "New Figure" tab for a single figure
    button.click()
    assert len(window._figure_editors) == 1  # second click raises the same editor

    redraws = []
    original_draw = plot_canvas.draw
    monkeypatch.setattr(plot_canvas, "draw", lambda: (redraws.append(1), original_draw()))
    figure.axes[0].set_title("Edited in the Figure Editor")
    editor.fm.canvas.draw()
    assert len(redraws) == 1  # the plot window followed the edit, once (no redraw loop)
    assert figure.axes[0].get_title() == "Edited in the Figure Editor"

    editor.close()
    APP.processEvents()
    QtWidgets.QApplication.sendPostedEvents(None, 0)
    APP.processEvents()
    assert figure.canvas is plot_canvas
    assert id(figure) not in window._figure_editors


def test_right_click_on_the_figure_opens_the_part_under_the_mouse(monkeypatch):
    import matplotlib.pyplot as plt
    from matplotlib.backend_bases import MouseEvent

    window, _ = _window(monkeypatch)
    monkeypatch.undo()
    figure, axes = plt.subplots()
    (line,) = axes.plot([0, 1], [0, 1], label="data", linewidth=6)
    axes.set_xlabel("Angle")
    editor = window._open_figure_editor(figure)
    fm = editor.fm
    fm.canvas.draw()

    def event_at(artist_xy):
        x, y = axes.transData.transform(artist_xy)
        return MouseEvent("button_press_event", fm.canvas, x, y, button=3)

    parts = fm.artists_at(event_at((0.5, 0.5)))
    assert parts[0] is line and axes in parts and parts[-1] is figure
    assert fm.describe_artist(line) == "Line – data"

    bbox = axes.xaxis.label.get_window_extent()
    label_event = MouseEvent("button_press_event", fm.canvas, bbox.x0 + bbox.width / 2, bbox.y0 + bbox.height / 2, button=3)
    assert fm.artists_at(label_event)[0] is axes.xaxis.label
    assert fm.describe_artist(axes.xaxis.label) == 'X label "Angle"'

    fm.on_canvas_press(event_at((0.5, 0.5)))
    assert fm.selected_obj is line
    assert fm.fe.tree.currentItem().reference is line

    axes.set_title("Scan")
    fm.canvas.draw()
    bbox = axes.title.get_window_extent()
    fm.on_canvas_press(MouseEvent("button_press_event", fm.canvas, bbox.x0 + bbox.width / 2, bbox.y0 + bbox.height / 2, button=1))
    assert fm.selected_obj is axes.title  # a single click on the title opens the title
    editor.close()
    plt.close(figure)


def test_clicking_the_same_spot_again_cycles_through_overlapping_parts(monkeypatch):
    import matplotlib.pyplot as plt
    from matplotlib.backend_bases import MouseEvent

    window, _ = _window(monkeypatch)
    monkeypatch.undo()
    figure, axes = plt.subplots()
    raw = axes.scatter([0, 0.5, 1], [0, 0.5, 1], s=200, label="raw")
    (fit,) = axes.plot([0, 1], [0, 1], label="fit", linewidth=6)
    editor = window._open_figure_editor(figure)
    fm = editor.fm
    fm.canvas.draw()
    messages = []
    fm.selectionMessage.connect(messages.append)
    x, y = axes.transData.transform((0.5, 0.5))

    def click(dx=0):
        fm.on_canvas_press(MouseEvent("button_press_event", fm.canvas, x + dx, y, button=1))
        return fm.selected_obj

    parts = fm.artists_at(MouseEvent("button_press_event", fm.canvas, x, y, button=1))
    assert parts[:2] == [fit, raw]  # the fit line is drawn above the data, so it comes first
    assert [click() for _ in range(len(parts) + 1)] == parts + [fit]  # cycles, then wraps
    assert messages[0].startswith("Line – fit (1 of ")
    assert messages[1].startswith("Scatter – raw (2 of ")
    assert editor.statusBar().currentMessage() == messages[-1]

    click()  # now on the second part
    far_x, far_y = axes.transData.transform((0.9, 0.1))
    fm.on_canvas_press(MouseEvent("button_press_event", fm.canvas, far_x, far_y, button=1))
    click()
    assert fm.selected_obj is fit  # a click elsewhere in between starts again from the top
    editor.close()
    plt.close(figure)


def test_editor_has_physplot_identity_readable_names_and_export_options(tmp_path, monkeypatch):
    import json

    import matplotlib.pyplot as plt

    from physplot_gui.figure_editor.dialogs.physplot_export import render_export
    from physplot_gui.plot_styles import save_style_module

    window, _ = _window(monkeypatch)
    monkeypatch.undo()
    figure, axes = plt.subplots()
    axes.scatter([1, 2], [3, 4], label="raw")
    axes.set_title("Intensity vs Angle")
    axes.set_xlabel("Angle")
    editor = window._open_figure_editor(figure)

    menus = [action.text() for action in editor.menuBar().actions()]
    texts = " ".join(
        a.text() for m in editor.menuBar().actions() if m.menu() for a in m.menu().actions()
    )
    assert "FigureForge" not in editor.windowTitle() + texts
    assert "Export Figure..." in texts and "Export Style..." in texts
    assert menus[-1] == "Help"

    names = []
    stack = [editor.fe.tree.topLevelItem(0)]
    while stack:
        item = stack.pop()
        names.append(item.text(0))
        stack.extend(item.child(i) for i in range(item.childCount()))
    assert 'Title "Intensity vs Angle"' in names and 'X label "Angle"' in names
    assert "Scatter – raw" in names and "Left spine" in names
    assert not any("_physplot" in name or "_child" in name or "Text(" in name for name in names)

    # Property Inspector: Property | Value, no Type column
    editor.fm.select_artist(axes.title)
    header = [editor.pi.content_layout.itemAtPosition(0, c) for c in range(3)]
    assert [h.widget().text() for h in header if h] == ["Property", "Value"]

    # Export in another format with another template, without touching the figure
    template = save_style_module(figure, "Big Title", tmp_path / "big.json")
    payload = json.loads(template.read_text())
    payload["axes"][0]["title"]["fontsize"] = 30.0
    template.write_text(json.dumps(payload))
    out = render_export(figure, tmp_path / "out.png", "pdf", 150, (4, 3), True, str(template))
    assert out.suffix == ".pdf" and out.read_bytes()[:4] == b"%PDF"
    assert axes.title.get_fontsize() != 30.0  # the on-screen figure is unchanged

    editor.close()
    plt.close(figure)


def test_advanced_figure_editor_tick_box_opens_plots_straight_in_the_editor(tmp_path, monkeypatch):
    from physplot.qt_compat import QtCore

    data = tmp_path / "scan.csv"
    data.write_text("x,y\n1,2\n2,4\n3,6\n")
    window, errors = _window(monkeypatch)
    monkeypatch.undo()
    saved = {}
    monkeypatch.setattr(QtCore.QSettings, "setValue", lambda self, key, value: saved.__setitem__(key, value))
    checkbox = window.mode_manager.panels["Simple"].advanced_editor
    assert not checkbox.isChecked() and not window.open_in_figure_editor

    checkbox.setChecked(True)
    assert window.open_in_figure_editor and saved["plot/open_in_figure_editor"] is True
    window.open_and_plot(data)
    assert not errors
    assert len(window._figure_editors) == 1  # opened straight in the editor
    assert not getattr(window, "_module_plot_dialogs", [])  # no simple plot window

    checkbox.setChecked(False)
    window.open_and_plot(data)
    assert len(window._module_plot_dialogs) == 1  # simple plot window again
    for editor in list(window._figure_editors.values()):
        editor.close()


def test_property_inspector_shows_current_numbers(monkeypatch):
    import matplotlib.pyplot as plt

    from physplot_gui.figure_editor.widgets.custom_spinbox import SpinBox

    window, _ = _window(monkeypatch)
    monkeypatch.undo()
    figure, axes = plt.subplots()
    (line,) = axes.plot([0, 1], [0, 1], linewidth=3.5)
    editor = window._open_figure_editor(figure)
    editor.fm.select_artist(line)
    values = [w.value() for w in editor.pi.content_widget.findChildren(SpinBox)]
    assert 3.5 in values
    assert line.get_linewidth() == 3.5  # showing the value did not change the figure
    editor.close()
    plt.close(figure)


def test_click_guide_explains_cycling(monkeypatch):
    import matplotlib.pyplot as plt
    from matplotlib.backend_bases import MouseEvent

    window, _ = _window(monkeypatch)
    monkeypatch.undo()
    figure, axes = plt.subplots()
    axes.scatter([0.5], [0.5], s=400, label="raw")
    axes.plot([0, 1], [0, 1], label="fit", linewidth=6)
    editor = window._open_figure_editor(figure)
    assert "click the same spot again" in editor.click_guide.text()
    editor.fm.canvas.draw()
    x, y = axes.transData.transform((0.5, 0.5))
    editor.fm.on_canvas_press(MouseEvent("button_press_event", editor.fm.canvas, x, y, button=1))
    assert "Selected:" in editor.click_guide.text() and "Line – fit" in editor.click_guide.text()
    assert "next part" in editor.click_guide.text()
    editor.close()
    plt.close(figure)
