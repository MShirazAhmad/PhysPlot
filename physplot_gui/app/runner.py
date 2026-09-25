"""Startup helper for the modern PhysPlot GUI."""

from __future__ import annotations

import sys

from physplot.qt_compat import QtGui, QtWidgets

from .main_window import LOGO_ICON, MainWindow

_WINDOW = None


def run_app() -> int:
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
