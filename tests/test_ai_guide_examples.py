"""The tested examples of the AI guides (``config/*/AI_GUIDE.md``) keep working.

Each guide's worked example is also shipped, switched off, in ``config/<folder>/examples/``
with sample data in ``test_data/AI_Examples/``. These tests check that the shipped files
still match the guides and still work when a user copies them into their config folder.
"""

from __future__ import annotations

import json
import py_compile
import re
import shutil
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config"
DATA = ROOT / "test_data" / "AI_Examples"
EXAMPLES = sorted(path for path in CONFIG.glob("*/examples/*") if path.is_file())


def _guide_blocks(folder: str) -> list[str]:
    text = (CONFIG / folder / "AI_GUIDE.md").read_text(encoding="utf-8")
    section = text.split("## Complete working example", 1)[1].split("\n## ", 1)[0]
    return [body + "\n" for body in re.findall(r"^```(?:python|json)\n(.*?)\n```", section, re.S | re.M)]


@pytest.mark.parametrize("example", EXAMPLES, ids=lambda path: path.name)
def test_example_file_matches_its_guide(example):
    if example.name == "apply_pipeline.py":  # from the guide's "How the user tests it" section
        return
    assert example.read_text(encoding="utf-8") in _guide_blocks(example.parent.parent.name)


@pytest.fixture
def user_config(monkeypatch, tmp_path):
    """Copy every example into a fresh per-user config folder, as a user would."""
    root = tmp_path / "PhysPlot"
    for example in EXAMPLES:
        target = root / "config" / example.parent.parent.name
        target.mkdir(parents=True, exist_ok=True)
        shutil.copy2(example, target / example.name)
    monkeypatch.setenv("PHYSPLOT_USER_DIR", str(root))
    return root / "config"


def test_loader_and_transformation_examples(user_config):
    from physplot import PhysPlot
    from physplot_gui.app.plugin_discovery import discover_fileloaders

    assert "Acme UV-1900 Loader (UV-Vis)" in {entry["display_name"] for entry in discover_fileloaders()}
    pp = PhysPlot()
    pp.load(str(DATA / "methylene_blue.uvs"))  # Auto Loader finds the loader by FILE_EXTENSIONS
    assert list(pp.dataset.dataframe.columns) == ["Wavelength (nm)", "Absorbance", "Absorbance SD"]
    assert pp.dataset.dataframe.shape == (6, 3)

    pp = PhysPlot()
    pp.load(str(DATA / "ftir_wavenumber.csv"))
    pp.transform("Wavenumber", "20_wavenumber_to_wavelength", output="Wavelength (nm)")
    assert pp.dataset.dataframe["Wavelength (nm)"].tolist() == pytest.approx([2500, 5000, 10000])


def test_plotter_and_preset_examples(user_config):
    from matplotlib.figure import Figure

    from physplot import PhysPlot
    from physplot.plotting_modules import PlotterRegistry

    registry = PlotterRegistry.default()
    assert "calibration_curve" in registry.list_plot_types("example_xy")
    pp = PhysPlot()
    pp.load(str(DATA / "anneal_01.csv"))
    pp.set_roles(x="Time (s)", y="Temperature (K)")
    for plot_type in ("normalized", "derivative"):
        assert isinstance(pp.plot_with_module("derivative", plot_type), Figure)


def test_sequence_protocol_module_and_pipeline_examples(user_config, tmp_path):
    from physplot.__main__ import main
    from physplot.workflow import discover_protocol_modules, load_workflow

    sequence = user_config / "sequences" / "uvvis_normalize_sequence.py"
    output = tmp_path / "out"
    assert main(["run-workflow", str(sequence), "--input", str(DATA / "uvvis_spectra" / "sample_A.csv"),
                 "--output", str(output)]) == 0
    assert (output / "plot.png").exists()

    modules = {Path(entry["path"]).name: entry for entry in discover_protocol_modules()}
    assert load_workflow(modules["kelvin_axis_plot.py"]["path"])

    pipeline = json.loads((user_config / "pipelines" / "uvvis_cleanup.json").read_text(encoding="utf-8"))
    assert all({"input", "function", "params", "output"} <= set(entry) for entry in pipeline)


def test_figure_examples(user_config):
    from physplot_gui.fit_styles import list_fit_style_presets
    from physplot_gui.plot_styles import list_style_modules

    assert any(Path(entry["path"]).name == "journal_single_column.json" for entry in list_style_modules())
    assert any(Path(preset["path"]).name == "thin_dashed_fit.json" for preset in list_fit_style_presets())
    for name in ("figureforge_plugins/journal_ticks.py", "fit_functions/20_exp_decay_offset.py"):
        py_compile.compile(str(user_config / name), doraise=True)
