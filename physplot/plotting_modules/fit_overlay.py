"""Least-squares fit overlays for plotter-module figures."""

from __future__ import annotations

import numpy as np
from scipy.optimize import curve_fit

from .utils import numeric_series, role_column

MODULE_ID = "physplot.plotting_modules.fit_overlay"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-07-08-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"


def apply_lsq_fit_overlay(figure, dataset, config: dict | None):
    """Overlay an arbitrary least-squares fit line on the first axes."""
    fit_config = dict(config or {})
    if not fit_config.get("enabled"):
        return None
    if figure is None or not figure.axes:
        raise ValueError("No plot axes are available for the fitted line.")

    expression = str(fit_config.get("expression") or "a*x + b").strip()
    parameters = _string_list(fit_config.get("parameters") or ["a", "b"])
    initial = [float(value) for value in _string_list(fit_config.get("initial") or [1, 0])]
    if not parameters:
        raise ValueError("Enter at least one LSQ fit parameter.")
    if len(initial) != len(parameters):
        raise ValueError("LSQ initial guesses must match the parameter list.")

    x_col = role_column(dataset, "X")
    y_col = role_column(dataset, "Y")
    x_values = numeric_series(dataset, x_col).to_numpy(dtype=float)
    y_values = numeric_series(dataset, y_col).to_numpy(dtype=float)
    mask = np.isfinite(x_values) & np.isfinite(y_values)
    x_values = x_values[mask]
    y_values = y_values[mask]
    if len(x_values) < len(parameters):
        raise ValueError("Not enough numeric points for the requested LSQ fit.")

    function = compile_lsq_function(expression, parameters)
    fitted, covariance = curve_fit(function, x_values, y_values, p0=initial, maxfev=20000)
    x_fit = np.linspace(float(np.nanmin(x_values)), float(np.nanmax(x_values)), 300)
    if len(np.unique(x_values)) <= 1:
        x_fit = np.sort(x_values)

    axes = figure.axes[0]
    label = str(fit_config.get("label") or "").strip() or _fit_label(expression, parameters, fitted)
    axes.plot(
        x_fit,
        function(x_fit, *fitted),
        linestyle=str(fit_config.get("line_style") or "--"),
        linewidth=float(fit_config.get("line_width") or 2.0),
        label=label,
    )
    if fit_config.get("show_legend", True):
        axes.legend()
    figure.tight_layout()
    return {"parameters": dict(zip(parameters, fitted)), "covariance": covariance}


def compile_lsq_function(expression: str, parameters: list[str]):
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


def _string_list(value) -> list[str]:
    if isinstance(value, str):
        return [part.strip() for part in value.split(",") if part.strip()]
    return [str(part).strip() for part in value if str(part).strip()]


def _fit_label(expression: str, parameters: list[str], values) -> str:
    parts = [f"{name}={value:.4g}" for name, value in zip(parameters, values)]
    return f"LSQ fit: {expression} ({', '.join(parts)})"
