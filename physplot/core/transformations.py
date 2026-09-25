"""Column transformations: registered built-ins plus ``config/transformations`` plugins.

Built-in transformations are registered in ``TRANSFORMS``. Any other name is
resolved against the transformation plugin folders returned by
``physplot.user_paths.plugin_search_dirs("transformations")`` (the editable
``Documents/PhysPlot/config/transformations`` first, then the bundled
``config/transformations``). A plugin is a ``.py`` file defining
``transform(values)`` and, optionally, ``DISPLAY_NAME``. It is matched by file
stem (``"02_square"``) first, then by ``DISPLAY_NAME`` (``"x^2"``), so a sequence
that records a plugin transformation replays headlessly with no GUI imports.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from physplot.user_paths import plugin_search_dirs

MODULE_ID = "physplot.core.transformations"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-09-25-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"


def normalize_max(series: pd.Series) -> pd.Series:
    maximum = series.abs().max()
    if maximum == 0 or pd.isna(maximum):
        return series.astype(float)
    return series / maximum


def multiply(series: pd.Series, factor=1) -> pd.Series:
    return series * factor


def add(series: pd.Series, value=0) -> pd.Series:
    return series + value


def subtract(series: pd.Series, value=0) -> pd.Series:
    return series - value


def divide(series: pd.Series, divisor=1) -> pd.Series:
    return series / divisor


def log(series: pd.Series) -> pd.Series:
    return np.log(series)


def log10(series: pd.Series) -> pd.Series:
    return np.log10(series)


def baseline_subtract(series: pd.Series, baseline=None) -> pd.Series:
    if baseline is None:
        baseline = series.iloc[0] if len(series) else 0
    return series - baseline


TRANSFORMS = {
    "normalize_max": normalize_max,
    "multiply": multiply,
    "add": add,
    "subtract": subtract,
    "divide": divide,
    "log": log,
    "log10": log10,
    "baseline_subtract": baseline_subtract,
}


def list_transforms() -> list[str]:
    return list(TRANSFORMS)


def get_transform(name: str):
    """Return a registered transformation, falling back to plugin transformations.

    Plugin transformations are wrapped as ``f(series, multiplier=1.0,
    offset=0.0, **params)`` returning ``transform(values, **params) *
    multiplier + offset``, which matches the Simple Mode controls.
    """
    if name in TRANSFORMS:
        return TRANSFORMS[name]
    entry = find_plugin_transform(name)
    if entry is None:
        raise ValueError(f"Unknown transformation '{name}'.")
    return _plugin_callable(entry)


def discover_plugin_transforms() -> list[dict]:
    """Return every usable plugin in the transformation folders.

    Each entry has ``name`` (the file stem, which is what sequences record),
    ``display_name``, ``path`` and the loaded ``module``. A user file overrides
    a bundled file with the same name. Plugins that fail to import, lack
    ``transform``, or reuse a built-in transformation name are skipped with a
    message on stderr.
    """
    entries = []
    for path in _plugin_files():
        entry = _plugin_entry(path)
        if entry is not None:
            entries.append(entry)
    return entries


def find_plugin_transform(name: str) -> dict | None:
    """Resolve a plugin transformation by file stem, then by ``DISPLAY_NAME``."""
    name = str(name)
    paths = _plugin_files()
    for path in paths:
        if path.stem == name:
            return _plugin_entry(path, raise_errors=True)
    for path in paths:
        entry = _plugin_entry(path)
        if entry is not None and entry["display_name"] == name:
            return entry
    return None


def _plugin_callable(entry: dict):
    module = entry["module"]
    name = entry["name"]

    def apply_plugin(series: pd.Series, multiplier=1.0, offset=0.0, **params) -> pd.Series:
        values = pd.to_numeric(series, errors="coerce").to_numpy(dtype=float)
        result = np.asarray(module.transform(values, **params), dtype=float)
        if result.ndim == 0:
            result = np.full(values.shape, float(result))
        if result.shape != values.shape:
            raise ValueError(
                f"Transformation '{name}' returned {result.size} values for a column of {values.size} rows."
            )
        return pd.Series(result * multiplier + offset, index=series.index)

    apply_plugin.__name__ = name
    return apply_plugin


def _plugin_files() -> list[Path]:
    paths_by_name = {}
    for folder in plugin_search_dirs("transformations"):
        if not folder.is_dir():
            continue
        for path in sorted(folder.glob("*.py")):
            if path.name.startswith(".") or path.name == "__init__.py" or not _looks_like_python_source(path):
                continue
            paths_by_name.setdefault(path.name, path)
    return sorted(paths_by_name.values(), key=lambda path: path.stem)


def _plugin_entry(path: Path, raise_errors: bool = False) -> dict | None:
    try:
        if path.stem in TRANSFORMS:
            raise ValueError(f"'{path.stem}' is a built-in transformation name; rename the file.")
        module = _load_plugin_module(path)
        if not callable(getattr(module, "transform", None)):
            raise AttributeError(f"{path.name} must define transform(values).")
    except Exception as exc:  # user code: never crash discovery
        if raise_errors:
            raise
        print(f"Skipping transformation plugin {path}: {exc}", file=sys.stderr)
        return None
    display_name = getattr(module, "DISPLAY_NAME", None) or path.stem.replace("_", " ").title()
    return {"name": path.stem, "display_name": str(display_name), "path": path, "module": module}


def _load_plugin_module(path: Path):
    spec = importlib.util.spec_from_file_location(f"physplot_config_transformations.{path.stem}", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load transformation plugin from {path}.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _looks_like_python_source(path: Path) -> bool:
    try:
        sample = path.read_bytes()[:4096]
    except OSError:
        return False
    return b"\x00" not in sample
