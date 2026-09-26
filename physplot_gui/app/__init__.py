"""Application objects for the PhysPlot GUI.

This package holds the pieces that start and coordinate the desktop application:

* :mod:`physplot_gui.app.runner`: :func:`~physplot_gui.app.runner.run_app`, which creates
  the ``QApplication``, sets the application name and icon, and shows the main window.
* :mod:`physplot_gui.app.main_window`: ``MainWindow``, which builds the header, the central
  table, the mode panels, the status bar and the native menu bar, and turns every user
  action into backend calls and recorded protocol steps.
* :mod:`physplot_gui.app.gui_state`: :class:`~physplot_gui.app.gui_state.GuiState`, the
  shared state (backend ``PhysPlot`` object, file names, mode and protocol rows) that
  survives mode switches.
* :mod:`physplot_gui.app.mode_manager`: :class:`~physplot_gui.app.mode_manager.ModeManager`,
  which swaps the Simple and Advanced panels below the table and sizes that area.
* :mod:`physplot_gui.app.plugin_discovery`: helpers that find the user's editable loader
  and transformation plugins and the plotters a loader plugin allows.

The package itself imports nothing; import the objects from their modules.
"""
