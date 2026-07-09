"""Discovery helpers for editable GUI plugin folders."""

from __future__ import annotations

import ast
import importlib.util
import sys
from pathlib import Path

from physplot.user_paths import plugin_search_dirs


def discover_functions() -> list[dict]:
    """Find simple transform plugins in ``functions/``.

    A function plugin is any ``.py`` file exposing ``transform(values)``.
    Optional ``DISPLAY_NAME`` controls the label shown in the GUI.
    """
    entries = []
    for path in _plugin_files(plugin_search_dirs("functions")):
        module = _load_module(path, f"physplot_user_function_{path.stem}")
        if module is None:
            continue
        if not hasattr(module, "transform"):
            continue
        display_name = getattr(module, "DISPLAY_NAME", path.stem.replace("_", " ").title())
        entries.append({"display_name": display_name, "path": path, "module": module})
    return entries


def discover_fileloaders() -> list[dict]:
    """Find personal file-loader plugins in ``fileloader/``.

    A loader plugin must expose ``load_data(file_path)``. Optional
    ``COLUMN_NAMES`` and ``DEFAULT_COLUMN_ROLES`` are picked up later by the GUI.
    """
    entries = []
    for path in _plugin_files(plugin_search_dirs("fileloader")):
        module = _load_module(path, f"physplot_user_loader_{path.stem}")
        if module is None:
            continue
        if not hasattr(module, "load_data"):
            continue
        display_name = getattr(module, "title", None) or _loader_title_from_source(path)
        entries.append({"display_name": display_name or path.stem.replace("_", " ").title(), "path": path, "module": module})
    return entries


def discover_loader_plotters(module) -> list[dict]:
    """Return plotters explicitly allowed by a file-loader plugin.

    Loader modules can define ``PLOTTER_MODULES``/``ALLOWED_PLOTTERS`` as a list
    of backend plotter ids, callables, or dictionaries such as:

    ``{"plotter_id": "paper", "name": "Publication Plot", "function": plot}``
    """
    raw_entries = (
        getattr(module, "PLOTTER_MODULES", None)
        or getattr(module, "ALLOWED_PLOTTER_MODULES", None)
        or getattr(module, "ALLOWED_PLOTTERS", None)
        or getattr(module, "PLOTTERS", None)
        or []
    )
    if callable(raw_entries):
        raw_entries = raw_entries()
    entries = []
    for raw_entry in raw_entries:
        entry = _normalize_plotter_entry(module, raw_entry)
        if entry is not None:
            entries.append(entry)
    return entries


def _plugin_files(folders: list[Path]) -> list[Path]:
    paths_by_name = {}
    for folder in folders:
        if not folder.exists():
            continue
        for path in sorted(folder.glob("*.py")):
            if path.name.startswith(".") or path.name == "__init__.py" or not _looks_like_python_source(path):
                continue
            paths_by_name.setdefault(path.name, path)
    return sorted(paths_by_name.values(), key=lambda path: (path.stem != "default_loader", path.stem))


def _load_module(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load plugin from {path}")
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except (ImportError, OSError, SyntaxError, ValueError) as exc:
        print(f"Skipping plugin {path}: {exc}", file=sys.stderr)
        return None
    return module


def _looks_like_python_source(path: Path) -> bool:
    try:
        sample = path.read_bytes()[:4096]
    except OSError:
        return False
    return b"\x00" not in sample


def _normalize_plotter_entry(module, raw_entry) -> dict | None:
    """Normalize loader-declared plotter forms into one GUI-friendly shape."""
    if isinstance(raw_entry, str):
        return {
            "plotter_id": raw_entry,
            "name": raw_entry.replace("_", " ").title(),
            "backend_plotter_id": raw_entry,
            "plot_types": [],
        }
    if callable(raw_entry):
        plotter_id = getattr(raw_entry, "__name__", "custom_plotter")
        return {
            "plotter_id": plotter_id,
            "name": plotter_id.replace("_", " ").title(),
            "callable": raw_entry,
            "plot_types": ["publication_ready"],
        }
    if not isinstance(raw_entry, dict):
        return None
    plotter_id = raw_entry.get("plotter_id") or raw_entry.get("id") or raw_entry.get("name")
    if not plotter_id:
        return None
    function = raw_entry.get("function") or raw_entry.get("callable") or raw_entry.get("plot")
    if isinstance(function, str):
        function = getattr(module, function, None)
    entry = {
        "plotter_id": str(plotter_id),
        "name": raw_entry.get("name") or str(plotter_id).replace("_", " ").title(),
        "plot_types": list(raw_entry.get("plot_types") or raw_entry.get("protocols") or ["publication_ready"]),
        "config": dict(raw_entry.get("config") or {}),
    }
    if callable(function):
        entry["callable"] = function
    else:
        entry["backend_plotter_id"] = raw_entry.get("backend_plotter_id") or str(plotter_id)
    return entry


def _loader_title_from_source(path: Path) -> str | None:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return None
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == "title" for target in node.targets):
            continue
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            return node.value.value
    return None
