"""Modern PhysPlot GUI package.

``physplot_gui`` is the PyQt6 desktop front end of PhysPlot, a table-first scientific
plotting application. The GUI is only an orchestration layer: data loading, column roles,
transformations, plotting and the replayable protocol all live in the backend ``physplot``
package, and the GUI calls into it.

.. rubric:: Launching the GUI

Any of these starts the application:

* ``physplot-gui`` or ``python-physplot-gui``, the commands installed with the
  ``python-physplot`` distribution;
* ``python -m physplot_gui`` (see :mod:`physplot_gui.__main__`);
* ``import physplot_gui; physplot_gui.run_app()`` from Python.

.. rubric:: What the user sees

The main window (:class:`physplot_gui.app.main_window.MainWindow`) is laid out top to
bottom as:

1. a header with the LSF and PhysLab logos on the left, the PhysPlot logo in the centre and
   the Simple/Advanced mode switcher on the right;
2. the central spreadsheet (:mod:`physplot_gui.widgets.central_table`), whose first row
   holds a role dropdown for every column;
3. the lower control area (:mod:`physplot_gui.app.mode_manager`): in Simple mode the
   **Data Importer**, **Transformation** and **Plotter Module** panels, in Advanced mode the
   **Build Protocol** and **Run Sequence** tabs;
4. the status bar (:mod:`physplot_gui.widgets.status_bar`).

The native menu bar carries the File, Protocol, View, Plot and Help menus.

.. rubric:: Package layout

* :mod:`physplot_gui.app`: application start-up, the main window, the shared GUI state,
  mode switching and plugin discovery.
* :mod:`physplot_gui.panels`: the Simple and Advanced mode panels.
* :mod:`physplot_gui.widgets`: the central table, mode switcher and status bar.
* :mod:`physplot_gui.style`: the application stylesheet.
* :mod:`physplot_gui.plot_styles` and :mod:`physplot_gui.fit_styles`: reusable figure
  templates and least-squares fit-line style presets.
"""

from __future__ import annotations


def run_app(*args, **kwargs):
    """Start the PhysPlot GUI and return the Qt event loop's exit code.

    A thin wrapper around :func:`physplot_gui.app.runner.run_app`. The runner, and with it
    PyQt6 and the main window, is imported only when this is called, so importing
    ``physplot_gui`` stays cheap. All arguments are passed through unchanged; the current
    runner takes none.

    :returns: The exit code from the event loop.
    """
    from .app.runner import run_app as _run_app

    return _run_app(*args, **kwargs)

__all__ = ["run_app"]
