"""Personal loader plugins from ``config/data_importers`` for the backend.

A loader plugin defines ``load_data(file_path)`` returning a DataFrame or 2D
table, and optionally ``COLUMN_NAMES``, ``DEFAULT_COLUMN_ROLES`` and
``FILE_EXTENSIONS`` (e.g. ``[".ras"]``). Auto Loader uses the first plugin
that declares a file's extension when no built-in loader handles it, so such
files load the same way in the GUI, in replayed sequences and in bulk runs.
"""

from __future__ import annotations

import ast
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd

from physplot.user_paths import plugin_search_dirs

from .base import BaseLoader

MODULE_ID = "physplot.loaders.plugins"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-09-25-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"

ROLE_NAMES = {
    "x": "X",
    "x-axis": "X",
    "y": "Y",
    "y-axis": "Y",
    "x error": "X Error",
    "x-error": "X Error",
    "y error": "Y Error",
    "y-error": "Y Error",
    "group": "Group",
    "label": "Label",
}


class PluginLoader(BaseLoader):
    """Adapter that loads a file through a personal loader plugin."""

    loader_id = "plugin"
    file_format = "plugin"

    def __init__(self, plugin_path):
        self.plugin_path = Path(plugin_path)
        self.module = load_plugin_module(self.plugin_path)
        self.name = str(getattr(self.module, "title", None) or self.plugin_path.stem)

    def read_dataframe(self, path: Path) -> pd.DataFrame:
        return plugin_dataframe(self.module, self.module.load_data(path))

    def dataset_from_dataframe(self, df, dataset_name, source_path=None):
        dataset = super().dataset_from_dataframe(df, dataset_name, source_path=source_path)
        dataset.metadata["loader_plugin"] = str(self.plugin_path)
        roles = getattr(self.module, "DEFAULT_COLUMN_ROLES", None) or []
        for column, role in zip(dataset.dataframe.columns, roles):
            dataset.column_metadata[column]["suggested_role"] = ROLE_NAMES.get(str(role).strip().lower(), str(role).strip())
        return dataset


def plugin_loader_for_suffix(suffix: str) -> PluginLoader | None:
    """Return a loader for the first plugin whose ``FILE_EXTENSIONS`` include ``suffix``."""
    suffix = suffix.lower()
    for path in _plugin_files():
        if suffix in _declared_extensions(path):
            return PluginLoader(path)
    return None


def plugin_extensions() -> set[str]:
    """Return every extension declared by an installed loader plugin."""
    extensions = set()
    for path in _plugin_files():
        extensions.update(_declared_extensions(path))
    return extensions


def load_plugin_module(path):
    """Import a loader plugin module from ``path``."""
    path = Path(path)
    spec = importlib.util.spec_from_file_location(f"physplot_config_data_importers.{path.stem}", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load file loader plugin from {path}.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def plugin_dataframe(module, loaded) -> pd.DataFrame:
    """Turn a plugin's ``load_data`` result into a DataFrame with its column names."""
    if isinstance(loaded, pd.DataFrame):
        return loaded.copy()
    table = np.asarray(loaded)
    if table.ndim == 1:
        table = table.reshape(-1, 1)
    if table.ndim != 2:
        raise ValueError("Loader plugins must return a 2D table.")
    return pd.DataFrame(table, columns=plugin_column_names(module, table.shape[1]))


def plugin_column_names(module, column_count: int) -> list[str]:
    """Use loader-declared ``COLUMN_NAMES`` when available, then pad defaults."""
    raw_names = getattr(module, "COLUMN_NAMES", None) or getattr(module, "column_names", None)
    if callable(raw_names):
        raw_names = raw_names()
    names = [str(name).strip() for name in (raw_names or []) if str(name).strip()]
    if len(names) < column_count:
        names.extend(f"Column {index}" for index in range(len(names) + 1, column_count + 1))
    return names[:column_count]


def _plugin_files() -> list[Path]:
    paths_by_name = {}
    for folder in plugin_search_dirs("data_importers"):
        if not folder.is_dir():
            continue
        for path in sorted(folder.glob("*.py")):
            if not path.name.startswith((".", "__")):
                paths_by_name.setdefault(path.name, path)
    return [paths_by_name[name] for name in sorted(paths_by_name)]


def _declared_extensions(path: Path) -> set[str]:
    """Read ``FILE_EXTENSIONS`` without importing the plugin."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
    except (OSError, SyntaxError, ValueError):
        return set()
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "FILE_EXTENSIONS" for target in node.targets
        ):
            try:
                values = ast.literal_eval(node.value)
            except ValueError:
                return set()
            values = [values] if isinstance(values, str) else values
            return {"." + str(value).lower().lstrip(".") for value in values}
    return set()
