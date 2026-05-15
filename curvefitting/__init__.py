"""Editable curve-fitting plugins for PhysPlot.

Each curve-fitting file should define:
- DISPLAY_NAME: text shown in the configuration window
- DEFAULT_LABEL: default legend label
- KIND: "poly" or "callable"
- LABEL_MODES: allowed legend-label modes, usually ["Off", "Equation", "Custom"]

For polynomial fits, also define DEGREE.
For callable fits, define function(x, ...), and optionally INITIAL_GUESS.

Input data structure:
    Curve-fitting plugins consume the active plot's one-dimensional X and Y
    arrays. Polynomial plugins declare metadata only; callable plugins expose
    a model function compatible with scipy.optimize.curve_fit.

Return type:
    Package marker module; plugin files declare metadata or callable model
    functions and do not produce output when imported.

Optional main/runtime behavior:
    Files in this package are discovered dynamically by PhysPlot. They are not
    intended to be executed directly.
"""
