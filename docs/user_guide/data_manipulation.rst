Data Manipulation
=================

For a full step-by-step flow, see :ref:`GUI Walkthrough — Custom Mathematical Function System <gui-custom-mathematical-function-system>`.

Transformation panel
--------------------

Use Simple Mode's **Apply Mathematical Transformation** panel to compute values
from one column and write them to another. Transformations are recorded as
workflow steps and can be replayed through **Build Protocol** or headless CLI
workflows.

Inputs
------

- **Input Col.**: source column
- **Output Col.**: destination column
- **Function**: selected transformation
- **Offset**: optional value added after the selected function is applied

Supported functions
-------------------

- ``x``
- ``x^2``
- ``x^3``
- ``1/x``
- ``log10(x)``
- ``log(x)``
- ``e^x``
- ``cos(x)``, ``sin(x)``, ``tan(x)``
- ``arccos(x)``, ``arsin(x)``, ``artan(x)``

Additional functions can be added as ``.py`` files under ``functions/`` and
are discovered when PhysPlot starts.

.. image:: ../_static/gui_walkthrough/07_custom_function_transform_system.png
   :alt: Mathematical transformation controls
   :width: 700px
