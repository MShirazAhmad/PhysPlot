"""Nanoindentation plotting module."""

from __future__ import annotations

import matplotlib.pyplot as plt

from .base import BasePlotter
from .utils import numeric_series, require_columns

MODULE_ID = "physplot.plotting_modules.nanoindentation_plotter"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-06-05-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"

DEPTH_ALIASES = ("Depth", "Depth nm", "Depth (nm)", "Displacement", "h")
NANO_PLOTS = {
    "load_depth": ("Load", ("Load", "Load mN", "Load (mN)", "P")),
    "hardness_depth": ("Hardness", ("Hardness", "Hardness GPa", "Hardness (GPa)", "H")),
    "modulus_depth": ("Modulus", ("Modulus", "Modulus GPa", "Modulus (GPa)", "E", "Er")),
    "stiffness_depth": ("Stiffness", ("Stiffness", "Stiffness N/m", "Stiffness (N/m)", "S")),
    "contact_depth": ("Contact Depth", ("Contact Depth", "Contact Depth nm", "Contact Depth (nm)", "hc")),
}


class NanoindentationPlotter(BasePlotter):
    plotter_id = "nanoindentation"
    name = "Nanoindentation Plotter"
    category = "Materials Science"
    supported_dataset_types = ("nanoindentation",)
    supported_plot_types = tuple(NANO_PLOTS)

    def plot(self, dataset, plot_type=None, config=None):
        plot_type = plot_type or "load_depth"
        if plot_type not in self.supported_plot_types:
            raise ValueError(f"Nanoindentation Plotter does not support plot type '{plot_type}'.")
        y_label, y_aliases = NANO_PLOTS[plot_type]
        columns = require_columns(dataset, self.name, {"Depth": DEPTH_ALIASES, y_label: y_aliases})
        fig, ax = plt.subplots()
        ax.plot(numeric_series(dataset, columns["Depth"]), numeric_series(dataset, columns[y_label]), marker="o")
        ax.set_xlabel(columns["Depth"])
        ax.set_ylabel(columns[y_label])
        ax.set_title(y_label)
        fig.tight_layout()
        return fig
