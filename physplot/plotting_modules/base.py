"""Base plotting module interface."""

from __future__ import annotations

MODULE_ID = "physplot.plotting_modules.base"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-06-05-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"


class BasePlotter:
    plotter_id = "base"
    name = "Base Plotter"
    category = "General"
    supported_dataset_types = ("generic",)
    supported_plot_types = ()

    def can_plot(self, dataset) -> bool:
        if dataset is None:
            return True
        if "*" in self.supported_dataset_types:
            return True
        dataset_type = dataset.metadata.get("dataset_type", "generic")
        return dataset_type in self.supported_dataset_types

    def plot(self, dataset, plot_type=None, config=None):
        raise NotImplementedError

    def get_plot_types(self, dataset=None) -> list[str]:
        return list(self.supported_plot_types)
