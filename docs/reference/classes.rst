Class Reference
===============

PhysPlot is primarily a GUI application, not a Python library API. The classes below describe its main runtime components.

Core classes
------------

- ``Ui_MainWindow``

  Main application window. Manages table operations, data import/export, transformations,
  axis role assignment, and plot launch.

- ``Ui_ConfigWindow``

  Plot configuration window. Stores style parameters and curve-fit label/enable settings
  used by the plotting dialog.

- ``Plot_Window``

  Plot dialog containing the matplotlib canvas and toolbar. Renders data/error bars,
  labels, legend, and enabled fit curves.

Support dialogs
---------------

- ``about_gui``

  Shows version/author/license and external links.

- ``pick_file_to_append``

  Opens dataset file-selection dialog and stores selected path.

- ``SaveFile``

  Opens save dialog and writes processed table output to disk.

Autodoc view
------------

.. automodule:: PhysPlot
   :members:
   :undoc-members:
   :show-inheritance:
