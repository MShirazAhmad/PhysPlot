"""Startup helper for the modern PhysPlot GUI.

:func:`run_app` is the one function that starts the desktop application. Every launcher
ends up here:

* the ``physplot-gui`` and ``python-physplot-gui`` console commands installed with the
  ``python-physplot`` package (both point at ``physplot_gui.app.runner:run_app``);
* ``python -m physplot_gui`` (see :mod:`physplot_gui.__main__`);
* ``physplot_gui.run_app()`` from Python code.
"""

from __future__ import annotations

import sys

from physplot.qt_compat import QtGui, QtWidgets

from .main_window import LOGO_ICON, MainWindow

_WINDOW = None


def run_app() -> int:
    """Start the PhysPlot GUI, show the main window, and run the Qt event loop.

    1. Reuses the running ``QApplication`` if there is one, otherwise creates it from
       ``sys.argv``.
    2. Sets the application name and display name to ``PhysPlot`` and the organization
       name to ``PhysLab``.
    3. If the PhysPlot logo (``physplot/inc/PhysPlot.png``) exists, sets it as the
       application-wide window icon. This is the icon shown in the macOS Dock and used by
       every window of the application that does not set its own.
    4. Creates the :class:`~physplot_gui.app.main_window.MainWindow`, keeps a module-level
       reference to it so it is not garbage-collected, and shows it.
    5. Runs the event loop until the last window is closed.

    :returns: The event loop's exit code, suitable for ``SystemExit``.
    """
    global _WINDOW
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    app.setApplicationName("PhysPlot")
    app.setApplicationDisplayName("PhysPlot")
    app.setOrganizationName("PhysLab")
    if LOGO_ICON.exists():
        # Application-wide icon: the macOS Dock and every window, including FigureForge.
        app.setWindowIcon(QtGui.QIcon(str(LOGO_ICON)))
    _WINDOW = MainWindow()
    _WINDOW.show()
    return app.exec_()
