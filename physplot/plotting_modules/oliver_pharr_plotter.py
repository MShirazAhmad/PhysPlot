"""Oliver-Pharr visualization module."""

from __future__ import annotations

import matplotlib.pyplot as plt

from .base import BasePlotter
from .nanoindentation_plotter import DEPTH_ALIASES
from .utils import numeric_series, require_columns

MODULE_ID = "physplot.plotting_modules.oliver_pharr_plotter"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-06-05-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"

LOAD_ALIASES = ("Load", "Load mN", "Load (mN)", "P")


class OliverPharrPlotter(BasePlotter):
    plotter_id = "oliver_pharr"
    name = "Oliver-Pharr Plotter"
    category = "Materials Science"
    supported_dataset_types = ("nanoindentation",)
    supported_plot_types = (
        "load_depth_with_unloading_fit",
        "unloading_fit",
        "contact_stiffness_fit",
        "area_function",
        "hardness_summary",
        "modulus_summary",
    )

    def plot(self, dataset, plot_type=None, config=None):
        plot_type = plot_type or "load_depth_with_unloading_fit"
        if plot_type not in self.supported_plot_types:
            raise ValueError(f"Oliver-Pharr Plotter does not support plot type '{plot_type}'.")
        if plot_type in {"hardness_summary", "modulus_summary", "area_function", "contact_stiffness_fit"}:
            return self._metadata_summary(dataset, plot_type)
        return self._load_depth_with_fit(dataset)

    def _load_depth_with_fit(self, dataset):
        columns = require_columns(dataset, self.name, {"Depth": DEPTH_ALIASES, "Load": LOAD_ALIASES})
        fig, ax = plt.subplots()
        ax.plot(numeric_series(dataset, columns["Depth"]), numeric_series(dataset, columns["Load"]), marker="o", label="Data")
        fit = dataset.metadata.get("oliver_pharr_fit")
        if isinstance(fit, dict) and {"depth", "load"} <= set(fit):
            ax.plot(fit["depth"], fit["load"], linestyle="--", label="Unloading fit")
            ax.legend()
        else:
            fig.physplot_warnings = ["No Oliver-Pharr fit metadata available; showing load-depth data only."]
        ax.set_xlabel(columns["Depth"])
        ax.set_ylabel(columns["Load"])
        ax.set_title("Oliver-Pharr Load-Depth")
        fig.tight_layout()
        return fig

    def _metadata_summary(self, dataset, plot_type: str):
        fig, ax = plt.subplots()
        ax.axis("off")
        ax.text(
            0.5,
            0.5,
            f"No Oliver-Pharr {plot_type.replace('_', ' ')} metadata available.",
            ha="center",
            va="center",
            wrap=True,
        )
        fig.physplot_warnings = ["Oliver-Pharr analysis metadata is not available."]
        fig.tight_layout()
        return fig
