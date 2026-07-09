Class Reference
===============

PhysPlot is both a table-first GUI application and an importable backend
package. The classes below describe the current runtime components most useful
to users and contributors.

Core classes
------------

- ``physplot.PhysPlot``

  Public backend facade for loading data, assigning roles, transforming
  columns, plotting with modules, exporting outputs, and running workflows.

- ``physplot_gui.app.main_window.MainWindow``

  Modern PyQt6 main window. Orchestrates the central table, Simple/Advanced
  panels, protocol menus, Help/About links, and backend API calls.

- ``physplot_gui.widgets.central_table.CentralTable``

  Spreadsheet widget with column-role dropdowns, cell editing, copy/paste,
  rename, row deletion, and column deletion behavior.

- ``physplot.steps.WorkflowStep``

  Base class for replayable workflow steps such as loading data, setting roles,
  transforming columns, calculating formulas, deleting rows/columns, renaming
  columns, editing cells, and generating plot modules.

- ``physplot.plotting_modules.PlotterRegistry``

  Registry for built-in plotter modules and their available plot types.

Autodoc view
------------

.. automodule:: physplot
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. automodule:: physplot_gui.app.main_window
   :members:
   :undoc-members:
   :show-inheritance:
