"""Discovery of user-editable modules from the Documents config tree."""

from __future__ import annotations

import json

from physplot.plotting_modules import PlotterRegistry
from physplot.workflow import discover_protocol_modules, load_workflow
from physplot.user_paths import writable_plugin_dir


def _user_root(monkeypatch, tmp_path):
    user_root = tmp_path / "PhysPlot"
    monkeypatch.setenv("PHYSPLOT_USER_DIR", str(user_root))
    return user_root


def test_bundled_example_plotter_and_preset_are_registered(monkeypatch, tmp_path):
    _user_root(monkeypatch, tmp_path)
    registry = PlotterRegistry.default()
    assert "example_xy" in registry.plotters
    assert registry.list_plot_types("example_xy") == ["xy_markers", "xy_line"]
    assert "scatter_publication" in registry.list_plot_types("basic")
    base, config = registry.resolve_plot_type("basic", "scatter_publication", {"marker": "x"})
    assert base == "scatter"
    assert config == {"grid": True, "marker": "x"}


def test_user_plotter_module_from_documents_folder(monkeypatch, tmp_path):
    user_root = _user_root(monkeypatch, tmp_path)
    plotter_dir = user_root / "config" / "plotter_modules"
    plotter_dir.mkdir(parents=True)
    (plotter_dir / "lab_plotter.py").write_text(
        "PLOTTER_ID = 'lab'\n"
        "NAME = 'Lab Plotter'\n"
        "PLOT_TYPES = ['quick']\n"
        "def plot(dataset, plot_type=None, config=None):\n"
        "    import matplotlib.pyplot as plt\n"
        "    fig, ax = plt.subplots()\n"
        "    ax.plot(dataset.dataframe.iloc[:, 0])\n"
        "    return fig\n",
        encoding="utf-8",
    )
    registry = PlotterRegistry.default()
    assert registry.get("lab").name == "Lab Plotter"
    assert registry.list_plot_types("lab") == ["quick"]


def test_user_plot_type_preset_overrides_bundled(monkeypatch, tmp_path):
    user_root = _user_root(monkeypatch, tmp_path)
    preset_dir = user_root / "config" / "plot_types"
    preset_dir.mkdir(parents=True)
    (preset_dir / "scatter_publication.json").write_text(
        json.dumps({"plotter_id": "basic", "plot_type": "scatter_publication", "base_plot_type": "line", "config": {"grid": False}}),
        encoding="utf-8",
    )
    registry = PlotterRegistry.default()
    base, config = registry.resolve_plot_type("basic", "scatter_publication")
    assert base == "line"
    assert config == {"grid": False}


def test_protocol_modules_are_discovered_and_loadable(monkeypatch, tmp_path):
    user_root = _user_root(monkeypatch, tmp_path)
    module_dir = user_root / "config" / "protocol_modules"
    module_dir.mkdir(parents=True)
    (module_dir / "my_fragment.py").write_text(
        "from physplot.steps import SetRoleStep\n"
        "DISPLAY_NAME = 'My Fragment'\n"
        "WORKFLOW_STEPS = [SetRoleStep(roles={'x': 'Column 1'})]\n",
        encoding="utf-8",
    )
    entries = {entry["display_name"]: entry for entry in discover_protocol_modules()}
    assert "Normalize Y and Plot" in entries
    assert "My Fragment" in entries
    assert len(load_workflow(entries["My Fragment"]["path"])) == 1
    assert len(load_workflow(entries["Normalize Y and Plot"]["path"])) == 3


def test_templates_and_fit_styles_prefer_user_folder(monkeypatch, tmp_path):
    user_root = _user_root(monkeypatch, tmp_path)
    monkeypatch.delenv("PHYSPLOT_STYLE_DIR", raising=False)
    monkeypatch.delenv("PHYSPLOT_FIT_STYLE_DIR", raising=False)
    from physplot_gui.fit_styles import fit_style_directory, list_fit_style_presets, save_fit_style_preset
    from physplot_gui.plot_styles import list_style_modules, style_directory

    assert style_directory() == user_root / "config" / "templates"
    assert fit_style_directory() == user_root / "config" / "figureforge_fit_styles"
    assert writable_plugin_dir("templates") == user_root / "config" / "templates"

    bundled_names = {entry["name"] for entry in list_style_modules()}
    assert "Publication Style" in bundled_names

    (user_root / "config" / "templates" / "Publication_Style.json").write_text(
        json.dumps({"schema_version": 1, "name": "My Lab Style", "figure": {}, "axes": []}),
        encoding="utf-8",
    )
    names = {entry["name"] for entry in list_style_modules()}
    assert "My Lab Style" in names and "Publication Style" not in names

    saved = save_fit_style_preset({"line_style": ":", "line_width": 1.5}, "Thin Dotted")
    assert saved.parent == user_root / "config" / "figureforge_fit_styles"
    preset_names = {preset["name"] for preset in list_fit_style_presets()}
    assert {"Thin Dotted", "Default LSQ Fit"} <= preset_names
