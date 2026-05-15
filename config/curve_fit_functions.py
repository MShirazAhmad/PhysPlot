"""Editable curve-fit definitions for PhysPlot.

Change ``POLYNOMIAL_DEGREES`` to control the polynomial fit rows in the
configuration dialog. The application expands that list into individual
fit slots automatically.

Input data structure:
    Legacy configuration data are represented as dictionaries with
    ``display_name``, ``default_label``, ``kind``, and either ``degree`` or a
    callable function.

Return type:
    Exposes ``CURVE_FIT_DEFINITIONS``, a list of dictionaries consumed by
    older versions of the configuration dialog.

Optional main/runtime behavior:
    This file is retained for compatibility. The current application discovers
    curve-fitting plugins from the top-level ``curvefitting`` folder.
"""

from __future__ import annotations

import numpy as np


def exponential_decay(x, a, b):
    """exponential_decay(x, a, b) -> numpy.ndarray

    Evaluate the legacy exponential curve-fit model.

    Parameters:
        x (numpy.ndarray): One-dimensional X data array.
        a (float): Amplitude parameter.
        b (float): Exponent parameter.

    Returns:
        numpy.ndarray: Model values ``a * exp(b * x)``.
    """
    return a * np.exp(b * x)


POLYNOMIAL_DEGREES = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]


def polynomial_display_name(degree):
    """polynomial_display_name(degree) -> str

    Build a user-facing label for a polynomial degree.

    Parameters:
        degree (int): Polynomial degree.

    Returns:
        str: Human-readable name such as ``Linear`` or ``4th degree``.
    """
    if degree == 1:
        return "Linear"
    if degree == 2:
        return "Quadratic"
    if degree == 3:
        return "Cubic"
    return f"{degree}th degree"


def polynomial_default_label(degree):
    """polynomial_default_label(degree) -> str

    Return the default legend label for a polynomial fit.

    Parameters:
        degree (int): Polynomial degree.

    Returns:
        str: Default label text.
    """
    return polynomial_display_name(degree)


def _polynomial_definition(degree, index):
    """_polynomial_definition(degree, index) -> dict

    Build a legacy curve-fit definition dictionary for a polynomial.

    Parameters:
        degree (int): Polynomial degree.
        index (int): One-based row index used for legacy widget names.

    Returns:
        dict: Curve-fit metadata consumed by legacy configuration code.
    """
    return {
        "display_name": polynomial_display_name(degree),
        "default_label": polynomial_default_label(degree),
        "kind": "poly",
        "degree": degree,
        "check_box_name": f"checkBox__crvft_{index}",
        "off_radio_name": "radioButton_off_crvft_1" if index == 1 else f"radioButton__off_crvft_{index}",
        "equation_radio_name": f"radioButton_Equation_crvft_{index}",
    }


CURVE_FIT_DEFINITIONS = [
    *[
        _polynomial_definition(degree, index)
        for index, degree in enumerate(POLYNOMIAL_DEGREES, start=1)
    ],
    {
        "display_name": "A*exp(-bx)",
        "default_label": "Ae^(-bx)",
        "kind": "callable",
        "function": exponential_decay,
        "initial_guess": [1.0, 1.0],
        "check_box_name": "checkBox__crvft_11",
        "off_radio_name": "radioButton__off_crvft_11",
        "equation_radio_name": "radioButton_Equation_crvft_11",
    },
]
