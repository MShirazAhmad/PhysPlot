"""Startup helper for the modern PhysPlot GUI."""

from __future__ import annotations

import sys

from physplot.qt_compat import QtWidgets

from .main_window import MainWindow

_WINDOW = None


def run_app() -> int:
    global _WINDOW
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    app.setApplicationName("PhysPlot")
    _WINDOW = MainWindow()
    _WINDOW.show()
    return app.exec_()
