"""Shared plotting constants for PhysPlot.

The user-facing labels and option lists are loaded from ``config/ui_config.json``.

Input data structure:
    Reads ``config/ui_config.json`` as a JSON object containing UI option
    arrays and plot-label defaults.

Return type:
    Exposes dictionaries and lists such as ``MARKERS``, ``LINESTYLES``,
    ``COLORS``, and ``PLOT_LABEL_DEFAULTS`` for use by the GUI.

Optional main/runtime behavior:
    Imported by the application at startup; not intended to be run directly.
"""

import json
from pathlib import Path

_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "ui_config.json"
with _CONFIG_PATH.open(encoding="utf-8") as config_file:
    UI_CONFIG = json.load(config_file)

MARKERS = {
    "Point": ".",
    "Pixel": ",",
    "Circle": "o",
    "Triangle-Down": "v",
    "Triangle-Up": "^",
    "Triangle-Left": "<",
    "Triangle-Right": ">",
    "Tri-Down": "1",
    "Tri-Up": "2",
    "Tri-Left": "3",
    "Tri-Right": "4",
    "Octagon": "8",
    "Square": "s",
    "Pentagon": "p",
    "Star": "*",
    "Hexagon1": "h",
    "Hexagon2": "H",
    "Plus": "+",
    "x": "x",
    "Diamond": "D",
    "Thin-Diamond": "d",
    "V-Line": "|",
    "H-Line": "_",
    "Draw Nothing": "None",
}

LINESTYLES = {
    "Solid Line": "-",
    "Dashed Line": "--",
    "Dash-Dotted Line": "-.",
    "Dotted Line": ":",
    "Draw Nothing": "None",
}

COLORS = {
    "Blue": "b",
    "Green": "g",
    "Red": "r",
    "Cyan": "c",
    "Magenta": "m",
    "Yellow": "y",
    "Black": "k",
    "White": "w",
}

AXIS_ROLE_OPTIONS = UI_CONFIG["axis_role_options"]
GRID_STYLE_OPTIONS = UI_CONFIG["grid_styles"]
GRID_COLOR_OPTIONS = UI_CONFIG["grid_colors"]
MARKER_STYLE_OPTIONS = UI_CONFIG["marker_styles"]
MARKER_COLOR_OPTIONS = UI_CONFIG["marker_colors"]
LINE_STYLE_OPTIONS = UI_CONFIG["line_styles"]
LINE_COLOR_OPTIONS = UI_CONFIG["line_colors"]
SCALE_X_OPTIONS = UI_CONFIG["scale_x_options"]
PLOT_LABEL_DEFAULTS = UI_CONFIG["plot_label_defaults"]
CURVE_FIT_LABEL_MODES = UI_CONFIG["curve_fit_label_modes"]
