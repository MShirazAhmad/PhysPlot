"""Entry point for the modern PhysPlot GUI.

Running the package as a module starts the desktop application::

    python -m physplot_gui

This calls :func:`physplot_gui.app.runner.run_app` and exits with the Qt event loop's exit
code once the window is closed. It is equivalent to the installed ``physplot-gui`` (or
``python-physplot-gui``) command. The macOS app bundle and the Windows Start menu shortcut
created by the one-command installers in ``scripts/`` also launch PhysPlot this way.

For local GUI work on macOS the project guide recommends a Python 3.12 virtual environment,
for example ``.gui-venv/bin/python -m physplot_gui``; set ``QT_QPA_PLATFORM=offscreen`` to
run it without a display (smoke checks).
"""

from physplot_gui.app.runner import run_app


if __name__ == "__main__":
    raise SystemExit(run_app())
