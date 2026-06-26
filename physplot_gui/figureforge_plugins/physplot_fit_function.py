"""Figure Editor plugin for fitting arbitrary functions to plotted data."""

from __future__ import annotations

import numpy as np
from matplotlib.axes import Axes
from matplotlib.collections import PathCollection
from matplotlib.lines import Line2D
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
)
from scipy.optimize import curve_fit


class AddFitFunction:
    name = "Add Fit Function"
    tooltip = "Fit a custom function to the selected axes, line, or scatter data."
    submenu = "Fitting"

    def run(self, obj):
        axes = self._axes_for(obj)
        if axes is None:
            self._warn("Select an axes, line, or scatter series before fitting.")
            return

        series = self._series_options(obj, axes)
        if not series:
            self._warn("No visible numeric line or scatter data found to fit.")
            return

        dialog = FitFunctionDialog(series)
        if dialog.exec() != QDialog.Accepted:
            return

        try:
            config = dialog.config()
            x, y = series[config["series_index"]][1], series[config["series_index"]][2]
            params = config["parameters"]
            initial = config["initial"]
            function = self._compile_function(config["expression"], params)
            fit_params, _ = curve_fit(function, x, y, p0=initial, maxfev=10000)
            order = np.argsort(x)
            x_fit = np.linspace(float(np.nanmin(x)), float(np.nanmax(x)), 300)
            if len(np.unique(x[order])) <= 1:
                x_fit = x[order]
            label = config["label"] or self._fit_label(config["expression"], params, fit_params)
            axes.plot(
                x_fit,
                function(x_fit, *fit_params),
                linestyle=config["line_style"],
                linewidth=config["line_width"],
                label=label,
            )
            if config["show_legend"]:
                axes.legend()
        except Exception as exc:
            self._warn(str(exc))

    @staticmethod
    def _axes_for(obj):
        if isinstance(obj, Axes):
            return obj
        if isinstance(obj, (Line2D, PathCollection)):
            return obj.axes
        return None

    def _series_options(self, obj, axes):
        preferred = self._series_from_obj(obj)
        if preferred is not None:
            return [preferred]

        series = []
        for line in axes.lines:
            data = self._series_from_obj(line)
            if data is not None:
                series.append(data)
        for collection in axes.collections:
            data = self._series_from_obj(collection)
            if data is not None:
                series.append(data)
        return series

    @staticmethod
    def _series_from_obj(obj):
        if isinstance(obj, Line2D):
            if not obj.get_visible():
                return None
            x = np.asarray(obj.get_xdata(), dtype=float)
            y = np.asarray(obj.get_ydata(), dtype=float)
            label = obj.get_label() or "Line2D"
        elif isinstance(obj, PathCollection):
            if not obj.get_visible():
                return None
            offsets = np.asarray(obj.get_offsets(), dtype=float)
            if offsets.ndim != 2 or offsets.shape[1] < 2:
                return None
            x = offsets[:, 0]
            y = offsets[:, 1]
            label = obj.get_label() or "Scatter"
        else:
            return None

        mask = np.isfinite(x) & np.isfinite(y)
        x = x[mask]
        y = y[mask]
        if len(x) < 2:
            return None
        return label, x, y

    @staticmethod
    def _compile_function(expression, parameters):
        allowed = {
            "np": np,
            "abs": np.abs,
            "arccos": np.arccos,
            "arcsin": np.arcsin,
            "arctan": np.arctan,
            "cos": np.cos,
            "cosh": np.cosh,
            "exp": np.exp,
            "log": np.log,
            "log10": np.log10,
            "sin": np.sin,
            "sinh": np.sinh,
            "sqrt": np.sqrt,
            "tan": np.tan,
            "tanh": np.tanh,
        }

        def function(x, *values):
            if len(values) != len(parameters):
                raise ValueError("Parameter count does not match initial guesses.")
            local_vars = {"x": x, **dict(zip(parameters, values)), **allowed}
            return eval(expression, {"__builtins__": {}}, local_vars)

        return function

    @staticmethod
    def _fit_label(expression, parameters, values):
        parts = [f"{name}={value:.4g}" for name, value in zip(parameters, values)]
        return f"fit: {expression} ({', '.join(parts)})"

    @staticmethod
    def _warn(message):
        box = QMessageBox()
        box.setIcon(QMessageBox.Warning)
        box.setWindowTitle("Fit Function")
        box.setText("Could not add fit function.")
        box.setInformativeText(message)
        box.exec()


class FitFunctionDialog(QDialog):
    def __init__(self, series):
        super().__init__()
        self.series = series
        self.setWindowTitle("Add Fit Function")

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.series_combo = QComboBox()
        for label, x, y in series:
            self.series_combo.addItem(f"{label} ({len(x)} points)")
        form.addRow("Data:", self.series_combo)

        self.expression = QLineEdit("a*x + b")
        form.addRow("f(x):", self.expression)

        self.parameters = QLineEdit("a,b")
        form.addRow("Parameters:", self.parameters)

        self.initial = QLineEdit("1,0")
        form.addRow("Initial guesses:", self.initial)

        self.label = QLineEdit("")
        form.addRow("Curve label:", self.label)

        self.line_style = QComboBox()
        self.line_style.addItems(["-", "--", "-.", ":"])
        form.addRow("Line style:", self.line_style)

        self.line_width = QLineEdit("2")
        form.addRow("Line width:", self.line_width)

        self.legend = QComboBox()
        self.legend.addItems(["Yes", "No"])
        form.addRow("Show legend:", self.legend)

        layout.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def config(self):
        parameters = [part.strip() for part in self.parameters.text().split(",") if part.strip()]
        if not parameters:
            raise ValueError("Enter at least one parameter name.")
        initial = [float(part.strip()) for part in self.initial.text().split(",") if part.strip()]
        if len(initial) != len(parameters):
            raise ValueError("Initial guesses must match the parameter list.")
        return {
            "series_index": self.series_combo.currentIndex(),
            "expression": self.expression.text().strip(),
            "parameters": parameters,
            "initial": initial,
            "label": self.label.text().strip(),
            "line_style": self.line_style.currentText(),
            "line_width": float(self.line_width.text()),
            "show_legend": self.legend.currentText() == "Yes",
        }


FitFunctionDialog.__module__ = __name__ + "._internal"
