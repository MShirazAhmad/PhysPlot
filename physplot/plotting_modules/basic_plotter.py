"""Basic plotting module: X/Y plots and every Matplotlib plot type."""

from __future__ import annotations

import warnings

import matplotlib.pyplot as plt

from .base import BasePlotter
from .gallery import PLOT_CATEGORIES, PLOT_TYPE_IDS, draw

MODULE_ID = "physplot.plotting_modules.basic_plotter"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-06-05-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"


class BasicPlotter(BasePlotter):
    """X/Y plots plus every Matplotlib plot type (see :mod:`.gallery`).

    ``plot_categories`` groups the plot types like the Matplotlib gallery, so the GUI can
    offer a Category menu and a Plot Type menu. ``scatter``, ``line`` and ``scatter_line``
    keep their original ids, so saved sequences replay unchanged.
    """

    plotter_id = "basic"
    name = "Basic Plotter"
    category = "General"
    supported_dataset_types = ("*",)
    supported_plot_types = PLOT_TYPE_IDS
    plot_categories = PLOT_CATEGORIES

    def plot(self, dataset, plot_type=None, config=None):
        plot_type = plot_type or self.supported_plot_types[0]  # "line" for the Line Plotter subclass
        if plot_type not in self.supported_plot_types:
            raise ValueError(f"{self.name} does not support plot type '{plot_type}'.")
        fig = plt.figure()
        draw(fig, dataset, plot_type)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)  # gridspec layouts (scatter_hist)
            fig.tight_layout()
        return fig
