Data Manipulation
=================

For a full step-by-step flow, see :ref:`GUI Walkthrough — Custom Mathematical Function System <gui-custom-mathematical-function-system>`.

Transformation panel
--------------------

Use Simple Mode's **2. Mathematical Transformation** panel to compute values
from one column and write them to another. Every transformation, whether built
in or a plugin, is recorded as a protocol step. It replays with
**Apply This Sequence**, from an exported ``Sequence.py``, from the command line,
and in bulk runs.

.. image:: ../_static/gui_walkthrough/walk_04_transform_configured.png
   :alt: Mathematical Transformation panel
   :width: 700px

Controls
--------

- **Input**: the source column. It is set to the **Y** column whenever new data
  loads; your own choice is kept while you work.
- **Function**: the transformation. Hover over an entry for a description.
- **+ offset**: added to the result (``transform(values) × multiplier + offset``).
- **Output**: a new column name, or an existing column to overwrite.
- **Apply**: runs the transformation and records the step.

Available functions
-------------------

Built-in transforms:

- ``identity``, ``multiply``, ``add``, ``subtract``, ``divide``
- ``normalize_max``: divide by the column's largest absolute value
- ``log`` (natural logarithm), ``log10``
- ``subtract first value``: subtract the column's first value, a single
  constant. This is *not* a background fit; use ``XRD: Baseline Remove`` for that.
  Sequences record it as ``baseline_subtract``.

Plugins from ``config/transformations/``:

- ``x``, ``x^2``, ``x^3``, ``1/x``, ``log10(x)``, ``log(x)``, ``e^x``
- ``cos(x)``, ``sin(x)``, ``tan(x)``, ``arccos(x)``, ``arcsin(x)``, ``arctan(x)``
- ``XRD: Baseline Remove``: fits a smooth background under the peaks
  (asymmetric least squares) and subtracts it. It works on any spectrum.

.. image:: ../_static/gui_walkthrough/walk_03_function_menu.png
   :alt: Function menu
   :width: 700px

Add your own functions as ``.py`` files under ``config/transformations/``, then
choose **File > Reload Config Modules**. See :doc:`../extensions/functions`.
