"""Matplotlib plot preview widget."""

from __future__ import annotations

import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from physplot.qt_compat import QtWidgets


class PlotCanvas(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.figure = Figure(figsize=(5.4, 3.0), tight_layout=True)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        self.draw_sample("Single")

    def draw_sample(self, mode: str = "Single") -> None:
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        x = np.linspace(0.1, 11, 24)
        labels = ["Run A (25 C)", "Run B (35 C)", "Run C (45 C)", "Run D (55 C)"]
        for index, label in enumerate(labels):
            y = np.log10(x) - (index * 0.42) + np.sin(x / 3) * 0.08
            ax.plot(x, y, marker="o", markersize=3, linewidth=1.4, label=label)
        ax.set_xlabel("Time [ms]")
        ax.set_ylabel("log(Current [mA])")
        ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.45)
        ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), fontsize=8)
        self.canvas.draw_idle()

    def draw_dataset(self, pp, mode: str = "Single", show_fit: bool = True, show_grid: bool = True) -> None:
        if pp.dataset is None:
            self.draw_sample(mode)
            return
        x_col = self._role_column(pp, "X")
        y_col = self._role_column(pp, "Y")
        if x_col is None or y_col is None:
            self.draw_sample(mode)
            return
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        df = pp.dataset.dataframe
        group_col = self._role_column(pp, "Group")
        if mode in {"Overlay", "Grouped Subplot"} and group_col:
            for label, group in df.groupby(group_col):
                ax.plot(group[x_col], group[y_col], marker="o", linewidth=1.4, markersize=3, label=str(label))
            ax.legend(loc="best", fontsize=8)
        else:
            ax.plot(df[x_col], df[y_col], marker="o", linewidth=1.5, markersize=3)
        if show_fit and pp.fit_result:
            x = df[x_col].astype(float)
            y = pp.fit_result["slope"] * x + pp.fit_result["intercept"]
            ax.plot(x, y, linestyle="--", color="#111827", linewidth=1.2, label="Linear fit")
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.grid(show_grid, linestyle="--", linewidth=0.5, alpha=0.45)
        self.canvas.draw_idle()

    @staticmethod
    def _role_column(pp, role: str) -> str | None:
        for column, column_role in pp.dataset.column_roles.items():
            if column_role == role:
                return column
        return None
