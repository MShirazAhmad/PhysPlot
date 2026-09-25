"""Discovery of user-editable plotter modules and plot-type presets.

Plotter modules live in ``config/plotter_modules/`` (user Documents folder
first, then the bundled defaults). A module file can provide any of:

* a ``BasePlotter`` subclass (instances are registered directly),
* a ``PLOTTER``/``PLOTTERS`` list of plotter instances or dictionaries,
* a module-level ``plot(dataset, plot_type=None, config=None)`` function
  together with ``PLOTTER_ID``, ``NAME`` and ``PLOT_TYPES`` constants.

Plot-type presets live in ``config/plot_types/`` as JSON files such as::

    {
      "plotter_id": "basic",
      "plot_type": "scatter_publication",
      "base_plot_type": "scatter",
      "config": {"marker": "o", "grid": true}
    }

They add a named entry to the plotter's plot-type list and merge their
``config`` into the call when that plot type is selected.
"""

from __future__ import annotations

import importlib.util
import inspect
import json
import sys
from pathlib import Path

from physplot.user_paths import plugin_search_dirs

from .base import BasePlotter

MODULE_ID = "physplot.plotting_modules.user_modules"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-09-25-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"


class CallablePlotter(BasePlotter):
    """Adapter that exposes a plain ``plot`` function as a plotter module."""

    def __init__(self, plotter_id, name, function, plot_types=(), category="User", dataset_types=("*",), source=None):
        self.plotter_id = str(plotter_id)
        self.name = str(name)
        self.category = str(category)
        self.supported_plot_types = tuple(plot_types)
        self.supported_dataset_types = tuple(dataset_types)
        self.source = source
        self._function = function

    def plot(self, dataset, plot_type=None, config=None):
        return self._function(dataset, plot_type=plot_type, config=dict(config or {}))


def discover_plotter_module_files() -> list[Path]:
    return _plugin_files(plugin_search_dirs("plotter_modules"), suffix=".py")


def load_user_plotters() -> list[BasePlotter]:
    """Instantiate every plotter defined in the plotter-module folders."""
    plotters = []
    for path in discover_plotter_module_files():
        module = _load_module(path, f"physplot_config_plotter_modules.{path.stem}")
        if module is None:
            continue
        for plotter in _plotters_from_module(module, path):
            plotters.append(plotter)
    return plotters


def discover_plot_type_files() -> list[Path]:
    return _plugin_files(plugin_search_dirs("plot_types"), suffix=".json")


def load_plot_type_presets() -> list[dict]:
    """Return normalized plot-type presets from the plot-type folders."""
    presets = []
    for path in discover_plot_type_files():
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            print(f"Skipping plot type preset {path}: {exc}", file=sys.stderr)
            continue
        entries = payload if isinstance(payload, list) else [payload]
        for entry in entries:
            preset = _normalize_preset(entry, path)
            if preset is not None:
                presets.append(preset)
    return presets


def _normalize_preset(entry, path: Path) -> dict | None:
    if not isinstance(entry, dict):
        return None
    plotter_id = entry.get("plotter_id") or entry.get("plotter")
    plot_type = entry.get("plot_type") or entry.get("name") or path.stem
    if not plotter_id or not plot_type:
        return None
    return {
        "plotter_id": str(plotter_id),
        "plot_type": str(plot_type),
        "base_plot_type": entry.get("base_plot_type"),
        "config": dict(entry.get("config") or {}),
        "description": entry.get("description", ""),
        "path": path,
    }


def _plotters_from_module(module, path: Path) -> list[BasePlotter]:
    plotters: list[BasePlotter] = []
    declared = getattr(module, "PLOTTERS", None)
    if declared is None and getattr(module, "PLOTTER", None) is not None:
        declared = [module.PLOTTER]
    if callable(declared) and not isinstance(declared, (list, tuple)):
        declared = declared()
    if declared:
        for raw in declared:
            plotter = _plotter_from_entry(module, raw, path)
            if plotter is not None:
                plotters.append(plotter)
        return plotters

    for _, candidate in inspect.getmembers(module, inspect.isclass):
        if issubclass(candidate, BasePlotter) and candidate is not BasePlotter and candidate.__module__ == module.__name__:
            plotters.append(candidate())
    if plotters:
        return plotters

    function = getattr(module, "plot", None)
    if callable(function):
        plotter = _plotter_from_entry(module, {"function": function}, path)
        if plotter is not None:
            plotters.append(plotter)
    return plotters


def _plotter_from_entry(module, raw, path: Path) -> BasePlotter | None:
    if isinstance(raw, BasePlotter):
        return raw
    if inspect.isclass(raw) and issubclass(raw, BasePlotter):
        return raw()
    if callable(raw):
        raw = {"function": raw, "plotter_id": getattr(raw, "__name__", path.stem)}
    if not isinstance(raw, dict):
        return None
    function = raw.get("function") or raw.get("callable") or raw.get("plot")
    if isinstance(function, str):
        function = getattr(module, function, None)
    if not callable(function):
        return None
    plotter_id = raw.get("plotter_id") or raw.get("id") or getattr(module, "PLOTTER_ID", None) or path.stem
    name = raw.get("name") or getattr(module, "NAME", None) or getattr(module, "DISPLAY_NAME", None) or str(plotter_id).replace("_", " ").title()
    plot_types = raw.get("plot_types") or raw.get("protocols") or getattr(module, "PLOT_TYPES", None) or ["default"]
    category = raw.get("category") or getattr(module, "CATEGORY", "User")
    dataset_types = raw.get("dataset_types") or getattr(module, "DATASET_TYPES", ("*",))
    return CallablePlotter(plotter_id, name, function, plot_types, category, dataset_types, source=path)


def _plugin_files(folders: list[Path], suffix: str) -> list[Path]:
    paths_by_name = {}
    for folder in folders:
        if not folder.exists():
            continue
        for path in sorted(folder.glob(f"*{suffix}")):
            if path.name.startswith(".") or path.name == "__init__.py":
                continue
            paths_by_name.setdefault(path.name, path)
    return sorted(paths_by_name.values(), key=lambda path: path.stem)


def _load_module(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as exc:  # user code: never crash discovery
        print(f"Skipping plotter module {path}: {exc}", file=sys.stderr)
        return None
    return module
