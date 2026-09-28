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

from pathlib import Path

from physplot.qt_compat import QtCore, QtGui, QtWidgets

from physplot_gui.style.theme import APP_STYLESHEET

from .main_window import LOGO_ICON, MainWindow

_WINDOW = None


class _FileOpenFilter(QtCore.QObject):
    """Collect macOS *Open With* requests and pass them to the main window.

    Finder sends a file opened with PhysPlot as a ``QFileOpenEvent`` rather than a
    command-line argument, and it can arrive before the window exists, so paths are queued
    until :meth:`attach` is called.
    """

    def __init__(self):
        super().__init__()
        self.window = None
        self.pending: list[str] = []

    def attach(self, window) -> None:
        self.window = window
        for path in self.pending:
            window.open_and_plot(path)
        self.pending.clear()

    def eventFilter(self, obj, event):  # noqa: N802 (Qt name)
        if event.type() == QtCore.QEvent.Type.FileOpen and event.file():
            if self.window is None:
                self.pending.append(event.file())
            else:
                self.window.open_and_plot(event.file())
            return True
        return False


def use_light_theme(app) -> None:
    """Give every PhysPlot window the same light look, whatever the system appearance.

    Qt follows macOS/Windows dark mode by default, so windows that are not children of the
    main window (the Figure Editor, message boxes, file dialogs) would turn dark while the
    main window stays light. The light colour scheme is requested for the whole application
    (Qt 6.8 or newer) and PhysPlot's style sheet is applied application-wide.
    """
    try:
        app.styleHints().setColorScheme(QtCore.Qt.ColorScheme.Light)
    except AttributeError:
        pass  # Qt older than 6.8
    app.setStyleSheet(APP_STYLESHEET)


def _command_line_files(argv) -> list[str]:
    """Return the existing files named on the command line (skipping macOS ``-psn_`` ids)."""
    return [arg for arg in argv[1:] if not arg.startswith("-") and Path(arg).is_file()]


def run_app() -> int:
    """Start the PhysPlot GUI, show the main window, and run the Qt event loop.

    1. On Windows, gives the process its own taskbar identity (app ID ``PhysLab.PhysPlot``)
       so the taskbar shows the PhysPlot logo rather than Python's. Then reuses the running
       ``QApplication`` if there is one, otherwise creates it from ``sys.argv``.
    2. Sets the application name and display name to ``PhysPlot`` and the organization
       name to ``PhysLab``.
    3. If the PhysPlot logo (``physplot/inc/PhysPlot.png``) exists, sets it as the
       application-wide window icon. This is the icon shown in the macOS Dock and used by
       every window of the application that does not set its own.
    4. Creates the :class:`~physplot_gui.app.main_window.MainWindow`, keeps a module-level
       reference to it so it is not garbage-collected, and shows it.
    5. Opens and plots any data file named on the command line or sent by macOS Finder
       (*Open With > PhysPlot*), see :meth:`MainWindow.open_and_plot`.
    6. Runs the event loop until the last window is closed.

    :returns: The event loop's exit code, suitable for ``SystemExit``.
    """
    global _WINDOW
    if sys.platform == "win32":
        # PhysPlot runs inside pythonw.exe; without an app ID of its own, Windows groups it
        # with Python and shows Python's icon on the taskbar instead of PhysPlot's.
        try:
            import ctypes

            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("PhysLab.PhysPlot")
        except (AttributeError, OSError):
            pass
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    app.setApplicationName("PhysPlot")
    app.setApplicationDisplayName("PhysPlot")
    app.setOrganizationName("PhysLab")
    use_light_theme(app)
    if LOGO_ICON.exists():
        # Application-wide icon: the macOS Dock and every window, including FigureForge.
        app.setWindowIcon(QtGui.QIcon(str(LOGO_ICON)))
    file_open_filter = _FileOpenFilter()
    app.installEventFilter(file_open_filter)
    _WINDOW = MainWindow()
    remembered = QtCore.QSettings("PhysLab", "PhysPlot").value("plot/open_in_figure_editor", False)
    if str(remembered).lower() in ("true", "1"):
        _WINDOW.open_in_figure_editor = True
        checkbox = getattr(_WINDOW.mode_manager.panels.get("Simple"), "advanced_editor", None)
        if checkbox is not None:
            checkbox.setChecked(True)
    _WINDOW.show()
    # Files from the command line (Windows/Linux *Open With*, or ``physplot-gui data.csv``)
    # and macOS open requests are loaded once the event loop is running.
    pending = _command_line_files(sys.argv)

    def open_pending():
        for path in pending:
            _WINDOW.open_and_plot(path)
        file_open_filter.attach(_WINDOW)

    QtCore.QTimer.singleShot(0, open_pending)
    return app.exec_()
