"""Workflow step for loading input data."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd

from .base import WorkflowStep

MODULE_ID = "physplot.steps.load_data"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-06-05-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"


class LoadDataStep(WorkflowStep):
    """Load a dataset as the first step of a reusable sequence.

    ``loader`` names a backend loader such as ``"csv"`` or ``"nanoindentation"``.
    ``loader_plugin`` points at a personal file-loader module from ``fileloader/``;
    this keeps exported sequences runnable outside the GUI.
    """

    def __init__(self, path=None, loader="auto", dataset_name=None, loader_plugin=None):
        self.path = path
        self.loader = loader
        self.dataset_name = dataset_name
        self.loader_plugin = loader_plugin

    def apply(self, physplot, allow_column_number_fallback: bool = False):
        """Load from a path, or no-op when a caller already supplied active data."""
        if self.path is None:
            if physplot.dataset is None:
                raise RuntimeError("LoadDataStep has no path and no active dataset is loaded.")
            return physplot.dataset
        if self.loader_plugin:
            module = _load_module(self.loader_plugin)
            loaded = module.load_data(self.path)
            if isinstance(loaded, pd.DataFrame):
                df = loaded.copy()
            else:
                table_data = np.asarray(loaded)
                if table_data.ndim == 1:
                    table_data = table_data.reshape(-1, 1)
                names = _plugin_column_names(module, table_data.shape[1])
                df = pd.DataFrame(table_data, columns=names)
            dataset = physplot.load(df, loader="dataframe", dataset_name=self.dataset_name or Path(str(self.path)).stem)
            dataset.metadata["loader_plugin"] = str(self.loader_plugin)
            return dataset
        return physplot.load(self.path, loader=self.loader, dataset_name=self.dataset_name)

    def to_code(self) -> str:
        return (
            "LoadDataStep(\n"
            f"    path={self.path!r},\n"
            f"    loader={self.loader!r},\n"
            f"    dataset_name={self.dataset_name!r},\n"
            f"    loader_plugin={self.loader_plugin!r},\n"
            ")"
        )


def _load_module(path):
    """Import a personal loader module recorded in a saved sequence file."""
    path = Path(path)
    spec = importlib.util.spec_from_file_location(f"physplot_sequence_loader_{path.stem}", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load file loader plugin from {path}.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _plugin_column_names(module, column_count: int) -> list[str]:
    """Use loader-declared ``COLUMN_NAMES`` when available, then pad defaults."""
    raw_names = getattr(module, "COLUMN_NAMES", None) or getattr(module, "column_names", None)
    if callable(raw_names):
        raw_names = raw_names()
    names = [str(name).strip() for name in (raw_names or []) if str(name).strip()]
    if len(names) < column_count:
        names.extend(f"Column {index}" for index in range(len(names) + 1, column_count + 1))
    return names[:column_count]
