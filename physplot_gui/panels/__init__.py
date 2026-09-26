"""Provide the mode panels shown under the central table of the PhysPlot GUI.

The PhysPlot main window is table-first: the central spreadsheet fills the
window, and the lower control area shows one of two mode panels, chosen with
the **Simple** / **Advanced** switcher on the right of the header (or
*View > Simple Mode*, ``Ctrl+1``, and *View > Advanced Mode*, ``Ctrl+2``). The
:class:`~physplot_gui.app.mode_manager.ModeManager` creates the panels, stacks
them, sizes the lower area for the active one, and forwards the main window's
refresh calls (columns, protocol rows, tracking state, plotters).

The panels are views only. Each control calls a method of the ``actions``
object passed to the panel, which is the
:class:`~physplot_gui.app.main_window.MainWindow`; the window performs the work
through the backend ``physplot`` package and records it as a replayable
protocol step.

Modules:

:mod:`~physplot_gui.panels.simple_mode_panel`
    :class:`~physplot_gui.panels.simple_mode_panel.SimpleModePanel`, the three
    Simple Mode panels **1. Data Importer**, **2. Mathematical
    Transformation** and **3. Plotter Module**, and
    :class:`~physplot_gui.panels.simple_mode_panel.AutoWidthComboBox`, the
    compact drop-down menu they use.
:mod:`~physplot_gui.panels.advanced_mode_panel`
    :class:`~physplot_gui.panels.advanced_mode_panel.AdvancedModePanel`, the
    Advanced Mode tabs **Build Protocol** and **Run Sequence**.
:mod:`~physplot_gui.panels.recorder_mode_panel`
    :class:`~physplot_gui.panels.recorder_mode_panel.SequenceTablePanel`, the
    protocol table and code editor, and
    :class:`~physplot_gui.panels.recorder_mode_panel.RecorderModePanel`, the
    **Run Sequence** tab.
:mod:`~physplot_gui.panels.bulk_panel`
    :class:`~physplot_gui.panels.bulk_panel.BulkPanel`, the **Bulk Run**
    controls that apply a sequence to every file in a folder.

Each module docstring is a detailed guide to its controls. For the user-facing
tour with screenshots see the *GUI Walkthrough* (``docs/getting_started.rst``
and the wiki page ``wiki/GUI-Walkthrough.md``) and the *UI Reference* wiki
page (``wiki/UI-Reference.md``), which links to one page per panel.
"""
