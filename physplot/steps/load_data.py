"""Workflow step for loading input data."""

from __future__ import annotations

from pathlib import Path

from physplot.loaders.plugins import load_plugin_module, plugin_dataframe

from .base import WorkflowStep

MODULE_ID = "physplot.steps.load_data"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-09-25-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"


class LoadDataStep(WorkflowStep):
    """Load a dataset as the first step of a reusable sequence.

    ``loader`` names a backend loader such as ``"csv"`` or ``"nanoindentation"``.
    ``loader_plugin`` points at a personal file-loader module from ``config/data_importers/``;
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
            module = load_plugin_module(self.loader_plugin)
            df = plugin_dataframe(module, module.load_data(self.path))
            dataset = physplot.load(df, loader="dataframe", dataset_name=self.dataset_name or Path(str(self.path)).stem)
            dataset.metadata["loader_plugin"] = str(self.loader_plugin)
            return dataset
        return physplot.load(self.path, loader=self.loader, dataset_name=self.dataset_name)

    def for_path(self, path) -> "LoadDataStep":
        """Return this load step pointed at another file, keeping loader and plugin."""
        return LoadDataStep(
            path=str(path),
            loader=self.loader,
            dataset_name=Path(str(path)).stem,
            loader_plugin=self.loader_plugin,
        )

    def to_code(self) -> str:
        return (
            "LoadDataStep(\n"
            f"    path={self.path!r},\n"
            f"    loader={self.loader!r},\n"
            f"    dataset_name={self.dataset_name!r},\n"
            f"    loader_plugin={self.loader_plugin!r},\n"
            ")"
        )


def load_input(physplot, path, steps, loader="auto") -> list:
    """Load ``path`` the way ``steps`` loads data and return the remaining steps.

    A personal loader plugin recorded in the sequence's ``LoadDataStep`` is
    reused for the new file, so sequences built on plugin formats (e.g. Rigaku
    ``.ras``) run headlessly and in bulk. Otherwise ``loader`` is used.
    """
    template = plugin_load_step(steps)
    if template is not None and loader == "auto":
        template.for_path(path).apply(physplot)
    else:
        physplot.load(path, loader=loader)
    return [step for step in steps if not isinstance(step, LoadDataStep)]


def plugin_load_step(steps):
    """Return the first ``LoadDataStep`` that uses a personal loader plugin, if any."""
    return next((step for step in steps if isinstance(step, LoadDataStep) and step.loader_plugin), None)
