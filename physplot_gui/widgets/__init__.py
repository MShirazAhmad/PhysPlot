"""Reusable widgets for the PhysPlot GUI.

The widgets here are used by :class:`physplot_gui.app.main_window.MainWindow` to build the
parts of the window that are shared by Simple and Advanced mode:

* :mod:`physplot_gui.widgets.central_table`: :class:`~.central_table.CentralTable`, the
  central spreadsheet with a role dropdown above every column.
* :mod:`physplot_gui.widgets.column_role_header`: ``ROLE_OPTIONS``, the roles offered in
  those dropdowns and what each one means for plotting.
* :mod:`physplot_gui.widgets.mode_switcher`: :class:`~.mode_switcher.ModeSwitcher`, the
  Simple/Advanced buttons on the right of the header.
* :mod:`physplot_gui.widgets.status_bar`: :class:`~.status_bar.PhysPlotStatusBar` and its
  :class:`~.status_bar.ElidedLabel`, the status strip along the bottom of the window.

The widgets hold no scientific logic. They report user actions through Qt signals and the
main window turns those into backend calls and recorded protocol steps. The package itself
imports nothing; import the widgets from their modules.
"""
