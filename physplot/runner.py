"""Application startup for PhysPlot.

Input data structure:
    Uses ``sys.argv`` from the current Python process. No custom command-line
    options are currently parsed by PhysPlot.

Return type:
    ``run_app`` starts the Qt event loop and returns the integer exit code
    from ``QApplication.exec_()``.

Optional main/runtime behavior:
    Sets the application icon, installs an exception logger, creates the main
    window, centers it, and activates it on macOS when possible.
"""

import os
import platform
import subprocess
import sys
import traceback
from pathlib import Path

_APP = None
_MAIN_WINDOW = None
_UI = None
_LOG_PATH = Path.home() / "PhysPlot-startup.log"
APP_ICON_PATH = Path(__file__).resolve().parent / "inc" / "PhysPlot.png"


def _log(message):
    """_log(message) -> None

    Append a line to the PhysPlot startup log.

    Parameters:
        message (str): Text to append.

    Returns:
        None
    """
    with _LOG_PATH.open("a", encoding="utf-8") as log_file:
        log_file.write(message.rstrip() + "\n")


def _exception_hook(exc_type, exc_value, exc_traceback):
    """_exception_hook(exc_type, exc_value, exc_traceback) -> None

    Log uncaught exceptions before delegating to Python's default hook.

    Parameters:
        exc_type (type): Exception class.
        exc_value (BaseException): Exception instance.
        exc_traceback (traceback): Traceback object.

    Returns:
        None
    """
    _log("Unhandled exception:")
    _log("".join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
    sys.__excepthook__(exc_type, exc_value, exc_traceback)


def _activate_current_process():
    """_activate_current_process() -> None

    Bring the current macOS process to the foreground when possible.

    Parameters:
        None

    Returns:
        None
    """
    if platform.system() != "Darwin":
        return
    script = (
        'tell application "System Events" '
        f'to set frontmost of the first process whose unix id is {os.getpid()} to true'
    )
    try:
        subprocess.run(["osascript", "-e", script], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError:
        pass


def run_app():
    """run_app() -> int

    Create and show the PhysPlot QApplication and main window.

    Parameters:
        None

    Returns:
        int: Qt event-loop exit code.
    """
    global _APP, _MAIN_WINDOW, _UI
    from PyQt5 import QtCore, QtGui, QtWidgets

    sys.excepthook = _exception_hook
    project_root = Path(__file__).resolve().parent.parent
    os.chdir(project_root)
    _log("Starting PhysPlot")
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_DontShowIconsInMenus, False)
    app = QtWidgets.QApplication(sys.argv)
    _APP = app
    app.setApplicationName("PhysPlot")
    app.setWindowIcon(QtGui.QIcon(str(APP_ICON_PATH)))
    app.setQuitOnLastWindowClosed(False)
    app.aboutToQuit.connect(lambda: _log("QApplication aboutToQuit emitted"))
    app.lastWindowClosed.connect(lambda: _log("QApplication lastWindowClosed emitted"))

    from .app import Ui_MainWindow

    main_window = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(main_window)
    _MAIN_WINDOW = main_window
    _UI = ui
    main_window.setAttribute(QtCore.Qt.WA_ShowWithoutActivating, False)
    main_window.setWindowIcon(QtGui.QIcon(str(APP_ICON_PATH)))
    main_window.setWindowState(main_window.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
    main_window.showNormal()
    main_window.show()
    screen = app.primaryScreen()
    if screen is not None:
        frame = main_window.frameGeometry()
        frame.moveCenter(screen.availableGeometry().center())
        main_window.move(frame.topLeft())
    main_window.raise_()
    main_window.activateWindow()
    app.setActiveWindow(main_window)
    _activate_current_process()
    QtCore.QTimer.singleShot(0, main_window.showNormal)
    QtCore.QTimer.singleShot(0, main_window.raise_)
    QtCore.QTimer.singleShot(0, main_window.activateWindow)
    QtCore.QTimer.singleShot(50, _activate_current_process)
    QtCore.QTimer.singleShot(250, main_window.showNormal)
    QtCore.QTimer.singleShot(250, main_window.raise_)
    QtCore.QTimer.singleShot(250, main_window.activateWindow)
    QtCore.QTimer.singleShot(
        100,
        lambda: _log(
            "window visible="
            f"{main_window.isVisible()} minimized={main_window.isMinimized()} "
            f"geometry={main_window.geometry().getRect()}"
        ),
    )
    print(f"PhysPlot GUI launched. Startup log: {_LOG_PATH}", flush=True)

    exit_code = app.exec_()
    _log(f"QApplication exited with code {exit_code}")
    sys.exit(exit_code)
