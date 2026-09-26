"""Build and run the PhysPlot main window: table, mode panels, menus and status bar.

This module defines :class:`MainWindow`, the main window of the PyQt6 desktop GUI, the helper
:func:`figureforge_plugin_dirs` and a few module constants. The function ``run_app`` in
:mod:`physplot_gui.app.runner` (used by ``python -m physplot_gui`` and by the
``physplot-gui`` / ``python-physplot-gui`` entry points) creates the ``QApplication``, builds
one ``MainWindow`` and shows it.

The window is an orchestration layer only. It owns the widgets, reacts to what the user does and
forwards every scientific operation to the backend :class:`physplot.PhysPlot` object kept in
``self.state.pp``. Loading, transforming, plotting, exporting and sequence replay all happen in
the ``physplot`` package; this module calls the backend, redraws the table from the backend
dataset and records the user's actions as rows of the protocol, most of them linked to
replayable backend steps.

The user documentation pages "GUI Walkthrough" and "UI Reference" in the project wiki
(``wiki/``), and the Read the Docs walkthrough (``docs/getting_started.rst``), describe the same
window from the user's point of view.

.. rubric:: Window layout

:meth:`MainWindow._build_ui` stacks the parts of the window from top to bottom::

    +--------------------------------------------------------------------------------------+
    | File   Protocol   View   Plot   Help                               (native menu bar) |
    +--------------------------------------------------------------------------------------+
    | [LSF] [PhysLab]           [  PhysPlot wide logo  ]         Mode: [Simple] [Advanced] |
    +--------------------------------------------------------------------------------------+
    |      |  Column 1  |  2: Time   |  3: Volts  | ...   <- headers: number and name      |
    |      | [Ignore v] | [X      v] | [Y      v] | ...   <- role dropdown row             |
    |    1 |            |    0.0     |    1.2     |                                        |
    |    2 |            |    0.5     |    1.9     |       central spreadsheet table        |
    |   .. |            |            |            |       (CentralTable, spare height)     |
    +--------------------------------------------------------------------------------------+
    | Lower mode panel (QStackedWidget owned by ModeManager)                               |
    |   Simple:   [1. Data Importer] [2. Mathematical Transformation] [3. Plotter Module]  |
    |   Advanced: tabs [Build Protocol] [Run Sequence]                                     |
    +--------------------------------------------------------------------------------------+
    | (o) Status: <last message>   Rows: N   Columns: N   File: <name>   Workflow   Mode   |
    +--------------------------------------------------------------------------------------+

* **Menu bar.** Created with ``QMainWindow.menuBar()``; on macOS Qt shows it in the system menu
  bar at the top of the screen instead of inside the window.
* **Header** (:meth:`MainWindow._header`). The LSF and PhysLab logos sit on the far left, the
  wide PhysPlot logo is centred and the Simple/Advanced switcher
  (:class:`~physplot_gui.widgets.mode_switcher.ModeSwitcher`) is on the right. When the wide
  logo file is missing, a text title "PhysPlot" with the subtitle "Advanced Plotting Made
  Simple" is shown instead. A missing LSF or PhysLab image is simply left out.
* **Central table** (:class:`~physplot_gui.widgets.central_table.CentralTable`). Row 0 holds
  one role dropdown per column (Ignore, X, Y, X Error, Y Error, Group, Label, Batch Key, Fit
  Weight). Data rows are numbered from 1 in the row header. Column headers read ``Column N``
  for default names and ``N: name`` otherwise. Double-click a header to rename the column;
  right-click a header, a row number or a cell for rename, copy, paste, clear and delete. The
  table always shows at least 100 data rows and 26 columns and grows when it is scrolled or
  typed into, so it usually shows more (empty) columns than the dataset has.
* **Lower mode panel** (:class:`~physplot_gui.app.mode_manager.ModeManager`). Simple Mode shows
  :class:`~physplot_gui.panels.simple_mode_panel.SimpleModePanel` (three panels, sized to
  exactly their height). Advanced Mode shows
  :class:`~physplot_gui.panels.advanced_mode_panel.AdvancedModePanel` with the tabs
  *Build Protocol* and *Run Sequence* (300 to 430 px tall). Simple Mode is shown at start-up.
* **Status bar** (:class:`~physplot_gui.widgets.status_bar.PhysPlotStatusBar`). Shows
  ``Status: <message>`` (long messages are cut with an ellipsis; hover for the full text), the
  row and column counts of the backend dataset and the loaded file name (``File: -`` when
  none). In Advanced Mode it also shows a green dot, ``Workflow: <sequence file name>``
  (``Untitled`` until a sequence is saved or imported) and ``Mode: Advanced``.

.. rubric:: Native menu bar

:meth:`MainWindow._build_menu_bar` creates five menus. Shortcuts are Qt key sequences, so
``Ctrl`` appears as the Command key on macOS.

**File**

* *Import Data...* (``Ctrl+O``): :meth:`MainWindow.import_data` with the Auto Loader. Pick a
  file; it replaces the table and is recorded as a *File Loader* protocol row.
* *Import Folder...*: :meth:`MainWindow.import_folder`. Pick a folder; the status bar reports
  ``Folder selected: <name>``. No data is loaded (folders are processed from Advanced Mode >
  Run Sequence).
* *Export Data...* (``Ctrl+E``): :meth:`MainWindow.export_data`. Pick a folder; the backend
  writes ``data.csv``, ``columns.csv`` and ``workflow.py`` there, plus ``fit.json`` and
  ``plot.png`` when a fit result or a figure exists.
* *Open Config Folder*: opens the per-user ``Documents/PhysPlot/config`` folder (or the
  ``config`` folder under ``PHYSPLOT_USER_DIR`` when that variable is set) in the system file
  manager, creating the folder tree first when it is missing.
* *Reload Config Modules* (``Ctrl+Shift+R``): re-scans the ``config/`` folders without a
  restart. It rebuilds the *Insert Protocol Module* submenu, asks every panel that has a
  ``refresh_plugins`` method (Simple Mode) to rebuild its loader, function, plotter, template
  and fit-style lists, refreshes the window and reports
  ``Reloaded config modules from <folder>``.

**Protocol**

* *Import Sequence.py...*: :meth:`MainWindow.open_workflow`. Replaces the protocol with the
  steps of a sequence file. The steps are not run.
* *Export Sequence.py...* (``Ctrl+S``): :meth:`MainWindow.save_workflow`. Writes the protocol
  as a runnable Python file.
* *Apply This Sequence* (``Ctrl+R``): :meth:`MainWindow.apply_current_sequence`. Replays the
  whole protocol on the table and fills the Status column.
* *Copy Sequence Code*: copies the generated Python of the protocol (the text
  :meth:`physplot.PhysPlot.workflow_script` returns) to the clipboard and reports
  ``Sequence script copied``.
* *Clear Sequence*: empties the protocol rows and the backend step list without asking. The
  table data is left as it is.
* *Insert Protocol Module* (submenu): one item per ``.py`` file found in
  ``config/protocol_modules`` (label from the file's ``DISPLAY_NAME`` or its file name,
  tooltip and status tip from ``DESCRIPTION``). A disabled item "No protocol modules in
  config/protocol_modules" is shown when there are none. Choosing a module appends its steps
  to the end of the protocol without running them and reports
  ``Inserted protocol module <name>``; a module that cannot be loaded is reported as
  "Insert protocol module failed".

**View**

* *Simple Mode* (``Ctrl+1``) and *Advanced Mode* (``Ctrl+2``): switch the lower panel through
  :meth:`physplot_gui.app.mode_manager.ModeManager.set_mode`, exactly like the header
  switcher.

**Plot**

* *Generate Plot* (``Ctrl+G``): :meth:`MainWindow.generate_plot`. A Basic Plotter scatter plot
  of the X and Y role columns, styled with the Template selected in Simple Mode and opened in
  the Figure Editor.
* *Update Integrated Preview*: :meth:`MainWindow.generate_integrated_plot`. Refreshes the
  panels' plotter lists and adds a display-only protocol row.

**Help**

* *Documentation*: opens https://physplot.readthedocs.io/en/latest/ in the default browser.
* *GitHub Repository*: opens https://github.com/MShirazAhmad/PhysPlot.
* *Report Issues or Bugs*: opens https://github.com/MShirazAhmad/PhysPlot/issues.
* *About PhysPlot*: :meth:`MainWindow.show_about_dialog`. The item carries Qt's ``AboutRole``,
  so on macOS Qt moves it into the application menu.

.. rubric:: What the panel controls call

``ModeManager(self)`` hands this window to every panel as its ``actions`` object. The panels call
its public methods directly and read shared data through ``actions.state``:

* Simple Mode, **1. Data Importer**: the *Data Loader* list comes from
  :meth:`MainWindow.backend_loader_entries`; *Import Data* calls :meth:`MainWindow.import_data`
  with the selected entry; *Import Folder* calls :meth:`MainWindow.import_folder`; *Export
  Data* calls :meth:`MainWindow.export_data`.
* Simple Mode, **2. Mathematical Transformation**: the *Function* list comes from
  :meth:`MainWindow.simple_function_entries`; *Apply* calls
  :meth:`MainWindow.apply_backend_transform` with the input column, the function entry, a
  multiplier of ``1.0``, the ``+`` offset and the output column.
* Simple Mode, **3. Plotter Module**: the *Plotter Module*, *Plot Type*, *Template* and *Fit
  Style* lists come from :meth:`MainWindow.plotter_entries`,
  :meth:`MainWindow.plot_type_entries`, :meth:`MainWindow.style_module_entries` and
  :meth:`MainWindow.fit_style_entries`; *Generate Plot* calls
  :meth:`MainWindow.generate_module_plot`; *Export Plot* calls
  :meth:`MainWindow.export_module_plot`.
* Advanced Mode, **Build Protocol**: *Import Sequence.py*, *Export Sequence.py*, *Apply This
  Sequence*, *Copy as Script* and *Clear Sequence* call the same methods as the Protocol menu.
  *Apply Code to Table* calls ``apply_sequence_code`` (it replaces the protocol with the steps
  defined by the edited code, without running them). Each row's *Delete* button calls
  ``delete_timeline_step`` (removes the row's steps, then replays what is left). The row
  context menu item *Rerun from this step* calls :meth:`MainWindow.rerun_from_timeline_step`.
  The *Status* column asks ``timeline_row_status`` for OK / Failed / Skipped and a tooltip,
  and the *Code* view shows ``sequence_code_text``.
* Advanced Mode, **Run Sequence**: the *Browse* buttons call
  :meth:`MainWindow.browse_input_folder`, :meth:`MainWindow.browse_workflow_file` and
  :meth:`MainWindow.browse_output_folder`; *Run Bulk Workflow* calls
  :meth:`MainWindow.run_bulk_workflow`.

Edits in the central table arrive as signals connected in :meth:`MainWindow._build_ui`:
``role_changed`` to :meth:`MainWindow.set_column_role`, ``column_renamed`` to
:meth:`MainWindow.rename_column`, ``cell_value_changed`` to :meth:`MainWindow.record_cell_edit`,
``rows_deleted`` to :meth:`MainWindow.record_row_delete`, ``columns_deleted`` to
:meth:`MainWindow.record_column_delete` and ``table_edited`` to
:meth:`MainWindow.sync_table_to_backend`.

.. rubric:: How actions reach the backend and the protocol

All shared state lives in ``self.state`` (:class:`~physplot_gui.app.gui_state.GuiState`) and
survives mode switches: ``pp`` (the backend), ``timeline`` (protocol rows), ``transformations``
(a display list of applied transformations), ``mode``, ``current_file`` and ``workflow_file``.
Two lists describe the protocol:

``self.state.pp.workflow``
    The ordered backend step objects (``LoadDataStep``, ``SetRoleStep``,
    ``TransformColumnStep``, ``PlotModuleStep``, ``RenameColumnStep``, ``SetCellValueStep``,
    ``DeleteRowsStep``, ``DeleteColumnsStep``, ...). This list is the replayable source of
    truth: *Apply This Sequence*, *Export Sequence.py*, *Copy Sequence Code*, the Build Protocol
    *Code* view and bulk runs all read it.
``self.state.timeline``
    One dict per row of the Build Protocol and Run Sequence tables, with the keys ``action``,
    ``details``, ``target``, ``workflow_index``, ``workflow_indices`` and ``code``.
    ``workflow_indices`` links the row to one or more positions in ``pp.workflow`` (a *File
    Loader* row covers the ``LoadDataStep`` and the ``SetRoleStep`` that follows it). A row
    without indices is display-only and is never replayed.

Every recording goes through :meth:`MainWindow._append_sequence`, in one of three ways:

1. The GUI builds the step object and passes it in; ``_append_sequence`` appends it to
   ``pp.workflow``. Used for imports, role changes, column renames, cell edits and row and
   column deletions.
2. The backend records the step itself (:meth:`physplot.PhysPlot.transform` and
   :meth:`physplot.PhysPlot.plot_with_module` append to ``pp.workflow``); the GUI passes the
   new step's index so the row links to it. Used for transformations and plots.
3. Nothing replayable is recorded: :meth:`MainWindow._record` adds a display-only row (used by
   *Update Integrated Preview*), and plots from loader-declared callable plotters add a row
   without a step.

A typical action, *Apply* in Simple Mode, runs:
:meth:`~MainWindow.apply_backend_transform` -> :meth:`~MainWindow.apply_simple_transform` ->
:meth:`~MainWindow._apply_transform` -> :meth:`~MainWindow.sync_table_to_backend` (table
contents copied into the backend dataset) -> :meth:`physplot.PhysPlot.transform` (adds the
column and records a ``TransformColumnStep``) -> table redrawn from the backend dataframe ->
:meth:`~MainWindow._append_sequence` -> status ``Transformation applied`` ->
:meth:`~MainWindow._refresh_all`.

:meth:`MainWindow._refresh_all` redraws the role dropdowns, the panels' column lists, both
protocol tables (including the Status column), the plotter lists and the status bar counts.
Role changes, cell edits and row or column deletions record their rows without calling it, so
those rows appear in Build Protocol at the next full refresh.

*Apply This Sequence* replays ``pp.workflow`` from its first step through
:meth:`physplot.PhysPlot.run_workflow_detailed` (a ``LoadDataStep`` reads its file from disk
again), redraws the table from the backend dataset and fills the Status column from
``pp.last_results``. The run stops at the first failing step; later steps are marked Skipped
and the table keeps the state reached before the failure. *Rerun from this step* resumes from
a state snapshot saved by an earlier run. *Import Sequence.py*, *Apply Code to Table* and
*Insert Protocol Module* replace or extend the protocol but do not run it.

.. rubric:: Dialogs and status messages

* File dialogs: *Import Data* (the built-in types, loader-plugin types or any file),
  *Import Folder*, *Export Data*, *Export Plot* (PNG, PDF or SVG), *Save Sequence.py* and
  *Load Sequence.py* (starting in the writable ``config/sequences`` folder), *Import Pipeline*
  and *Export Pipeline* (``config/pipelines``) and the Run Sequence folder and file pickers.
  Cancelling a dialog leaves the data and the protocol unchanged.
* Message boxes: *About PhysPlot*, *Fit Results*, *Sequence Manager* and the error warnings
  described below.
* Plot windows: Basic Plotter figures open in the Figure Editor (a separate process); other
  plotter modules open in a non-modal PhysPlot dialog titled
  ``PhysPlot - <plotter>: <plot type>`` with the Matplotlib navigation toolbar.
* Status messages set by this module include ``Ready``, ``Transformation applied``,
  ``Enter or import data before applying a transformation``, ``Plot generated``,
  ``Plot preview updated``, ``Plot exported``, ``Exported``, ``Fit complete``,
  ``Pipeline exported``, ``Sequence saved``, ``Sequence loaded``, ``Sequence complete``,
  ``Sequence updated``, ``Sequence cleared``, ``Sequence code applied``,
  ``Sequence script copied``, ``Reran from row N``, ``Row N has no replayable step``,
  ``Row N failed (<StepName>): <error>``, ``Bulk complete: N outputs``,
  ``Folder selected: <name>``, ``Inserted protocol module <name>`` and
  ``Reloaded config modules from <folder>``. After an error the status bar shows the error
  title (for example ``Import failed``).

.. rubric:: Figure Editor (FigureForge)

Figures from the Basic Plotter open in FigureForge, which the UI calls the "Figure Editor".
:meth:`MainWindow._open_figureforge_editor`:

1. Checks that the ``FigureForge`` package can be imported and otherwise raises a
   ``RuntimeError`` that tells the user to run ``python -m pip install FigureForge``.
2. Copies PhysPlot's Figure Editor plugins (the bundled ``config/figureforge_plugins`` folder,
   then the per-user copy, whose files win) into FigureForge's own ``plugins`` package folder
   and points FigureForge's ``preferences.json`` at that folder.
3. Adds hidden placeholder artists (line, scatter, legend, annotation) to every axes.
4. Pickles the figure to a temporary file and starts ``sys.executable -c <launcher> <file>``
   with :class:`subprocess.Popen`. The launcher script imports PySide6 and FigureForge in that
   new Python process, shows the FigureForge window with its plugin menu renamed "Figure
   Editor", and deletes the temporary file when it exits. The child process gets
   ``PHYSPLOT_STYLE_DIR`` (the folder new templates are written to) and ``PHYSPLOT_APP_ICON``.
5. Returns at once, so PhysPlot stays usable and several editors can be open. About 1.2 s
   later :meth:`MainWindow._check_figureforge_process` checks the process once and reports
   "Figure Editor failed" with the captured error output if it has already exited with a
   non-zero code.

Edits made in the Figure Editor stay in that process: they are not sent back to PhysPlot and
are not recorded in the protocol.

.. rubric:: Bulk runs

*Run Bulk Workflow* on the Run Sequence tab calls :meth:`MainWindow.run_bulk_workflow`, which
passes the chosen sequence file, or a copy of the current protocol when no file is given, to
:meth:`physplot.PhysPlot.run_bulk` (:func:`physplot.bulk.run_folder`). Each matching file of the
input folder is processed in name order with a fresh backend and exported to
``<output folder>/<file stem>/``. The run happens in the GUI thread, so the window does not
respond until it finishes. The first failing file stops the run; the error names it, and
files before it have already been exported.

.. rubric:: Error reporting

Nearly every action method catches exceptions and passes them to :meth:`MainWindow._error`,
which puts the error title in the status bar, stores ``(title, exception)`` in
``MainWindow.last_error`` and then either prints ``<title>: <message>`` to stderr (when the
Qt platform is ``offscreen``, as in headless tests and CI, where no one can dismiss a dialog)
or shows a modal warning box with the title and the exception text. The window stays usable
after an error.

.. rubric:: Module constants

``LOGO_WIDE``, ``LOGO_ICON``, ``LSF_LOGO``, ``PHYSLAB_LOGO``
    Image files in ``physplot/inc``: the centred header logo (``PhysPlotWide1.png``), the
    window icon that is also shown in the About dialog and passed to the Figure Editor
    (``PhysPlot.png``), and the two left header logos (``lsf.jpeg`` and ``physlab.png``).
``FIGUREFORGE_PLUGIN_DIR``
    The bundled ``config/figureforge_plugins`` folder, named in the error raised when no Figure
    Editor plugin folder exists.
``BUILTIN_FUNCTIONS``
    Menu label and tooltip of each built-in transformation in the Simple Mode *Function* list,
    keyed by the backend function name that sequences record.

.. rubric:: Related modules

* :mod:`physplot_gui.app.gui_state`: :class:`~physplot_gui.app.gui_state.GuiState`, the shared
  state holder.
* :mod:`physplot_gui.app.mode_manager`: the lower panel stack and Simple/Advanced switching.
* :mod:`physplot_gui.panels`: the Simple Mode panels, Build Protocol
  (``SequenceTablePanel``), Run Sequence (``RecorderModePanel``) and ``BulkPanel``.
* :mod:`physplot_gui.widgets`: ``CentralTable``, ``ModeSwitcher`` and ``PhysPlotStatusBar``.
* :mod:`physplot_gui.plot_styles`: figure templates in ``config/templates``.
* :mod:`physplot_gui.fit_styles`: LSQ fit-style presets in ``config/figureforge_fit_styles``.
* :mod:`physplot_gui.app.plugin_discovery`: loader plugins, transformation plugins and
  loader-declared plotters.
* :mod:`physplot_gui.style.theme`: ``APP_STYLESHEET``, the window style sheet.
* Backend: :mod:`physplot` (``PhysPlot``), :mod:`physplot.steps`, :mod:`physplot.workflow`,
  :mod:`physplot.execution`, :mod:`physplot.bulk` and :mod:`physplot.user_paths`.
"""

from __future__ import annotations

import importlib.util
import json
import os
import pickle
import shutil
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

from appdirs import user_config_dir
from importlib.metadata import version as package_version
import numpy as np
import pandas as pd
from physplot.qt_compat import QtCore, QtGui, QtWidgets
from physplot.core.transformations import list_transforms
from physplot.loaders import list_loaders
from physplot.loaders.plugins import plugin_extensions
from physplot.plotting_modules import PlotterRegistry
from physplot.user_paths import (
    bundled_plugin_dir,
    ensure_user_physplot_dirs,
    plugin_search_dirs,
    user_physplot_dir,
    writable_plugin_dir,
)
from physplot.execution import STATUS_FAILED, STATUS_OK, STATUS_SKIPPED, first_failure
from physplot.workflow import discover_protocol_modules, load_workflow, load_workflow_source
from physplot.steps import (
    CalculateColumnStep,
    DeleteColumnsStep,
    DeleteRowsStep,
    LoadDataStep,
    PlotModuleStep,
    RenameColumnStep,
    SetCellValueStep,
    SetRoleStep,
    TransformColumnStep,
)

from physplot_gui.app.gui_state import GuiState
from physplot_gui.app.mode_manager import ModeManager
from physplot_gui.app.plugin_discovery import discover_fileloaders, discover_functions, discover_loader_plotters
from physplot_gui.fit_styles import list_fit_style_presets
from physplot_gui.plot_styles import apply_style_module, list_style_modules, style_directory
from physplot_gui.style.theme import APP_STYLESHEET
from physplot_gui.widgets.central_table import CentralTable
from physplot_gui.widgets.mode_switcher import ModeSwitcher
from physplot_gui.widgets.status_bar import PhysPlotStatusBar


LOGO_WIDE = Path(__file__).resolve().parents[2] / "physplot" / "inc" / "PhysPlotWide1.png"
LOGO_ICON = Path(__file__).resolve().parents[2] / "physplot" / "inc" / "PhysPlot.png"
LSF_LOGO = Path(__file__).resolve().parents[2] / "physplot" / "inc" / "lsf.jpeg"
PHYSLAB_LOGO = Path(__file__).resolve().parents[2] / "physplot" / "inc" / "physlab.png"
FIGUREFORGE_PLUGIN_DIR = bundled_plugin_dir("figureforge_plugins")


# Menu labels and descriptions for built-in transformations; sequences keep the
# function names, so relabelling here never breaks saved protocols.
BUILTIN_FUNCTIONS = {
    "identity": ("identity", "Copy the column, plus the offset."),
    "normalize_max": ("normalize_max", "Divide by the column's largest absolute value."),
    "multiply": ("multiply", "Multiply by a factor (edit it in the sequence Code view)."),
    "add": ("add", "Add the offset."),
    "subtract": ("subtract", "Subtract the offset."),
    "divide": ("divide", "Divide by a factor (edit it in the sequence Code view)."),
    "log": ("log", "Natural logarithm (ln)."),
    "log10": ("log10", "Base-10 logarithm."),
    "baseline_subtract": (
        "subtract first value",
        "Subtract the column's first value (one constant). For background removal use XRD: Baseline Remove.",
    ),
}


#: Role labels by the keys ``SetRoleStep`` stores (the inverse of ``MainWindow._role_key``).
ROLE_LABELS = {
    "x": "X",
    "y": "Y",
    "xerr": "X Error",
    "yerr": "Y Error",
    "group": "Group",
    "label": "Label",
    "batch_key": "Batch Key",
    "fit_weight": "Fit Weight",
}


#: File types the built-in loaders read, listed first in the *Import Data* dialog.
BUILT_IN_DATA_EXTENSIONS = [".csv", ".txt", ".dat", ".tsv", ".msa", ".xls", ".xlsx", ".xrdml"]


def data_file_filter() -> str:
    """Return the *Import Data* dialog filter: built-in types plus loader-plugin types.

    Every extension a loader plugin declares in ``FILE_EXTENSIONS`` (for example
    ``.ras`` or ``.jdx``) is added, so a file a plugin can read is listed without
    switching the dialog to *All Files*.

    :returns: A Qt name filter such as ``"Data Files (*.csv ... *.ras);;All Files (*)"``.
    """
    extensions = list(BUILT_IN_DATA_EXTENSIONS)
    extensions += sorted(ext for ext in plugin_extensions() if ext not in extensions)
    return f"Data Files ({' '.join('*' + ext for ext in extensions)});;All Files (*)"


def loader_label(step) -> str:
    """Return the *Data Loader* menu label for a recorded ``LoadDataStep``.

    A loader plugin is named by its ``DISPLAY_NAME`` (matched on the plugin file name, or the
    file name itself when the plugin is missing); a built-in loader by its menu name, for
    example ``"auto"`` becomes "Auto Loader". This is the text a live import records, so rows
    rebuilt from a saved sequence read the same as the rows recorded while working.

    :param step: The ``LoadDataStep``.
    :returns: The loader label.
    """
    if step.loader_plugin:
        stem = Path(str(step.loader_plugin)).stem
        for entry in discover_fileloaders():
            if Path(str(entry.get("path", ""))).stem == stem:
                return entry.get("display_name") or stem
        return stem
    names = {loader.loader_id: loader.name for loader in list_loaders()}
    return names.get(step.loader or "auto", str(step.loader))


def transform_label(function_name: str) -> str:
    """Return the protocol-row text for a transformation, as a live *Apply* records it.

    Built-in transformations keep their backend name (``normalize_max``); a plugin from
    ``config/transformations`` is shown by its ``DISPLAY_NAME`` (``14_xrd_baseline_remove``
    becomes "XRD: Baseline Remove"). An unknown name is returned unchanged.

    :param function_name: The recorded ``function_name``.
    :returns: The row text.
    """
    if function_name in BUILTIN_FUNCTIONS or function_name in list_transforms():
        return function_name
    for entry in discover_functions():
        if entry.get("name") == function_name:
            return entry.get("display_name") or function_name
    return function_name


def plot_details(plotter_id: str, plot_type: str | None, fit_config=None) -> str:
    """Return the *Details* text of a Generate Plot row, for example "Create line line".

    :param plotter_id: The plotter module id.
    :param plot_type: The plot type, or ``None`` for the plotter's default.
    :param fit_config: The step's ``lsq_fit`` settings; an enabled fit adds " with LSQ fit".
    :returns: The row text.
    """
    details = f"Create {plotter_id} {plot_type or ''}".strip()
    if isinstance(fit_config, dict) and fit_config.get("enabled", True):
        details += " with LSQ fit"
    return details


def figureforge_plugin_dirs() -> list[Path]:
    """Return the Figure Editor plugin folders in copy order: bundled first, then per-user.

    :func:`physplot.user_paths.plugin_search_dirs` lists the per-user
    ``Documents/PhysPlot/config/figureforge_plugins`` folder (or the one under
    ``PHYSPLOT_USER_DIR``) before the bundled ``config/figureforge_plugins`` folder. This
    function reverses that order because :meth:`MainWindow._install_figureforge_plugins` copies
    the folders one after another: a per-user plugin file with the same name as a bundled one is
    copied last and so replaces it. Folders are returned whether or not they exist; the caller
    skips missing ones.

    :returns: The plugin folders, bundled folder first.
    """
    return list(reversed(plugin_search_dirs("figureforge_plugins")))


class MainWindow(QtWidgets.QMainWindow):
    """Show the PhysPlot window and route every user action to the backend.

    ``MainWindow`` is the main window of the GUI. See the module documentation above
    for the layout sketch, the complete menu bar and the flow from a click to a recorded
    protocol step.

    **Responsibilities**

    * Build the window: native menu bar, branded header with the mode switcher, the central
      spreadsheet, the lower Simple/Advanced panel stack and the status bar.
    * Act as the ``actions`` object of the panels. ``ModeManager(self)`` passes this window to
      :class:`~physplot_gui.panels.simple_mode_panel.SimpleModePanel` and
      :class:`~physplot_gui.panels.advanced_mode_panel.AdvancedModePanel` (and from there to
      the Build Protocol, Run Sequence and Bulk Run widgets). Those panels call its public
      methods directly, for example :meth:`import_data`, :meth:`apply_backend_transform`,
      :meth:`generate_module_plot`, :meth:`apply_current_sequence` and
      :meth:`run_bulk_workflow`, and fill their dropdowns from the ``*_entries`` methods.
    * Turn each action into calls on the backend :class:`physplot.PhysPlot` (``state.pp``) and
      record it as a protocol step with :meth:`_append_sequence`.
    * Keep every widget in step with the backend after each action (:meth:`_refresh_all`).
    * Open plot windows (the Figure Editor subprocess or an in-app Matplotlib dialog) and
      report errors (:meth:`_error`).

    **Attributes**

    ``state``
        The :class:`~physplot_gui.app.gui_state.GuiState`: the backend ``pp``, the protocol
        rows ``timeline``, the display list ``transformations``, the current ``mode``, the
        loaded data file ``current_file`` and the saved or imported sequence file
        ``workflow_file``.
    ``central_table``
        The :class:`~physplot_gui.widgets.central_table.CentralTable` spreadsheet with the role
        dropdown row.
    ``mode_manager``
        The :class:`~physplot_gui.app.mode_manager.ModeManager`. ``mode_manager.stack`` is the
        lower ``QStackedWidget`` and ``mode_manager.panels`` maps ``"Simple"`` and
        ``"Advanced"`` to the panel widgets.
    ``mode_switcher``
        The :class:`~physplot_gui.widgets.mode_switcher.ModeSwitcher` on the right of the
        header (created by :meth:`_header`).
    ``status``
        The :class:`~physplot_gui.widgets.status_bar.PhysPlotStatusBar` at the bottom.
    ``file_menu``, ``protocol_menu``, ``view_menu``, ``plot_menu``, ``help_menu``
        The ``QMenu`` objects of the native menu bar. ``protocol_modules_menu`` is the
        *Protocol > Insert Protocol Module* submenu.
    ``last_error``
        ``(title, exception)`` of the most recent error passed to :meth:`_error`, or ``None``.
        Tests read it because no dialog is shown on the ``offscreen`` platform.
    ``_active_loader_entry``
        The loader-plugin entry used for the last import, or ``None`` after a built-in loader
        or :meth:`new_table`. Plotters declared by that plugin are added to the Plotter Module
        list by :meth:`plotter_entries`.
    ``_custom_plotters``
        Loader-declared callable plotters by their ``"loader:<id>"`` identifier, rebuilt by
        :meth:`plotter_entries`.

    Attributes created on first use: ``_figureforge_processes`` (running Figure Editor
    processes and their temporary files), ``_module_plot_dialogs`` (open plot dialogs) and, for
    the legacy plot windows, ``plot_config_window``, ``plot_config_ui``, ``plot_window`` and
    ``_main_window``.

    **Signals connected**

    * ``mode_switcher.mode_changed`` to ``mode_manager.set_mode`` (header buttons).
    * ``mode_manager.mode_changed`` to :meth:`_mode_changed`.
    * ``central_table.role_changed`` to :meth:`set_column_role`.
    * ``central_table.column_renamed`` to :meth:`rename_column`.
    * ``central_table.cell_value_changed`` to :meth:`record_cell_edit`.
    * ``central_table.rows_deleted`` to :meth:`record_row_delete`.
    * ``central_table.columns_deleted`` to :meth:`record_column_delete`.
    * ``central_table.table_edited`` to :meth:`sync_table_to_backend`.
    * Each menu action's ``triggered`` signal to its handler (see :meth:`_build_menu_bar`).
    """
    def __init__(self, parent=None):
        """Create the window, its widgets and an empty "Untitled" table.

        Creates a fresh :class:`~physplot_gui.app.gui_state.GuiState`, and with it a new backend
        :class:`physplot.PhysPlot` with an empty sequence. Makes sure the per-user
        ``Documents/PhysPlot/config/<folder>`` tree exists
        (:func:`physplot.user_paths.ensure_user_physplot_dirs`, which skips folders it is not
        allowed to create). Sets the window title "PhysPlot", a 1500 x 900 px size, the
        application style sheet and the PhysPlot window icon (when the image exists). Then it
        builds the UI (:meth:`_build_ui`), loads a blank 17 x 19 table
        (:meth:`_bootstrap_blank_table`) and refreshes every panel (:meth:`_refresh_all`).

        The window is not shown here; :func:`physplot_gui.app.runner.run_app` shows it. Nothing
        is recorded in the protocol.

        :param parent: Optional parent widget, passed on to ``QMainWindow``.
        """
        super().__init__(parent)
        self.state = GuiState()
        self._active_loader_entry = None
        self._custom_plotters: dict[str, dict] = {}
        self.last_error: tuple[str, Exception] | None = None
        ensure_user_physplot_dirs()
        self.setWindowTitle("PhysPlot")
        self.resize(1500, 900)
        self.setStyleSheet(APP_STYLESHEET)
        if LOGO_ICON.exists():
            self.setWindowIcon(QtGui.QIcon(str(LOGO_ICON)))
        self._build_ui()
        self._bootstrap_blank_table()
        self._refresh_all()

    def _build_ui(self) -> None:
        """Assemble the menu bar and the central widget, top to bottom.

        Builds the native menu bar (:meth:`_build_menu_bar`), then a root widget with a vertical
        layout (margins 12/8/12/0 px, spacing 7 px) containing, in order:

        1. The header from :meth:`_header` (logos and mode switcher), followed by a 10 px gap.
           The :class:`~physplot_gui.app.mode_manager.ModeManager` is created just before it,
           with this window as the panels' ``actions`` object, because the header's switcher
           connects to ``mode_manager.set_mode``. ``mode_manager.mode_changed`` is connected to
           :meth:`_mode_changed`.
        2. The :class:`~physplot_gui.widgets.central_table.CentralTable` with stretch factor 1,
           so it takes all spare height. Its signals are connected here: ``role_changed`` to
           :meth:`set_column_role`, ``column_renamed`` to :meth:`rename_column`,
           ``cell_value_changed`` to :meth:`record_cell_edit`, ``rows_deleted`` to
           :meth:`record_row_delete`, ``columns_deleted`` to :meth:`record_column_delete` and
           ``table_edited`` to :meth:`sync_table_to_backend`.
        3. The lower mode panel stack (``mode_manager.stack``) with stretch factor 0; its height
           is set by the mode manager.
        4. The :class:`~physplot_gui.widgets.status_bar.PhysPlotStatusBar` (``self.status``).

        Called once from :meth:`__init__`.
        """
        self._build_menu_bar()
        root = QtWidgets.QWidget()
        self.setCentralWidget(root)
        layout = QtWidgets.QVBoxLayout(root)
        layout.setContentsMargins(12, 8, 12, 0)
        layout.setSpacing(7)
        self.mode_manager = ModeManager(self)
        self.mode_manager.mode_changed.connect(self._mode_changed)
        layout.addLayout(self._header())
        layout.addSpacing(10)
        self.central_table = CentralTable()
        self.central_table.role_changed.connect(self.set_column_role)
        self.central_table.column_renamed.connect(self.rename_column)
        self.central_table.cell_value_changed.connect(self.record_cell_edit)
        self.central_table.rows_deleted.connect(self.record_row_delete)
        self.central_table.columns_deleted.connect(self.record_column_delete)
        self.central_table.table_edited.connect(self.sync_table_to_backend)
        layout.addWidget(self.central_table, 1)
        layout.addWidget(self.mode_manager.stack, 0)
        self.status = PhysPlotStatusBar()
        layout.addWidget(self.status)

    def _build_menu_bar(self) -> None:
        menu_bar = self.menuBar()

        self.file_menu = file_menu = menu_bar.addMenu("File")
        self._add_menu_action(file_menu, "Import Data...", lambda: self.import_data("auto"), "Ctrl+O")
        self._add_menu_action(file_menu, "Import Folder...", self.import_folder)
        self._add_menu_action(file_menu, "Export Data...", self.export_data, "Ctrl+E")
        file_menu.addSeparator()
        self._add_menu_action(file_menu, "Open Config Folder", self.open_user_config_folder)
        self._add_menu_action(file_menu, "Reload Config Modules", self.reload_config_modules, "Ctrl+Shift+R")

        self.protocol_menu = protocol_menu = menu_bar.addMenu("Protocol")
        self._add_menu_action(protocol_menu, "Import Sequence.py...", self.open_workflow)
        self._add_menu_action(protocol_menu, "Export Sequence.py...", self.save_workflow, "Ctrl+S")
        self._add_menu_action(protocol_menu, "Apply This Sequence", self.apply_current_sequence, "Ctrl+R")
        self._add_menu_action(protocol_menu, "Copy Sequence Code", self.copy_workflow_script)
        self._add_menu_action(protocol_menu, "Clear Sequence", self.clear_recording)
        protocol_menu.addSeparator()
        self.protocol_modules_menu = protocol_menu.addMenu("Insert Protocol Module")
        self._populate_protocol_modules_menu()

        self.view_menu = view_menu = menu_bar.addMenu("View")
        self._add_menu_action(view_menu, "Simple Mode", lambda: self.mode_manager.set_mode("Simple"), "Ctrl+1")
        self._add_menu_action(view_menu, "Advanced Mode", lambda: self.mode_manager.set_mode("Advanced"), "Ctrl+2")

        self.plot_menu = plot_menu = menu_bar.addMenu("Plot")
        self._add_menu_action(plot_menu, "Generate Plot", self.generate_plot, "Ctrl+G")
        self._add_menu_action(plot_menu, "Update Integrated Preview", self.generate_integrated_plot)

        self.help_menu = help_menu = menu_bar.addMenu("Help")
        self._add_menu_action(help_menu, "Documentation", lambda: self._open_url("https://physplot.readthedocs.io/en/latest/"))
        self._add_menu_action(help_menu, "GitHub Repository", lambda: self._open_url("https://github.com/MShirazAhmad/PhysPlot"))
        self._add_menu_action(help_menu, "Report Issues or Bugs", lambda: self._open_url("https://github.com/MShirazAhmad/PhysPlot/issues"))
        help_menu.addSeparator()
        self._add_menu_action(help_menu, "About PhysPlot", self.show_about_dialog, menu_role=QtGui.QAction.AboutRole)

    def _add_menu_action(self, menu, text: str, callback, shortcut: str | None = None, menu_role=None):
        action = QtWidgets.QAction(text, self)
        if shortcut:
            action.setShortcut(shortcut)
        if menu_role is not None:
            action.setMenuRole(menu_role)
        action.triggered.connect(lambda checked=False: callback())
        menu.addAction(action)
        return action

    def _populate_protocol_modules_menu(self) -> None:
        menu = self.protocol_modules_menu
        menu.clear()
        entries = discover_protocol_modules()
        if not entries:
            placeholder = menu.addAction("No protocol modules in config/protocol_modules")
            placeholder.setEnabled(False)
            return
        for entry in entries:
            action = self._add_menu_action(menu, entry["display_name"], lambda path=entry["path"]: self.insert_protocol_module(path))
            if entry.get("description"):
                action.setStatusTip(entry["description"])
                action.setToolTip(entry["description"])

    def insert_protocol_module(self, path) -> None:
        """Append the steps of a reusable protocol module to the sequence."""
        try:
            steps = load_workflow(path)
            self.state.pp.workflow.extend(steps)
            self.state.timeline.extend(self._sequence_rows_from_steps(steps))
            self.status.set_message(f"Inserted protocol module {Path(path).stem}")
            self._refresh_all()
        except Exception as exc:
            self._error("Insert protocol module failed", exc)

    def open_user_config_folder(self) -> None:
        root = ensure_user_physplot_dirs() / "config"
        QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(str(root)))

    def reload_config_modules(self) -> None:
        """Re-scan every ``config/`` folder without restarting the application."""
        ensure_user_physplot_dirs()
        self._populate_protocol_modules_menu()
        for panel in self.mode_manager.panels.values():
            if hasattr(panel, "refresh_plugins"):
                panel.refresh_plugins()
        self._refresh_all()
        self.status.set_message(f"Reloaded config modules from {user_physplot_dir() / 'config'}")

    def _header(self):
        """Build the branded header row and create the mode switcher.

        The header is a three-column grid:

        * Left: the LSF logo (72 px high) and the PhysLab logo (46 px high), left-aligned. A
          logo whose image file is missing is left out.
        * Centre: the wide PhysPlot logo (72 px high). When ``PhysPlotWide1.png`` is missing, a
          bold "PhysPlot" title with the blue subtitle "Advanced Plotting Made Simple" is shown
          instead.
        * Right: the :class:`~physplot_gui.widgets.mode_switcher.ModeSwitcher` ("Mode:" with
          *Simple* and *Advanced* buttons), stored as ``self.mode_switcher``. Its
          ``mode_changed`` signal is connected to ``mode_manager.set_mode``, so
          ``self.mode_manager`` must exist before this method runs.

        The left and right columns get equal stretch and the centre none, which keeps the
        PhysPlot logo centred in the window.

        :returns: The ``QGridLayout``, which :meth:`_build_ui` adds to the root layout.
        """
        header = QtWidgets.QGridLayout()
        header.setContentsMargins(4, 0, 4, 0)
        header.setHorizontalSpacing(12)

        left_logos = QtWidgets.QHBoxLayout()
        left_logos.setContentsMargins(0, 0, 0, 0)
        left_logos.setSpacing(10)
        for path, height in ((LSF_LOGO, 72), (PHYSLAB_LOGO, 46)):
            label = self._logo_label(path, height)
            if label is not None:
                left_logos.addWidget(label)
        left_logos.addStretch(1)

        title_wrap = QtWidgets.QHBoxLayout()
        title_wrap.setContentsMargins(0, 0, 0, 0)
        if LOGO_WIDE.exists():
            logo = self._logo_label(LOGO_WIDE, 72)
            if logo is not None:
                title_wrap.addWidget(logo)
        else:
            labels = QtWidgets.QVBoxLayout()
            title = QtWidgets.QLabel("PhysPlot")
            title.setStyleSheet("font-size:30px;font-weight:800;color:#0f172a;")
            subtitle = QtWidgets.QLabel("Advanced Plotting Made Simple")
            subtitle.setStyleSheet("color:#0b65d8;font-weight:600;")
            labels.addWidget(title, alignment=QtCore.Qt.AlignCenter)
            labels.addWidget(subtitle, alignment=QtCore.Qt.AlignCenter)
            title_wrap.addLayout(labels)

        self.mode_switcher = ModeSwitcher()
        self.mode_switcher.mode_changed.connect(self.mode_manager.set_mode)

        header.addLayout(left_logos, 0, 0, alignment=QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        header.addLayout(title_wrap, 0, 1, alignment=QtCore.Qt.AlignCenter)
        header.addWidget(self.mode_switcher, 0, 2, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        header.setColumnStretch(0, 1)
        header.setColumnStretch(1, 0)
        header.setColumnStretch(2, 1)
        return header

    @staticmethod
    def _logo_label(path: Path, height: int):
        """Return a centred label showing an image scaled to a given height.

        The image is scaled with smooth transformation; its width follows from the aspect
        ratio. Used for the header logos and the About dialog icon.

        :param path: Image file to show.
        :param height: Height of the shown image in pixels.
        :returns: A ``QLabel`` with the scaled pixmap, or ``None`` when ``path`` does not exist.
        """
        if not path.exists():
            return None
        logo = QtWidgets.QLabel()
        logo.setAlignment(QtCore.Qt.AlignCenter)
        pixmap = QtGui.QPixmap(str(path))
        logo.setPixmap(pixmap.scaledToHeight(height, QtCore.Qt.SmoothTransformation))
        return logo

    def show_about_dialog(self) -> None:
        """Show the modal *About PhysPlot* dialog (Help > About PhysPlot).

        The dialog shows, top to bottom: the PhysPlot icon (64 px, when the image exists), the
        title "PhysPlot", the summary "Table-first scientific plotting and replayable workflow
        builder.", three links (Documentation on Read the Docs, GitHub Repository and Report
        issues or bugs) that open in the default browser, and a *Close* button. The call blocks
        until the dialog is closed. Nothing is recorded and the status bar is not changed.
        """
        about = QtWidgets.QDialog(self)
        about.setWindowTitle("About PhysPlot")
        about.setModal(True)
        layout = QtWidgets.QVBoxLayout(about)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(10)

        logo = self._logo_label(LOGO_ICON, 64)
        if logo is not None:
            layout.addWidget(logo, alignment=QtCore.Qt.AlignCenter)

        title = QtWidgets.QLabel("PhysPlot")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size:22px;font-weight:800;color:#0f172a;")
        layout.addWidget(title)

        summary = QtWidgets.QLabel("Table-first scientific plotting and replayable workflow builder.")
        summary.setAlignment(QtCore.Qt.AlignCenter)
        summary.setWordWrap(True)
        layout.addWidget(summary)

        links = QtWidgets.QLabel(
            "<p><a href='https://physplot.readthedocs.io/en/latest/'>Documentation</a></p>"
            "<p><a href='https://github.com/MShirazAhmad/PhysPlot'>GitHub Repository</a></p>"
            "<p><a href='https://github.com/MShirazAhmad/PhysPlot/issues'>Report issues or bugs</a></p>"
        )
        links.setAlignment(QtCore.Qt.AlignCenter)
        links.setTextFormat(QtCore.Qt.RichText)
        links.setOpenExternalLinks(True)
        layout.addWidget(links)

        close_button = QtWidgets.QPushButton("Close")
        close_button.clicked.connect(about.accept)
        layout.addWidget(close_button, alignment=QtCore.Qt.AlignCenter)
        about.exec_()

    @staticmethod
    def _open_url(url: str) -> None:
        """Open a web address in the system's default browser.

        Used by the Help menu items *Documentation*, *GitHub Repository* and *Report Issues or
        Bugs*. The result of ``QDesktopServices.openUrl`` is ignored, so a failure to open the
        browser is not reported.

        :param url: The address to open.
        """
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))

    def _bootstrap_blank_table(self) -> None:
        """Load an empty 17-row by 19-column table as the "Untitled" dataset.

        The columns are named ``Column 1`` to ``Column 19`` and every cell is an empty string.
        The frame is loaded into the backend through the ``dataframe`` loader
        (:meth:`~physplot_gui.app.gui_state.GuiState.load_dataframe`) and shown in the central
        table with every role at ``Ignore``. Called once from :meth:`__init__`; nothing is
        recorded in the protocol.
        """
        df = pd.DataFrame("", index=range(17), columns=[f"Column {i}" for i in range(1, 20)])
        self.state.load_dataframe(df, name="Untitled")
        self.central_table.set_dataframe(df, self.state.roles)

    def discover_function_entries(self) -> list[dict]:
        """Return the transformation plugins in ``config/transformations``, or a placeholder.

        No control in the bundled panels calls this method; the Simple Mode *Function* list
        comes from :meth:`simple_function_entries`.

        :returns: The entries from
            :func:`physplot_gui.app.plugin_discovery.discover_functions` (keys ``name``,
            ``display_name``, ``path`` and ``module``). When no plugin is found, a single
            placeholder ``{"display_name": "x", "path": None, "module": None}``.
        """
        entries = discover_functions()
        if not entries:
            entries = [{"display_name": "x", "path": None, "module": None}]
        return entries

    def discover_loader_entries(self) -> list[dict]:
        """Return the loader plugins in ``config/data_importers``, or an Auto Loader placeholder.

        No control in the bundled panels calls this method; the Simple Mode *Data Loader* list
        comes from :meth:`backend_loader_entries`.

        :returns: The entries from
            :func:`physplot_gui.app.plugin_discovery.discover_fileloaders` (keys
            ``display_name``, ``path`` and ``module``). When no plugin is found, a single entry
            ``{"display_name": "Auto Loader", "path": None, "module": None,
            "loader_id": "auto"}``.
        """
        entries = discover_fileloaders()
        if not entries:
            entries = [{"display_name": "Auto Loader", "path": None, "module": None, "loader_id": "auto"}]
        return entries

    def backend_loader_entries(self) -> list[dict]:
        """Return the entries of the Simple Mode *Data Loader* dropdown.

        The list starts with the built-in backend loaders in the order
        :func:`physplot.loaders.list_loaders` gives them (currently Auto Loader, CSV, TXT, Excel,
        Nanoindentation, XRDML and DataFrame loaders), each as ``{"display_name", "loader_id",
        "enabled"}``. ``enabled`` is ``False`` only for the internal ``dataframe`` loader, which
        the panel shows greyed out and :meth:`import_data` refuses. Loader plugins from
        ``config/data_importers`` follow, as returned by
        :func:`physplot_gui.app.plugin_discovery.discover_fileloaders` (``{"display_name",
        "path", "module"}``); the plugin files are imported again on every call.

        The panel stores each entry as item data and passes the selected one back to
        :meth:`import_data`. The list is also rebuilt after *File > Reload Config Modules*.

        :returns: The loader entries, built-in loaders first.
        """
        entries = [
            {"display_name": loader.name, "loader_id": loader.loader_id, "enabled": loader.loader_id != "dataframe"}
            for loader in list_loaders()
        ]
        entries.extend(discover_fileloaders())
        return entries

    def backend_transform_entries(self) -> list[str]:
        """Return the names of the built-in backend transformations.

        A thin wrapper around :func:`physplot.core.transformations.list_transforms`. No control
        in the bundled panels calls it; see :meth:`simple_function_entries` for the list the
        user sees.

        :returns: Backend function names such as ``"normalize_max"`` or ``"log10"``.
        """
        return list_transforms()

    def simple_function_entries(self) -> list[dict]:
        """Return the entries of the Simple Mode *Function* dropdown.

        The order is:

        1. ``identity`` followed by every built-in backend transformation from
           :func:`physplot.core.transformations.list_transforms`. Each becomes
           ``{"display_name", "function_name", "tooltip"}``, with the label and tooltip taken
           from :data:`BUILTIN_FUNCTIONS` (for example ``baseline_subtract`` is shown as
           "subtract first value"); a name missing from that table is shown as is, without a
           tooltip.
        2. Every transformation plugin from ``config/transformations``
           (:func:`physplot_gui.app.plugin_discovery.discover_functions`), keeping its
           ``name``, ``display_name``, ``path`` and ``module`` keys. Its tooltip is the first
           line of the plugin module's docstring followed by the file name in brackets, or just
           the file name when the module has no docstring.

        Labels are made unique: a plugin whose label is already taken is relabelled
        ``"<label> (<name>)"`` so it stays reachable, and any other repeated label is dropped
        (the first entry wins). The selected entry is passed back to
        :meth:`apply_backend_transform` when the user clicks *Apply*.

        :returns: The function entries in display order.
        """
        entries = []
        for name in ["identity", *list_transforms()]:
            label, tooltip = BUILTIN_FUNCTIONS.get(name, (name, ""))
            entries.append({"display_name": label, "function_name": name, "tooltip": tooltip})
        for entry in discover_functions():
            summary = (entry["module"].__doc__ or "").strip().splitlines()
            tooltip = f"{summary[0]} ({entry['path'].name})" if summary else entry["path"].name
            entries.append({**entry, "tooltip": tooltip})
        seen = set()
        unique = []
        for entry in entries:
            key = entry.get("display_name")
            if key in seen and entry.get("name"):
                # A plugin whose DISPLAY_NAME matches another entry stays reachable.
                entry = {**entry, "display_name": f"{key} ({entry['name']})"}
                key = entry["display_name"]
            if key in seen:
                continue
            seen.add(key)
            unique.append(entry)
        return unique

    def plotter_entries(self) -> list[dict]:
        """Return the entries of the Simple Mode *Plotter Module* dropdown.

        The list starts with the backend plotter modules that
        :meth:`physplot.plotting_modules.PlotterRegistry.list_plotters` offers for the current
        dataset, each as ``{"plotter_id", "name", "category"}``.

        When the last import used a loader plugin (``self._active_loader_entry``), the
        plotters that plugin declares (see
        :func:`physplot_gui.app.plugin_discovery.discover_loader_plotters`) are appended with
        the category ``"Loader"``:

        * An entry backed by a Python callable gets the id ``"loader:<plotter_id>"`` and is
          stored in ``self._custom_plotters`` so :meth:`generate_module_plot` can run it.
        * Any other entry uses its ``backend_plotter_id`` and is plotted by the backend.
        * An id already in the list is skipped.

        ``self._custom_plotters`` is reset on every call. The Simple Mode panel calls this
        whenever the window refreshes (through ``ModeManager.refresh_plots``).

        :returns: The plotter entries in display order.
        """
        dataset = self.state.pp.dataset
        entries = [
            {"plotter_id": plotter.plotter_id, "name": plotter.name, "category": plotter.category}
            for plotter in PlotterRegistry.default().list_plotters(dataset)
        ]
        self._custom_plotters = {}
        if isinstance(self._active_loader_entry, dict) and self._active_loader_entry.get("module") is not None:
            for entry in discover_loader_plotters(self._active_loader_entry["module"]):
                plotter_id = entry.get("backend_plotter_id") or f"loader:{entry['plotter_id']}"
                if "callable" in entry:
                    plotter_id = f"loader:{entry['plotter_id']}"
                    self._custom_plotters[plotter_id] = entry
                if any(existing["plotter_id"] == plotter_id for existing in entries):
                    continue
                entries.append(
                    {
                        "plotter_id": plotter_id,
                        "name": entry.get("name", plotter_id),
                        "category": "Loader",
                    }
                )
        return entries

    def plot_type_entries(self, plotter_id: str) -> list[str]:
        """Return the *Plot Type* choices for the selected plotter module.

        Called by Simple Mode whenever the *Plotter Module* selection changes.

        :param plotter_id: Id of the selected plotter, as returned by :meth:`plotter_entries`.
        :returns: For a loader-declared callable plotter, its declared ``plot_types`` (or
            ``["publication_ready"]`` when it declares none). For a backend plotter, the types
            :meth:`physplot.plotting_modules.PlotterRegistry.list_plot_types` offers for the
            current dataset (for the Basic Plotter, for example ``scatter``, ``line`` and
            ``scatter_line``). An empty list when ``plotter_id`` is empty.
        """
        if plotter_id in self._custom_plotters:
            return list(self._custom_plotters[plotter_id].get("plot_types") or ["publication_ready"])
        dataset = self.state.pp.dataset
        return PlotterRegistry.default().list_plot_types(plotter_id, dataset) if plotter_id else []

    def style_module_entries(self) -> list[dict]:
        """Return the entries of the Simple Mode *Template* dropdown.

        The first entry, ``{"name": "None", "path": None}``, means "no template". It is followed
        by every figure template JSON file from :func:`physplot_gui.plot_styles.list_style_modules`
        (the per-user ``config/templates`` folder first, then the bundled one, or only the
        folder in ``PHYSPLOT_STYLE_DIR`` when that variable is set), sorted by name. Templates
        are saved from the Figure Editor with *PhysPlot > Save as Template*.

        :returns: Entries of the form ``{"name", "path"}``.
        """
        return [{"name": "None", "path": None}, *list_style_modules()]

    def fit_style_entries(self) -> list[dict]:
        """Return the entries of the Simple Mode *Fit Style* dropdown.

        The first entry, ``{"name": "Default", "path": None, "style": None}``, keeps the Fit
        Line fields as they are. It is followed by the LSQ fit-style presets from
        :func:`physplot_gui.fit_styles.list_fit_style_presets` (``config/figureforge_fit_styles``,
        or the folder in ``PHYSPLOT_FIT_STYLE_DIR``), sorted by name. Choosing a preset fills
        the fit label, line style, line width and legend fields from its ``style`` payload.

        :returns: Entries of the form ``{"name", "path", "style"}``, where ``style`` is the
            preset's JSON content.
        """
        return [{"name": "Default", "path": None, "style": None}, *list_fit_style_presets()]

    def refresh_style_modules(self) -> None:
        """Refresh the plotter-related dropdowns of the panels.

        Calls ``ModeManager.refresh_plots``: Simple Mode rebuilds its *Plotter Module*, *Plot
        Type* and *Template* lists, and Advanced Mode's ``refresh_plot`` does nothing. No
        control in the bundled panels calls this method; the *Reload* button next to
        *Template* calls the panel's own ``refresh_styles``.
        """
        self.mode_manager.refresh_plots()

    def _selected_style_module(self):
        """Return the template path selected in Simple Mode, or ``None``.

        Reads ``SimpleModePanel.current_style_module()``. :meth:`generate_plot` (*Plot >
        Generate Plot*) uses it so the menu command applies the same Template as the panel.

        :returns: The template file path as a string, or ``None`` when *None* is selected or
            the Simple Mode panel has no ``current_style_module`` method.
        """
        panel = self.mode_manager.panels.get("Simple")
        if hasattr(panel, "current_style_module"):
            return panel.current_style_module()
        return None

    def _mode_changed(self, mode: str) -> None:
        """React to a switch between Simple and Advanced Mode.

        Connected to ``ModeManager.mode_changed``, which fires after the header switcher or
        *View > Simple Mode* / *Advanced Mode* has already swapped the lower panel. Stores the
        mode in ``state.mode``, updates the switcher's checked button, sets the status to
        ``Ready`` and runs :meth:`_refresh_all` (which also shows or hides the Advanced-only
        status bar fields). Nothing is recorded in the protocol.

        :param mode: ``"Simple"`` or ``"Advanced"``.
        """
        self.state.mode = mode
        self.mode_switcher.set_mode(mode)
        self.status.set_message("Ready")
        self._refresh_all()

    def _refresh_all(self) -> None:
        """Bring every widget in line with the current state.

        Called at the end of most actions. In order it:

        1. Takes the column names from the central table, which include its empty padding
           columns (or from the backend dataframe if the table does not exist yet).
        2. Makes the mode switcher visible.
        3. Sets the role dropdowns from the backend roles (``state.roles``).
        4. Refreshes the panels' column lists (Simple Mode *Input* and *Output*; Simple Mode
           selects the Y-role column as *Input* when a new dataset was loaded).
        5. Passes ``state.transformations`` to the panels' ``refresh_pipeline`` (the bundled
           panels ignore it).
        6. Rebuilds the Build Protocol and Run Sequence tables from ``state.timeline``,
           including the Status column (see ``timeline_row_status``), and the Code view unless
           it is open with unapplied edits.
        7. Passes ``state.pp.recording`` to the Advanced panel's ``set_recording`` (the bundled
           panel always shows "Tracking: ON").
        8. Rebuilds the Simple Mode plotter, plot type and template lists (``refresh_plots``).
        9. Updates the status bar counts, file name, sequence file name and mode.

        It does not change the table cells and does not set a status message.
        """
        columns = self.central_table.column_names() if hasattr(self, "central_table") else list(self.state.dataframe.columns)
        self.mode_switcher.setVisible(True)
        self.central_table.set_roles(self.state.roles)
        self.mode_manager.refresh_columns(columns)
        self.mode_manager.refresh_pipeline(self.state.transformations)
        self.mode_manager.refresh_timeline(self.state.timeline)
        self.mode_manager.set_recording(bool(getattr(self.state.pp, "recording", False)))
        self.mode_manager.refresh_plots()
        self.status.update_state(self.state)

    def sync_table_to_backend(self) -> None:
        """Copy the visible table contents into the backend dataset.

        Connected to ``CentralTable.table_edited`` (emitted after typing, pasting, clearing,
        renaming and deleting rows or columns) and called before every action that reads the
        data: export, plotting, transformations, fitting and sequence replay.

        ``CentralTable.to_dataframe`` trims the table to its used extent (keeping columns that
        have a role) and converts columns whose non-empty cells are all numbers to numeric.
        :meth:`~physplot_gui.app.gui_state.GuiState.refresh_dataset_values` then reloads that
        frame into ``state.pp`` while keeping the dataset name, roles, metadata, source path
        and loader information. The status bar counts are updated.

        Nothing is recorded here; the individual edits are recorded by
        :meth:`record_cell_edit`, :meth:`record_row_delete`, :meth:`record_column_delete` and
        :meth:`rename_column`.
        """
        self.state.refresh_dataset_values(self.central_table.to_dataframe())
        self.status.update_state(self.state)

    def new_table(self, rows: int, columns: int, delete_old: bool) -> None:
        """Replace the data with a blank or resized table named "Untitled".

        ``CentralTable.resize_table`` either builds a blank table (``delete_old`` true) or
        keeps the current values, padding or cutting them to the new size; in both cases the
        roles are cleared. The result is loaded into the backend as ``Untitled``, the active
        loader plugin and the current file are forgotten, the status is set to ``Ready`` and the
        window is refreshed. Nothing is recorded in the protocol. No control in the bundled
        panels or menus calls this method.

        :param rows: Number of data rows.
        :param columns: Number of columns.
        :param delete_old: ``True`` to discard the current values.
        """
        df = self.central_table.resize_table(rows, columns, delete_old)
        self.state.load_dataframe(df, name="Untitled")
        self._active_loader_entry = None
        self.state.current_file = None
        self.status.set_message("Ready")
        self._refresh_all()

    def import_data(self, loader: str | dict = "auto") -> None:
        """Ask for a data file, load it into the table and record a *File Loader* row.

        Triggered by *File > Import Data...* (``Ctrl+O``, always the Auto Loader) and by the
        *Import Data* button of Simple Mode's **1. Data Importer** (the loader selected in
        *Data Loader*). An *Import Data* file dialog opens in the current working directory
        with two filters: "Data Files" from :func:`data_file_filter` (the built-in types plus
        every loader plugin's ``FILE_EXTENSIONS``) and "All Files".
        Cancelling does nothing.

        **Loader plugin** (an entry with a ``module``, from ``config/data_importers``): the
        plugin's ``load_data(path)`` is called. A returned DataFrame keeps its column names
        unless the plugin defines ``COLUMN_NAMES`` (or ``column_names``); any other result is
        turned into an array and named from those names or ``Column N`` (see
        :meth:`_plugin_column_names`). A 1-D result becomes one column; anything that is not
        2-D raises "Loader must return a 2D table-like array.". The table is loaded into the
        backend through the ``dataframe`` loader under the file's stem, the plugin path and
        name are stored in the dataset
        metadata (``loader_plugin``, ``loader_name``), the plugin's ``DEFAULT_COLUMN_ROLES`` are
        applied (:meth:`_apply_loader_roles`) and the entry is remembered as the active loader,
        so its declared plotters appear in the Plotter Module list. The recorded step is
        ``LoadDataStep(path, loader="dataframe", dataset_name=<stem>,
        loader_plugin=<plugin path>)``.

        **Built-in loader** (a loader id string or an entry with a ``loader_id``):
        :meth:`physplot.PhysPlot.load` reads the file (``"auto"`` picks the loader from the
        file extension), the loader's suggested roles are applied and the active loader plugin
        is cleared. The recorded step is ``LoadDataStep(path, loader=<id>,
        dataset_name=<stem>)``.

        In both cases the file becomes ``state.current_file`` (shown as ``File:`` in the status
        bar) and the table is redrawn from the backend dataset. The load step and, when any
        column has a role other than Ignore, a ``SetRoleStep`` with those roles are appended to
        the protocol as one *File Loader* row whose details read ``"<loader> (column names and
        role setup)"`` (or ``"(column names)"`` without roles) and whose target is the file
        name. The status is set to ``Ready`` and the window refreshed.

        Errors, including choosing a disabled entry such as the DataFrame loader ("... is not
        available yet."), are reported as "Import failed" through :meth:`_error`.

        :param loader: A backend loader id such as ``"auto"`` or ``"csv"``, or an entry from
            :meth:`backend_loader_entries`.
        """
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Import Data",
            str(Path.cwd()),
            data_file_filter(),
        )
        if not path:
            return
        try:
            loader_id = loader.get("loader_id") if isinstance(loader, dict) else loader
            loader_display = (
                loader.get("display_name")
                if isinstance(loader, dict)
                else {entry.loader_id: entry.name for entry in list_loaders()}.get(loader_id or "auto", str(loader_id))
            )
            if isinstance(loader, dict) and not loader.get("enabled", True):
                raise ValueError(f"{loader.get('display_name', 'Selected loader')} is not available yet.")
            if isinstance(loader, dict) and loader.get("module") is not None:
                loaded = loader["module"].load_data(path)
                if isinstance(loaded, pd.DataFrame):
                    table_data = loaded.to_numpy()
                    column_names = self._plugin_column_names(loader["module"], len(loaded.columns), list(loaded.columns))
                else:
                    table_data = np.asarray(loaded)
                    column_names = self._plugin_column_names(loader["module"], table_data.shape[1] if table_data.ndim > 1 else 1)
                if table_data.ndim == 1:
                    table_data = table_data.reshape(-1, 1)
                if table_data.ndim != 2:
                    raise ValueError("Loader must return a 2D table-like array.")
                df = pd.DataFrame(
                    table_data,
                    columns=column_names,
                )
                self.state.load_dataframe(df, name=Path(path).stem)
                self.state.pp.dataset.metadata["loader_plugin"] = str(loader.get("path", ""))
                self.state.pp.dataset.metadata["loader_name"] = loader.get("display_name")
                self._apply_loader_roles(loader, df.columns)
                self._active_loader_entry = loader
                workflow_step = LoadDataStep(
                    path=str(path),
                    loader="dataframe",
                    dataset_name=Path(path).stem,
                    loader_plugin=str(loader.get("path")) if loader.get("path") else None,
                )
            else:
                self.state.pp.load(path, loader=loader_id or "auto")
                self.state.pp.dataset.apply_suggested_roles()
                self._active_loader_entry = None
                workflow_step = LoadDataStep(path=str(path), loader=loader_id or "auto", dataset_name=Path(path).stem)
            self.state.current_file = Path(path)
            self.central_table.set_dataframe(self.state.dataframe, self.state.roles)
            workflow_steps = [workflow_step]
            role_step = self._role_step_from_current_roles()
            if role_step is not None:
                workflow_steps.append(role_step)
            setup_note = "column names"
            if role_step is not None:
                setup_note += " and role setup"
            self._append_sequence(
                "File Loader",
                f"{loader_display or 'Auto Loader'} ({setup_note})",
                Path(path).name,
                workflow_steps=workflow_steps,
            )
            self.status.set_message("Ready")
            self._refresh_all()
        except Exception as exc:
            self._error("Import failed", exc)

    def _apply_loader_roles(self, loader: dict, columns) -> None:
        """Apply a loader plugin's ``DEFAULT_COLUMN_ROLES`` to the loaded columns.

        The plugin's ``DEFAULT_COLUMN_ROLES`` list (empty when missing) is matched to the
        columns by position; extra roles or extra columns are ignored. Common spellings are
        normalised, case-insensitively: ``x`` and ``x-axis`` become X, ``y`` and ``y-axis``
        become Y, ``x error`` / ``x-error`` and ``y error`` / ``y-error`` become X Error and
        Y Error, ``group`` and ``label`` become Group and Label. Any other text is used as
        written (stripped); an empty role is skipped. Roles are set on the backend dataset
        only; the caller records them as part of the *File Loader* row.

        :param loader: The loader-plugin entry; its ``module`` is read.
        :param columns: The loaded column names, in table order.
        """
        role_map = {
            "x": "X",
            "x-axis": "X",
            "y": "Y",
            "y-axis": "Y",
            "x error": "X Error",
            "x-error": "X Error",
            "y error": "Y Error",
            "y-error": "Y Error",
            "group": "Group",
            "label": "Label",
        }
        roles = getattr(loader["module"], "DEFAULT_COLUMN_ROLES", [])
        for column, role in zip(columns, roles):
            normalized = role_map.get(str(role).strip().lower(), str(role).strip())
            if normalized:
                self.state.set_role(str(column), normalized)

    @staticmethod
    def _plugin_column_names(module, column_count: int, fallback_names=None) -> list[str]:
        """Return exactly ``column_count`` column names for data from a loader plugin.

        Names come from the plugin's ``COLUMN_NAMES`` or ``column_names`` attribute (called
        first when it is a function), otherwise from ``fallback_names``. Each name is converted
        to text and stripped, and blank names are dropped. Missing trailing names are filled
        with ``Column N``, where N is the column's position, and surplus names are cut off.

        :param module: The imported loader plugin module.
        :param column_count: Number of columns the loaded data has.
        :param fallback_names: Names to use when the plugin declares none, for example the
            columns of a returned DataFrame.
        :returns: The column names, one per column.
        """
        raw_names = getattr(module, "COLUMN_NAMES", None) or getattr(module, "column_names", None)
        if callable(raw_names):
            raw_names = raw_names()
        names = [str(name).strip() for name in (raw_names or fallback_names or []) if str(name).strip()]
        if len(names) < column_count:
            names.extend(f"Column {index}" for index in range(len(names) + 1, column_count + 1))
        return names[:column_count]

    def import_folder(self) -> None:
        """Ask for a folder and report the choice in the status bar.

        Triggered by *File > Import Folder...* and Simple Mode's *Import Folder* button. An
        *Import Folder* directory dialog opens in the current working directory; after a choice
        the status reads ``Folder selected: <folder name>``. No files are loaded and nothing is
        recorded. To process every file of a folder, use Advanced Mode > *Run Sequence*
        (:meth:`run_bulk_workflow`).
        """
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Import Folder", str(Path.cwd()))
        if folder:
            self.status.set_message(f"Folder selected: {Path(folder).name}")

    def export_data(self) -> None:
        """Export the current dataset, sequence, fit and plot to a folder.

        Triggered by *File > Export Data...* (``Ctrl+E``) and Simple Mode's *Export Data*
        button. The table is first synced to the backend (:meth:`sync_table_to_backend`), then
        an *Export Data* directory dialog opens in the current working directory. For the chosen
        folder :meth:`physplot.PhysPlot.export` writes ``data.csv`` (the table),
        ``columns.csv`` (column metadata) and ``workflow.py`` (the protocol as a runnable
        sequence file), plus ``fit.json`` when a fit result exists and ``plot.png`` when a
        figure has been generated. The status then reads ``Exported``; errors are reported as
        "Export failed". The export is not recorded in the protocol.
        """
        self.sync_table_to_backend()
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Export Data", str(Path.cwd()))
        if not folder:
            return
        try:
            self.state.pp.export(folder)
            self.status.set_message("Exported")
        except Exception as exc:
            self._error("Export failed", exc)

    def generate_plot(self) -> None:
        """Plot the X and Y columns as a Basic Plotter scatter plot in the Figure Editor.

        Triggered by *Plot > Generate Plot* (``Ctrl+G``). The table is synced to the backend,
        then :meth:`physplot.PhysPlot.plot_with_module` draws ``("basic", "scatter")`` from the
        X and Y role columns and records a ``PlotModuleStep``. The Template selected in Simple
        Mode (:meth:`_selected_style_module`) is applied to the figure, which then opens in the
        Figure Editor (:meth:`_open_figureforge_editor`). A *Generate Plot* row with the
        details ``Create <mode> plot`` (``Single`` in Simple Mode, ``Sequence`` in Advanced
        Mode; see :meth:`_current_plot_mode`) and the target ``X vs Y`` is linked to the
        recorded step, the status reads ``Plot generated`` and the window is refreshed.

        Errors, such as missing X/Y roles or a Figure Editor that is not installed, are reported
        as "Plot failed". If the error happens after the backend call, the ``PlotModuleStep`` is
        already in ``pp.workflow`` but no protocol row is added for it.
        """
        self.sync_table_to_backend()
        try:
            figure = self.state.pp.plot_with_module("basic", "scatter")
            workflow_index = len(self.state.pp.workflow) - 1 if self.state.pp.workflow else None
            apply_style_module(figure, self._selected_style_module())
            self._open_figureforge_editor(figure)
            self._append_sequence(
                "Generate Plot",
                f"Create {self._current_plot_mode()} plot",
                "X vs Y",
                workflow_index=workflow_index,
            )
            self.status.set_message("Plot generated")
            self._refresh_all()
        except Exception as exc:
            self._error("Plot failed", exc)

    def generate_integrated_plot(self) -> None:
        """Refresh the panels' plot controls and log a display-only protocol row.

        Triggered by *Plot > Update Integrated Preview*. The table is synced to the backend and
        ``ModeManager.refresh_plots`` runs (Simple Mode rebuilds its plotter, plot type and
        template lists; the Advanced panel's ``refresh_plot`` does nothing). A *Generate Plot*
        row with the details ``Create <mode> integrated plot`` and the target ``Plot Preview``
        is added through :meth:`_record`; it has no backend step, so it is not replayed. The
        status reads ``Plot preview updated``. No figure is drawn, and because
        :meth:`_refresh_all` is not called the new row shows in Build Protocol at the next full
        refresh. Errors are reported as "Plot failed".
        """
        self.sync_table_to_backend()
        try:
            self.mode_manager.refresh_plots()
            self._record("Generate Plot", f"Create {self._current_plot_mode()} integrated plot", "Plot Preview")
            self.status.set_message("Plot preview updated")
            self.status.update_state(self.state)
        except Exception as exc:
            self._error("Plot failed", exc)

    def _open_legacy_plot_windows(self) -> None:
        """Open or raise the legacy plot configuration and plot windows side by side.

        Imports the legacy :mod:`physplot.app` module, fills its module-level table and role
        arrays from the central table (:meth:`_prepare_legacy_plot_state`, which raises
        ``ValueError`` unless exactly one column is X and one is Y) and sets
        ``self._main_window``. The legacy configuration window (``Ui_ConfigWindow``) and plot
        window (``Plot_Window``) are created and shown when they do not exist or are hidden;
        otherwise they are raised and activated, and the plot window is redrawn. Both are then
        placed next to each other (:meth:`_tile_legacy_plot_windows`).

        Nothing in the current GUI calls this method; exceptions propagate to the caller.
        """
        from physplot import app as legacy_app

        self._prepare_legacy_plot_state(legacy_app)
        self._main_window = self
        if getattr(self, "plot_config_window", None) is None or not self.plot_config_window.isVisible():
            self.plot_config_window = QtWidgets.QMainWindow()
            self.plot_config_ui = legacy_app.Ui_ConfigWindow()
            self.plot_config_ui.setupUiConfigWindow(self.plot_config_window)
            self.plot_config_ui.owner = self
            self.plot_config_window.show()
        else:
            self.plot_config_window.raise_()
            self.plot_config_window.activateWindow()

        if getattr(self, "plot_window", None) is None or not self.plot_window.isVisible():
            self.plot_window = legacy_app.Plot_Window()
            self.plot_window.show()
        else:
            self.plot_window.refresh_plot()
            self.plot_window.raise_()
            self.plot_window.activateWindow()
        self._tile_legacy_plot_windows()

    def _tile_legacy_plot_windows(self) -> None:
        """Place the legacy configuration and plot windows next to each other.

        Does nothing unless both windows exist and a screen is available. On the screen of this
        window (or the primary screen), the configuration window goes on the left and the plot
        window on the right with a 12 px gap, the pair horizontally centred with at least a
        24 px left margin. The top edge is at least 24 px below the top of the available area
        and 40 px below this window's top. Both windows get the same height. Sizes start from
        the windows' current sizes with minimums of 620 px height and 430 px / 860 px width,
        then are limited by the available screen space (but never below 420 px height and
        380 px / 620 px width). Both windows are raised afterwards.
        """
        config_window = getattr(self, "plot_config_window", None)
        plot_window = getattr(self, "plot_window", None)
        if config_window is None or plot_window is None:
            return
        screen = self.screen() or QtWidgets.QApplication.primaryScreen()
        if screen is None:
            return
        available = screen.availableGeometry()
        gap = 12
        margin = 24
        top = max(available.top() + margin, self.y() + 40)
        height = min(max(620, config_window.height(), plot_window.height()), max(420, available.height() - top - margin))
        config_width = min(max(430, config_window.width()), max(380, int(available.width() * 0.32)))
        plot_width = min(max(860, plot_window.width()), max(620, available.width() - config_width - gap - margin * 2))
        total_width = config_width + gap + plot_width
        left = available.left() + max(margin, (available.width() - total_width) // 2)
        config_window.setGeometry(left, top, config_width, height)
        plot_window.setGeometry(left + config_width + gap, top, plot_width, height)
        config_window.raise_()
        plot_window.raise_()

    def _prepare_legacy_plot_state(self, legacy_app) -> None:
        """Copy the table and its roles into the legacy plotting module's globals.

        ``legacy_app.OutPut_Table`` receives the trimmed table as a float array, with cells that
        are not numbers set to 0.0. ``legacy_app.tableLabels`` receives one integer code per
        column (at least 100 entries): 1 for X, 2 for X Error, 3 for Y, 4 for Y Error and 0 for
        every other role.

        :param legacy_app: The imported :mod:`physplot.app` module.
        :raises ValueError: Unless exactly one column has the X role and exactly one the Y role
            ("Select exactly one X column and one Y column from the column dropdowns before
            generating a plot.").
        """
        df = self.central_table.to_dataframe()
        numeric = df.apply(pd.to_numeric, errors="coerce").fillna(0.0)
        legacy_app.OutPut_Table = numeric.to_numpy(dtype=float)
        legacy_app.tableLabels = np.zeros(max(100, len(numeric.columns)), dtype=int)
        role_map = {"X": 1, "X Error": 2, "Y": 3, "Y Error": 4}
        for column_index, column_name in enumerate(numeric.columns):
            role = self.state.roles.get(column_name, "Ignore")
            legacy_app.tableLabels[column_index] = role_map.get(role, 0)
        if int(np.count_nonzero(legacy_app.tableLabels == 1)) != 1 or int(np.count_nonzero(legacy_app.tableLabels == 3)) != 1:
            raise ValueError(
                "Select exactly one X column and one Y column from the column dropdowns before generating a plot."
            )

    def _open_figureforge_editor(self, figure) -> None:
        """Open a Matplotlib figure in the Figure Editor (FigureForge) in a new process.

        Used for Basic Plotter figures by :meth:`generate_plot` and
        :meth:`generate_module_plot`. Steps:

        1. When the ``FigureForge`` package cannot be found, raise a ``RuntimeError`` saying
           the Figure Editor is not installed and giving ``python -m pip install FigureForge``.
        2. Copy PhysPlot's Figure Editor plugins into FigureForge and point its preferences at
           them (:meth:`_install_figureforge_plugins`).
        3. Add hidden placeholder artists to the figure (:meth:`_prepare_figureforge_figure`).
        4. Clean up editors that have already closed (:meth:`_reap_figureforge_processes`).
        5. Pickle the figure into a temporary ``physplot_figureforge_*.pkl`` file and start
           ``sys.executable -c <launcher> <file>`` with :class:`subprocess.Popen` in the
           current working directory. Standard output is discarded and standard error is
           captured. The environment adds ``PHYSPLOT_STYLE_DIR`` (from
           :func:`physplot_gui.plot_styles.style_directory`, where templates saved in the
           editor go) and ``PHYSPLOT_APP_ICON`` (the PhysPlot icon path).
        6. Remember ``(process, temp file)`` in ``self._figureforge_processes`` and schedule
           :meth:`_check_figureforge_process` to run once after 1200 ms.

        The launcher script, run in the new Python process, unpickles the figure, creates a
        PySide6 ``QApplication`` with the PhysPlot icon, shows the FigureForge splash screen and
        main window with the figure, renames FigureForge's plugin menu to "Figure Editor", runs
        the event loop and deletes the temporary file when it ends.

        The method returns without waiting for the editor, so PhysPlot stays usable and several
        editors can be open at once. If starting the process fails, the temporary file is
        deleted and the exception is re-raised; callers report it as "Plot failed".

        :param figure: The Matplotlib figure to edit. Changes made in the editor are not sent
            back to this figure.
        :raises RuntimeError: When FigureForge or the plugin folder is missing.
        """
        if importlib.util.find_spec("FigureForge") is None:
            raise RuntimeError("Figure Editor is not installed. Install it with `python -m pip install FigureForge`.")

        self._install_figureforge_plugins()
        self._prepare_figureforge_figure(figure)
        self._reap_figureforge_processes()
        temp_file = tempfile.NamedTemporaryFile(
            prefix="physplot_figureforge_",
            suffix=".pkl",
            delete=False,
        )
        temp_path = Path(temp_file.name)
        try:
            with temp_file:
                pickle.dump(figure, temp_file)
            launcher = textwrap.dedent(
                """
                import os
                import pickle
                import sys

                temp_path = sys.argv[1]
                try:
                    with open(temp_path, "rb") as handle:
                        figure = pickle.load(handle)
                    from PySide6.QtWidgets import QApplication
                    from FigureForge.main import create_splash
                    from FigureForge.gui import MainWindow

                    app = QApplication.instance() or QApplication(sys.argv)
                    icon_path = os.environ.get("PHYSPLOT_APP_ICON")
                    if icon_path:
                        from PySide6.QtGui import QIcon

                        app.setWindowIcon(QIcon(icon_path))
                    splash = create_splash()
                    window = MainWindow(splash, figure)
                    window.plugin_menu.setTitle("Figure Editor")
                    window.show()
                    splash.finish(window)
                    app.exec()
                finally:
                    try:
                        os.remove(temp_path)
                    except OSError:
                        pass
                """
            )
            process = subprocess.Popen(
                [sys.executable, "-c", launcher, str(temp_path)],
                cwd=str(Path.cwd()),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
                env={**os.environ, "PHYSPLOT_STYLE_DIR": str(style_directory()), "PHYSPLOT_APP_ICON": str(LOGO_ICON)},
            )
        except Exception:
            try:
                temp_path.unlink()
            except OSError:
                pass
            raise

        self._figureforge_processes = getattr(self, "_figureforge_processes", [])
        self._figureforge_processes.append((process, temp_path))
        QtCore.QTimer.singleShot(1200, lambda: self._check_figureforge_process(process, temp_path))

    def _check_figureforge_process(self, process, temp_path: Path) -> None:
        """Report a Figure Editor process that failed right after starting.

        Runs once, about 1.2 s after :meth:`_open_figureforge_editor` started the process. If
        the process is still running, nothing happens (it is not checked again). Otherwise its
        captured standard error is read, finished editors are cleaned up
        (:meth:`_reap_figureforge_processes`) and, for a non-zero exit code, "Figure Editor
        failed" is reported through :meth:`_error` with the error output (or "Figure Editor
        exited with code N." when there is none). The temporary figure file is deleted if it
        still exists.

        :param process: The ``subprocess.Popen`` object of the editor.
        :param temp_path: The temporary pickle file passed to the editor.
        """
        if process.poll() is None:
            return
        try:
            _, stderr = process.communicate(timeout=0.1)
        except Exception:
            stderr = ""
        self._reap_figureforge_processes()
        if process.returncode:
            detail = stderr.strip() or f"Figure Editor exited with code {process.returncode}."
            self._error("Figure Editor failed", RuntimeError(detail))
        try:
            temp_path.unlink()
        except OSError:
            pass

    def _reap_figureforge_processes(self) -> None:
        """Forget Figure Editor processes that have exited and delete their temporary files.

        Keeps only the still-running entries of ``self._figureforge_processes``. Called before
        each new editor is opened and after a finished process is checked; errors while
        deleting a file are ignored.
        """
        active = []
        for process, temp_path in getattr(self, "_figureforge_processes", []):
            if process.poll() is None:
                active.append((process, temp_path))
                continue
            try:
                temp_path.unlink()
            except OSError:
                pass
        self._figureforge_processes = active

    @staticmethod
    def _install_figureforge_plugins() -> None:
        """Copy PhysPlot's Figure Editor plugins into the installed FigureForge package.

        Every ``*.py`` file from the existing folders returned by
        :func:`figureforge_plugin_dirs` (bundled ``config/figureforge_plugins`` first, then the
        per-user copy, so a per-user file replaces a bundled file of the same name) is copied
        into the ``plugins`` folder inside the FigureForge package, which is created when
        missing. Existing files there with the same names are overwritten. FigureForge's
        preferences are then pointed at that folder
        (:meth:`_point_figureforge_at_plugin_dir`). Runs each time a figure is opened in the
        editor.

        :raises RuntimeError: When FigureForge is not installed, or when none of the plugin
            folders exists (the message names ``FIGUREFORGE_PLUGIN_DIR``).
        """
        spec = importlib.util.find_spec("FigureForge")
        if spec is None or not spec.submodule_search_locations:
            raise RuntimeError("Figure Editor is not installed. Install it with `python -m pip install FigureForge`.")
        source_dirs = [directory for directory in figureforge_plugin_dirs() if directory.exists()]
        if not source_dirs:
            raise RuntimeError(f"PhysPlot Figure Editor plugin directory is missing: {FIGUREFORGE_PLUGIN_DIR}")
        plugin_dir = Path(next(iter(spec.submodule_search_locations))) / "plugins"
        plugin_dir.mkdir(parents=True, exist_ok=True)
        for source_dir in source_dirs:
            for plugin_source in source_dir.glob("*.py"):
                shutil.copy2(plugin_source, plugin_dir / plugin_source.name)
        MainWindow._point_figureforge_at_plugin_dir(plugin_dir)

    @staticmethod
    def _point_figureforge_at_plugin_dir(plugin_dir: Path) -> None:
        """Write FigureForge's ``preferences.json`` so it loads plugins from ``plugin_dir``.

        The file lives in ``appdirs.user_config_dir(<installed FigureForge version>,
        "FigureForge")``, which is created when missing. Existing preferences are read (an
        unreadable JSON file is treated as empty) and updated: ``plugin_directory`` is set to
        ``plugin_dir`` and ``plugin_requirements`` to ``plugin_dir / "requirements.txt"``,
        while ``theme``, ``debug``, ``show_welcome``, ``recent_files``, ``check_for_updates``
        and ``last_export_path`` keep their current values or get the defaults ``"light"``,
        ``False``, ``False``, ``[]``, ``False`` and ``""``. Other keys are kept.

        :param plugin_dir: The FigureForge plugin folder the PhysPlot plugins were copied to.
        """
        config_dir = Path(user_config_dir(package_version("FigureForge"), "FigureForge"))
        config_dir.mkdir(parents=True, exist_ok=True)
        preferences_path = config_dir / "preferences.json"
        if preferences_path.exists():
            try:
                preferences = json.loads(preferences_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                preferences = {}
        else:
            preferences = {}
        preferences.update(
            {
                "plugin_directory": str(plugin_dir),
                "plugin_requirements": str(plugin_dir / "requirements.txt"),
                "theme": preferences.get("theme", "light"),
                "debug": preferences.get("debug", False),
                "show_welcome": preferences.get("show_welcome", False),
                "recent_files": preferences.get("recent_files", []),
                "check_for_updates": preferences.get("check_for_updates", False),
                "last_export_path": preferences.get("last_export_path", ""),
            }
        )
        preferences_path.write_text(json.dumps(preferences, indent=4), encoding="utf-8")

    @staticmethod
    def _prepare_figureforge_figure(figure) -> None:
        """Add hidden placeholder artists to every axes of a figure before editing.

        For each axes that lacks one, this adds an empty invisible line labelled
        ``_physplot_template_line``, an empty invisible scatter labelled
        ``_physplot_template_scatter``, an empty hidden legend and an empty invisible annotation
        labelled ``_physplot_template_annotation``. Axes that already have an artist of a kind
        are left alone for that kind. :mod:`physplot_gui.plot_styles` recognises the
        ``_physplot_template`` label prefix and leaves the placeholder line and scatter out
        when it saves a template. The figure is changed in place.

        :param figure: The Matplotlib figure that will be opened in the Figure Editor.
        """
        for axes in figure.get_axes():
            if not any(child.__class__.__name__ == "Line2D" for child in axes.get_children()):
                axes.plot([], [], label="_physplot_template_line", visible=False)
            if not any(child.__class__.__name__ == "PathCollection" for child in axes.get_children()):
                axes.scatter([], [], label="_physplot_template_scatter", visible=False)
            if axes.get_legend() is None:
                legend = axes.legend([], [])
                legend.set_visible(False)
            if not any(child.__class__.__name__ == "Annotation" for child in axes.get_children()):
                axes.annotate(
                    "",
                    xy=(0.5, 0.5),
                    xytext=(0.5, 0.5),
                    xycoords="axes fraction",
                    textcoords="axes fraction",
                    annotation_clip=False,
                    label="_physplot_template_annotation",
                    visible=False,
                )

    def set_column_role(self, column: str, role: str) -> None:
        """Apply a role picked in a column's dropdown and record it.

        Connected to ``CentralTable.role_changed``. The role is set on the backend dataset
        (the backend moves a single-use role such as X or Y away from the column that had it,
        which then becomes Ignore). For every role except ``Ignore`` a row is recorded with the
        action ``Set <role>``, the details ``Set column as <role>``, the column as target and a
        ``SetRoleStep`` such as ``SetRoleStep({"x": "Time"})`` (role names are converted by
        :meth:`_role_key`). Choosing ``Ignore`` changes the dataset but records nothing. The
        role dropdowns are then redrawn from the backend roles and the status bar counts
        updated; :meth:`_refresh_all` is not called, so the new row shows in Build Protocol at
        the next full refresh.

        Errors, for example a column that the backend dataset does not contain, are reported
        as "Role update failed".

        :param column: Name of the column whose dropdown changed.
        :param role: The chosen role label, for example ``"X"`` or ``"Y Error"``.
        """
        try:
            self.state.set_role(column, role)
            if role != "Ignore":
                key = self._role_key(role)
                self._append_sequence(
                    f"Set {role}",
                    f"Set column as {role}",
                    column,
                    workflow_step=SetRoleStep({key: column}),
                )
            self.central_table.set_roles(self.state.roles)
            self.status.update_state(self.state)
        except Exception as exc:
            self._error("Role update failed", exc)

    def rename_column(self, old_name: str, new_name: str) -> None:
        """Rename a column in the backend and record a ``RenameColumnStep``.

        Connected to ``CentralTable.column_renamed``, emitted after the user renames a column
        (double-click on the header, or *Rename Column* in the header's context menu) and the
        table has already changed its header. When the backend dataset has a column called
        ``old_name``, its 1-based column number is looked up and the column is renamed there
        with :meth:`physplot.PhysPlot.rename_column`; otherwise the number is taken from a
        default name such as ``Column 4`` (or left as ``None``) and the backend is not
        changed. In both cases a *Rename Column* row (``old -> new``, target the new name) is
        recorded with ``RenameColumnStep(old_name, new_name, old_column_number=<number>)``, so
        a replay can fall back to the column number when no column has the old name. The
        window is refreshed.
        Errors are reported as "Column rename failed".

        :param old_name: The column's previous name.
        :param new_name: The column's new name.
        """
        try:
            old_number = self._column_number_from_name(old_name)
            if self.state.pp.dataset is not None and old_name in self.state.pp.dataset.dataframe.columns:
                old_number = self.state.pp.dataset.get_column_number(old_name)
                self.state.pp.rename_column(old_name, new_name)
            self._append_sequence(
                "Rename Column",
                f"{old_name} -> {new_name}",
                new_name,
                workflow_step=RenameColumnStep(old_name, new_name, old_column_number=old_number),
            )
            self._refresh_all()
        except Exception as exc:
            self._error("Column rename failed", exc)

    def record_cell_edit(self, row_index: int, column: str, value: str, column_number: int) -> None:
        """Record one edited cell as a ``SetCellValueStep``.

        Connected to ``CentralTable.cell_value_changed``, which fires for each cell the user
        types into and for each cell filled by a paste. Adds an *Edit Cell* row with the
        details ``Row <row>, <column>`` and the new value as target, linked to
        ``SetCellValueStep(row_index, column, value, column_number=column_number)``. The new
        value itself reaches the backend through :meth:`sync_table_to_backend`, which runs on
        the ``table_edited`` signal. The window is not refreshed here.

        :param row_index: 1-based data row number, as shown in the row header.
        :param column: Name of the edited column.
        :param value: The cell's new text.
        :param column_number: 1-based column position, used on replay when the name is not
            found.
        """
        self._append_sequence(
            "Edit Cell",
            f"Row {row_index}, {column}",
            value,
            workflow_step=SetCellValueStep(row_index, column, value, column_number=column_number),
        )

    def record_row_delete(self, row_indices: list[int]) -> None:
        """Record deleted table rows as a ``DeleteRowsStep``.

        Connected to ``CentralTable.rows_deleted`` (*Delete Row* in the row-number context
        menu). Adds a *Delete Rows* row with the details ``Rows 3, 4`` and the target
        ``Table``, linked to ``DeleteRowsStep(row_indices)``. The rows have already been
        removed from the table; the backend dataset follows through
        :meth:`sync_table_to_backend`. The window is not refreshed here.

        :param row_indices: 1-based data row numbers that were deleted, in ascending order.
        """
        self._append_sequence(
            "Delete Rows",
            f"Rows {', '.join(str(row) for row in row_indices)}",
            "Table",
            workflow_step=DeleteRowsStep(row_indices),
        )

    def record_column_delete(self, columns: list[str], column_numbers: list[int]) -> None:
        """Record deleted table columns as a ``DeleteColumnsStep``.

        Connected to ``CentralTable.columns_deleted`` (*Delete Column* in the header context
        menu). Adds a *Delete Columns* row with the column names as details and the target
        ``Table``, linked to ``DeleteColumnsStep(columns, column_numbers=column_numbers)``.
        The columns have already been removed from the table; the backend dataset follows
        through :meth:`sync_table_to_backend`. The window is not refreshed here.

        :param columns: Names of the deleted columns.
        :param column_numbers: Their 1-based positions before the deletion.
        """
        self._append_sequence(
            "Delete Columns",
            ", ".join(columns),
            "Table",
            workflow_step=DeleteColumnsStep(columns, column_numbers=column_numbers),
        )

    def apply_simple_transform(self, input_column: str, output: str, function_name: str | dict, multiplier: float, offset: float):
        """Apply a built-in or plugin transformation to a column, as Simple Mode's *Apply* does.

        Does nothing when ``input_column`` is empty. When the input column has no non-blank
        cell in the table, the status reads ``Enter or import data before applying a
        transformation`` and nothing else happens. An empty ``output`` means "overwrite the
        input column".

        A plugin entry (a dict with a ``module``) is handed to :meth:`_apply_function_plugin`,
        which passes ``multiplier`` and ``offset`` to the plugin. Built-in functions are mapped
        to backend parameters:

        * ``identity`` runs the backend ``multiply`` with ``factor=multiplier`` (so the
          protocol shows ``multiply``);
        * ``multiply`` uses ``factor=multiplier``;
        * ``add`` and ``subtract`` use ``value=offset``;
        * ``divide`` uses ``divisor=multiplier`` (``1`` when the multiplier is 0);
        * every other function runs without parameters.

        Each call goes through :meth:`_apply_transform`. For any built-in function other than
        ``add`` and ``subtract``, a non-zero ``offset`` is then applied by a second ``add``
        transformation on the output column, which is recorded as a separate protocol row.

        :param input_column: Name of the source column.
        :param output: Name of the output column; a new name adds a column and an existing
            name overwrites that column.
        :param function_name: A backend function name, or a plugin entry from
            :meth:`simple_function_entries`.
        :param multiplier: Factor for ``identity``, ``multiply`` and ``divide``; passed to
            plugins.
        :param offset: Value added to the result; used directly by ``add`` and ``subtract``.
        """
        if not input_column:
            return
        if not self._column_has_values(input_column):
            self.status.set_message("Enter or import data before applying a transformation")
            return
        output = output or input_column
        if isinstance(function_name, dict) and function_name.get("module") is not None:
            self._apply_function_plugin(input_column, output, function_name, multiplier, offset)
            return
        params = {}
        function_to_run = function_name
        if function_name == "identity":
            function_to_run = "multiply"
            params["factor"] = multiplier
        elif function_name == "multiply":
            params["factor"] = multiplier
        elif function_name in {"add", "subtract"}:
            params["value"] = offset
        elif function_name == "divide":
            params["divisor"] = multiplier or 1
        self._apply_transform({"input": input_column, "function": function_to_run, "params": params, "output": output})
        if function_name not in {"add", "subtract"} and offset:
            self._apply_transform({"input": output, "function": "add", "params": {"value": offset}, "output": output})

    def apply_backend_transform(
        self,
        input_column: str,
        function_entry: str | dict,
        multiplier: float,
        offset: float,
        output: str,
    ) -> None:
        """Run the transformation configured in Simple Mode's *Mathematical Transformation*.

        Called by the panel's *Apply* button with the *Input* column, the selected *Function*
        entry, a multiplier of ``1.0``, the ``+`` offset and the *Output* text. Does nothing
        when no input column is selected. The function name is read from the entry's
        ``function_name`` (built-in functions) or ``display_name`` (plugins); plugin entries
        are passed on whole so the plugin module can be used. An empty output defaults to
        ``<input>_<function name>``. The work is done by :meth:`apply_simple_transform`.

        :param input_column: Name of the source column.
        :param function_entry: An entry from :meth:`simple_function_entries`, or a function
            name.
        :param multiplier: Factor passed on to :meth:`apply_simple_transform`.
        :param offset: Offset passed on to :meth:`apply_simple_transform`.
        :param output: Name of the output column, or an empty string for the default name.
        """
        if not input_column:
            return
        if isinstance(function_entry, dict):
            function_name = function_entry.get("function_name") or function_entry.get("display_name", "")
            function_to_run = function_entry if function_entry.get("module") is not None else function_name
        else:
            function_name = str(function_entry)
            function_to_run = function_name
        output = output or f"{input_column}_{function_name}"
        self.apply_simple_transform(input_column, output, function_to_run, multiplier, offset)

    def _column_has_values(self, column_name: str) -> bool:
        """Return whether a table column contains at least one non-blank cell.

        Reads the whole central table (without trimming), so it reflects what the user sees
        rather than the backend dataset.

        :param column_name: Column name as shown in the table.
        :returns: ``False`` when the column does not exist or all its cells are empty or
            whitespace.
        """
        df = self.central_table.to_dataframe(trim_empty=False)
        if column_name not in df.columns:
            return False
        return df[column_name].astype(str).str.strip().ne("").any()

    def _apply_function_plugin(self, input_column: str, output_column: str, entry: dict, multiplier: float, offset: float) -> None:
        """Apply a transformation plugin from ``config/transformations``.

        Runs :meth:`_apply_transform` with the plugin's file stem (``entry["name"]``) as the
        backend function name, ``multiplier`` and ``offset`` as parameters and the plugin's
        ``display_name`` as the label shown in the protocol row's details.

        :param input_column: Name of the source column.
        :param output_column: Name of the output column.
        :param entry: The plugin entry (keys ``name`` and ``display_name`` are used).
        :param multiplier: Passed to the plugin as ``multiplier``.
        :param offset: Passed to the plugin as ``offset``.
        """
        # The backend resolves the plugin by file stem, so the recorded
        # TransformColumnStep replays in sequences, exports and bulk runs.
        self._apply_transform(
            {
                "input": input_column,
                "function": entry["name"],
                "params": {"multiplier": multiplier, "offset": offset},
                "output": output_column,
                "label": entry["display_name"],
            }
        )

    def add_pipeline_step(self, payload: dict) -> None:
        """Apply a pipeline-style transformation; same as :meth:`apply_pipeline_step`.

        :param payload: See :meth:`apply_pipeline_step`.
        """
        self.apply_pipeline_step(payload)

    def apply_pipeline_step(self, payload: dict) -> None:
        """Apply a transformation described by a pipeline-style payload.

        The payload's ``params`` text, such as ``"factor=2, value=0.5"``, is parsed by
        :meth:`_parse_params` (numbers become floats). The function defaults to ``multiply``
        and the output to ``<input>_<function>``. The transformation then runs through
        :meth:`_apply_transform`, which records it. No control in the bundled panels calls this
        method.

        :param payload: A dict with the keys ``input``, ``function``, ``params`` (text) and
            ``output`` (optional).
        """
        params = self._parse_params(payload.get("params", ""))
        step = {
            "input": payload.get("input", ""),
            "function": payload.get("function", "multiply"),
            "params": self._format_params(params),
            "output": payload.get("output") or f"{payload.get('input')}_{payload.get('function')}",
        }
        self._apply_transform({**step, "params": params})

    def _apply_transform(self, step: dict) -> None:
        """Run one column transformation in the backend and record it.

        This is where every GUI transformation ends up. The table is synced to the backend
        first, then :meth:`physplot.PhysPlot.transform` computes the output column (adding it,
        or overwriting an existing column of that name) and records a
        ``TransformColumnStep`` in ``pp.workflow``. A display entry (with the parameters
        formatted by :meth:`_format_params`) is appended to ``state.transformations``, the
        table is redrawn from the backend dataset, and a *Transform* protocol row is added
        with the label (or function name) as details and ``<input> -> <output>`` as target,
        linked to the step the backend recorded. The status then reads ``Transformation
        applied`` and the window is refreshed.

        Errors are reported as "Transformation failed". When the backend call itself fails
        (for example an input column without numeric values or an unknown function), nothing
        is recorded.

        :param step: A dict with the keys ``input``, ``function``, ``output``, ``params`` (a
            dict of keyword arguments for the function, optional) and ``label`` (optional text
            for the protocol row).
        """
        self.sync_table_to_backend()
        try:
            self.state.pp.transform(step["input"], step["function"], output=step["output"], **step.get("params", {}))
            workflow_index = len(self.state.pp.workflow) - 1 if self.state.pp.workflow else None
            display_step = {
                "input": step["input"],
                "function": step["function"],
                "params": self._format_params(step.get("params", {})),
                "output": step["output"],
            }
            self.state.transformations.append(display_step)
            self.central_table.set_dataframe(self.state.dataframe, self.state.roles)
            self._append_sequence(
                "Transform",
                step.get("label") or step["function"],
                f"{step['input']} -> {step['output']}",
                workflow_index=workflow_index,
            )
            self.status.set_message("Transformation applied")
            self._refresh_all()
        except Exception as exc:
            self._error("Transformation failed", exc)

    def generate_module_plot(self, plotter_id: str, plot_type: str, style_module=None, fit_config=None) -> None:
        """Draw a plot with the selected plotter module, as Simple Mode's *Generate Plot* does.

        Does nothing when no plotter is selected. The table is synced to the backend first. A
        ``fit_config`` is passed to the backend as ``lsq_fit=fit_config`` so a least-squares
        fit is overlaid. Then, by plotter:

        * ``"basic"`` (Basic Plotter): :meth:`physplot.PhysPlot.plot_with_module` draws the
          figure and records a ``PlotModuleStep`` (including the fit settings); the Template is
          applied and the figure opens in the Figure Editor (:meth:`_open_figureforge_editor`).
        * A loader-declared callable plotter (id ``"loader:<name>"``): run by
          :meth:`_run_custom_plotter`; no backend step is recorded, so the protocol row is
          display-only. Asking for an LSQ fit raises "LSQ fit from Simple Mode is available for
          backend plotter modules.". The Template is applied and the figure is shown in a
          PhysPlot plot dialog (:meth:`_show_module_figure`).
        * Any other backend plotter: drawn and recorded like the Basic Plotter, with the
          Template applied, but shown in a PhysPlot plot dialog titled
          ``PhysPlot - <plotter>: <plot type>``.

        The Template is applied to the figure after the backend call and is not part of the
        recorded step. A *Generate Plot* row with the details ``Create <plotter> <plot type>``
        and the target ``Plotter Module`` is added, the status reads ``Plot generated`` and the
        window is refreshed. Errors are reported as "Plot failed"; if the error happens after
        the backend call, the ``PlotModuleStep`` is already recorded in ``pp.workflow`` but has
        no protocol row.

        :param plotter_id: Id from :meth:`plotter_entries`, for example ``"basic"``.
        :param plot_type: Plot type from :meth:`plot_type_entries`, for example ``"scatter"``.
        :param style_module: Path of the template JSON file, or ``None`` for no template.
        :param fit_config: The panel's LSQ fit settings (``enabled``, ``expression``,
            ``parameters``, ``initial``, ``label``, ``line_style``, ``line_width``,
            ``show_legend``), or ``None`` when *LSQ fit* is not ticked.
        """
        if not plotter_id:
            return
        self.sync_table_to_backend()
        try:
            plot_config = {"lsq_fit": fit_config} if fit_config else {}
            if plotter_id == "basic":
                figure = self.state.pp.plot_with_module(plotter_id, plot_type, **plot_config)
                workflow_index = len(self.state.pp.workflow) - 1 if self.state.pp.workflow else None
                apply_style_module(figure, style_module)
                self._open_figureforge_editor(figure)
            elif plotter_id in self._custom_plotters:
                if fit_config:
                    raise ValueError("LSQ fit from Simple Mode is available for backend plotter modules.")
                figure = self._run_custom_plotter(plotter_id, plot_type)
                workflow_index = None
                apply_style_module(figure, style_module)
                self._show_module_figure(figure, f"{plotter_id}: {plot_type}")
            else:
                figure = self.state.pp.plot_with_module(plotter_id, plot_type, **plot_config)
                workflow_index = len(self.state.pp.workflow) - 1 if self.state.pp.workflow else None
                apply_style_module(figure, style_module)
                self._show_module_figure(figure, f"{plotter_id}: {plot_type}")
            self._append_sequence(
                "Generate Plot",
                plot_details(plotter_id, plot_type, fit_config),
                "Plotter Module",
                workflow_index=workflow_index,
            )
            self.status.set_message("Plot generated")
            self._refresh_all()
        except Exception as exc:
            self._error("Plot failed", exc)

    def _run_custom_plotter(self, plotter_id: str, plot_type: str):
        """Call a plotter function declared by a loader plugin and return its figure.

        The function is tried with these call forms, in order, moving on only when a call
        raises ``TypeError``:

        1. ``function(dataset, plot_type=plot_type, config=config)``
        2. ``function(dataset, plot_type)``
        3. ``function(dataset)``
        4. ``function(dataframe, roles=column_roles, metadata=metadata, plot_type=plot_type)``
        5. ``function(dataframe)``

        When every form raises ``TypeError``, ``function(dataset)`` is called once more and its
        error propagates. A ``TypeError`` raised inside the plotter itself is treated the same
        way as a signature mismatch. ``config`` is a copy of the entry's declared ``config``.
        The figure is stored as ``state.pp.last_figure`` so *Export Plot* can save it.

        :param plotter_id: A ``"loader:<name>"`` id present in ``self._custom_plotters``.
        :param plot_type: The selected plot type.
        :returns: The figure returned by the plotter function.
        """
        entry = self._custom_plotters[plotter_id]
        function = entry["callable"]
        dataset = self.state.pp.get_active_dataset()
        config = dict(entry.get("config") or {})
        for call in (
            lambda: function(dataset, plot_type=plot_type, config=config),
            lambda: function(dataset, plot_type),
            lambda: function(dataset),
            lambda: function(dataset.dataframe, roles=dataset.column_roles, metadata=dataset.metadata, plot_type=plot_type),
            lambda: function(dataset.dataframe),
        ):
            try:
                figure = call()
                break
            except TypeError:
                continue
        else:
            figure = function(dataset)
        self.state.pp.last_figure = figure
        return figure

    def export_module_plot(self) -> None:
        """Save the most recently generated plot to an image file.

        Triggered by Simple Mode's *Export Plot* button. Uses ``state.pp.last_figure``; when no
        plot has been generated yet, "Export plot failed" is reported with "Generate a plot
        before exporting.". Otherwise an *Export Plot* save dialog opens with the suggested
        file ``physplot_plot.png`` in the current working directory and the filters PNG, PDF,
        SVG and All Files, and the figure is saved at 300 dpi. The status then reads ``Plot
        exported``; errors are reported as "Export plot failed". Changes made in the Figure
        Editor are not included, because they live in the editor's own process. Nothing is
        recorded in the protocol.
        """
        figure = getattr(self.state.pp, "last_figure", None)
        if figure is None:
            self._error("Export plot failed", RuntimeError("Generate a plot before exporting."))
            return
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Export Plot",
            str(Path.cwd() / "physplot_plot.png"),
            "PNG Files (*.png);;PDF Files (*.pdf);;SVG Files (*.svg);;All Files (*)",
        )
        if not path:
            return
        try:
            figure.savefig(path, dpi=300)
            self.status.set_message("Plot exported")
        except Exception as exc:
            self._error("Export plot failed", exc)

    def _show_module_figure(self, figure, title: str) -> None:
        """Show a figure in a non-modal PhysPlot plot dialog.

        The dialog is titled ``PhysPlot - <title>``, opens at 820 x 620 px and holds the
        Matplotlib navigation toolbar (pan, zoom, save) above a Qt canvas with the figure. A
        reference is kept in ``self._module_plot_dialogs`` and the dialog is shown without
        blocking, so several plots can stay open.

        :param figure: The Matplotlib figure to show.
        :param title: Text after ``PhysPlot -`` in the window title; callers pass
            ``"<plotter id>: <plot type>"``.
        """
        from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
        from matplotlib.backends.backend_qtagg import NavigationToolbar2QT

        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle(f"PhysPlot - {title}")
        dialog.resize(820, 620)
        layout = QtWidgets.QVBoxLayout(dialog)
        canvas = FigureCanvas(figure)
        toolbar = NavigationToolbar2QT(canvas, dialog)
        layout.addWidget(toolbar)
        layout.addWidget(canvas)
        canvas.draw()
        self._module_plot_dialogs = getattr(self, "_module_plot_dialogs", [])
        self._module_plot_dialogs.append(dialog)
        dialog.show()

    def delete_pipeline_step(self, index: int) -> None:
        """Remove one entry from the display list of applied transformations.

        Only ``state.transformations`` changes: the column the transformation created, the
        backend sequence and the protocol rows stay as they are. Out-of-range indices are
        ignored. No control in the bundled panels calls this method.

        :param index: Position of the entry in ``state.transformations``.
        """
        if 0 <= index < len(self.state.transformations):
            self.state.transformations.pop(index)
            self._refresh_all()

    def clear_pipeline(self) -> None:
        """Empty the display list of applied transformations.

        Only ``state.transformations`` is cleared; table data, the backend sequence and the
        protocol rows are unchanged. No control in the bundled panels calls this method.
        """
        self.state.transformations.clear()
        self._refresh_all()

    def import_pipeline(self) -> None:
        """Load the display list of transformations from a pipeline JSON file.

        An *Import Pipeline* dialog opens in the writable ``config/pipelines`` folder. The
        chosen file's JSON content replaces ``state.transformations``; the transformations are
        not applied to the data and nothing is recorded in the protocol. Errors are reported
        as "Import pipeline failed". No control in the bundled panels calls this method.
        """
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Import Pipeline",
            str(writable_plugin_dir("pipelines")),
            "JSON Files (*.json)",
        )
        if not path:
            return
        try:
            self.state.transformations = json.loads(Path(path).read_text(encoding="utf-8"))
            self._refresh_all()
        except Exception as exc:
            self._error("Import pipeline failed", exc)

    def export_pipeline(self) -> None:
        """Save the display list of applied transformations as a pipeline JSON file.

        An *Export Pipeline* save dialog suggests ``pipeline.json`` in the writable
        ``config/pipelines`` folder. ``state.transformations`` (one ``{"input", "function",
        "params", "output"}`` entry per applied transformation, with ``params`` as display
        text) is written as indented JSON and the status reads ``Pipeline exported``. Write
        errors are not caught here. No control in the bundled panels calls this method.
        """
        default_path = writable_plugin_dir("pipelines") / "pipeline.json"
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Export Pipeline", str(default_path), "JSON Files (*.json)")
        if path:
            Path(path).write_text(json.dumps(self.state.transformations, indent=2), encoding="utf-8")
            self.status.set_message("Pipeline exported")

    def fit_model(self) -> None:
        """Fit a straight line to the X and Y role columns in the backend.

        Syncs the table, then calls :meth:`physplot.PhysPlot.fit` with ``"linear"``, which
        stores the slope and intercept in ``state.pp.fit_result`` (see
        :meth:`show_fit_results`). The status reads ``Fit complete`` and the window is
        refreshed. The fit is not recorded in the protocol. Errors, such as a missing X or Y
        role, are reported as "Fit failed". No control in the bundled panels calls this
        method; Simple Mode fits through the *LSQ fit* option of :meth:`generate_module_plot`.
        """
        try:
            self.sync_table_to_backend()
            self.state.pp.fit("linear")
            self.status.set_message("Fit complete")
            self._refresh_all()
        except Exception as exc:
            self._error("Fit failed", exc)

    def show_fit_results(self) -> None:
        """Show the backend's last fit result in a *Fit Results* message box.

        Each entry of ``state.pp.fit_result`` is shown on its own ``key: value`` line (for a
        linear fit: kind, x, y, slope and intercept; for an LSQ fit from a plot: method,
        expression and parameters). Without a result the box reads "No fit result yet.". No
        control in the bundled panels calls this method.
        """
        result = self.state.pp.fit_result
        text = "No fit result yet."
        if result:
            text = "\n".join(f"{key}: {value}" for key, value in result.items())
        QtWidgets.QMessageBox.information(self, "Fit Results", text)

    def start_recording(self) -> None:
        """Set the backend's recording flag and log a display-only *Start Tracking* row.

        Calls :meth:`physplot.PhysPlot.start_recording` and adds a row reading "Sequence
        tracking is always on" with the target ``Advanced``; it has no backend step. The GUI
        records every action regardless of this flag. No control in the bundled panels calls
        this method.
        """
        self.state.pp.start_recording()
        self._append_sequence("Start Tracking", "Sequence tracking is always on", "Advanced")
        self._refresh_all()

    def stop_recording(self) -> None:
        """Log a display-only *Tracking* row and clear the backend's recording flag.

        Adds a row reading "Sequence tracking stays on" with the target ``Advanced`` (no
        backend step), then calls :meth:`physplot.PhysPlot.stop_recording`. The GUI keeps
        recording every action regardless of this flag. No control in the bundled panels
        calls this method.
        """
        self._append_sequence("Tracking", "Sequence tracking stays on", "Advanced")
        self.state.pp.stop_recording()
        self._refresh_all()

    def save_workflow(self) -> None:
        """Save the protocol as a runnable ``Sequence.py`` file.

        Triggered by *Protocol > Export Sequence.py...* (``Ctrl+S``) and the *Export
        Sequence.py* button of Build Protocol. A *Save Sequence.py* dialog suggests
        ``sequence.py`` in the writable ``config/sequences`` folder. The backend writes the
        same Python source that *Copy Sequence Code* produces
        (:meth:`physplot.PhysPlot.save_workflow`): a ``WORKFLOW_STEPS`` list plus
        ``build_workflow()`` and ``run()`` helpers, usable from notebooks, scripts or
        ``physplot run-workflow``. The file becomes ``state.workflow_file`` (shown as
        ``Workflow:`` in the Advanced Mode status bar), the status reads ``Sequence saved``
        and the window is refreshed. Errors are reported as "Save workflow failed".
        """
        default_path = writable_plugin_dir("sequences") / "sequence.py"
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save Sequence.py",
            str(default_path),
            "Python Files (*.py)",
        )
        if not path:
            return
        try:
            self.state.pp.save_workflow(path)
            self.state.workflow_file = Path(path)
            self.status.set_message("Sequence saved")
            self._refresh_all()
        except Exception as exc:
            self._error("Save workflow failed", exc)

    def open_workflow(self) -> None:
        """Replace the protocol with the steps of a ``Sequence.py`` file.

        Triggered by *Protocol > Import Sequence.py...* and the *Import Sequence.py* button of
        Build Protocol. A *Load Sequence.py* dialog opens in the writable
        ``config/sequences`` folder. The chosen file is executed as Python by
        :meth:`physplot.PhysPlot.load_workflow` and must define ``WORKFLOW_STEPS`` or
        ``build_workflow()``. Its steps replace ``pp.workflow``, the protocol rows are rebuilt
        from them (:meth:`_sequence_rows_from_steps`), the file becomes
        ``state.workflow_file`` and the status reads ``Sequence loaded``. The steps are not run
        and the table is not changed; use *Apply This Sequence* to replay them. Errors are
        reported as "Load sequence failed" and leave the protocol as it was. The window is
        refreshed whenever a file was chosen.
        """
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Load Sequence.py",
            str(writable_plugin_dir("sequences")),
            "Python Files (*.py)",
        )
        if path:
            try:
                steps = self.state.pp.load_workflow(path)
                self.state.pp.workflow = list(steps)
                self.state.timeline = self._sequence_rows_from_steps(steps)
                self.state.workflow_file = Path(path)
                self.status.set_message("Sequence loaded")
            except Exception as exc:
                self._error("Load sequence failed", exc)
            self._refresh_all()

    def run_workflow(self) -> None:
        """Replay the current protocol; same as :meth:`apply_current_sequence`."""
        self.apply_current_sequence()

    def apply_current_sequence(self) -> None:
        """Replay the whole protocol on the table and show each row's status.

        Triggered by *Protocol > Apply This Sequence* (``Ctrl+R``) and the *Apply This
        Sequence* button of Build Protocol. With an empty protocol, "Apply sequence failed" is
        reported with "Build or import a protocol sequence first.". Otherwise
        :meth:`_run_current_sequence` replays every step from the first one, redraws the table
        and fills the Status column (OK, Failed or Skipped), and the status reads
        ``Sequence complete``.

        When a step fails, the replay stops there, later steps are Skipped and the table keeps
        the state reached before the failure. The failure is reported as "Apply sequence
        failed" with the text ``Row N failed (<StepName>): <error>`` (a dialog, or stderr on
        the offscreen platform), and the status bar keeps that text. An exception raised by the
        run itself (outside the per-step results) is also reported as "Apply sequence failed".
        """
        if not self.state.pp.workflow:
            self._error("Apply sequence failed", RuntimeError("Build or import a protocol sequence first."))
            return
        try:
            failure = self._run_current_sequence("Sequence complete")
        except Exception as exc:
            self._error("Apply sequence failed", exc)
            return
        if failure is not None:
            message = self._failure_message(failure)
            self._error("Apply sequence failed", RuntimeError(message))
            self.status.set_message(message)

    def _run_current_sequence(self, status_message: str):
        """Replay the whole sequence on the table and report per-step status.

        Returns the failing ``StepResult`` or ``None``. The table always shows
        the state reached before the failure, and the Status column shows
        which rows ran, failed, or were skipped.

        The table is synced to the backend first, then a copy of ``pp.workflow`` runs from its
        first step through :meth:`physplot.PhysPlot.run_workflow_detailed` with
        ``allow_column_number_fallback=True`` (a step whose column name is missing may use the
        recorded column number instead). A ``LoadDataStep`` at the start reads its file from
        disk again. The run saves state snapshots before the steps (the backend keeps a limited
        number), which :meth:`rerun_from_timeline_step` can resume from. Step failures do not
        raise; they are returned. The results are shown by :meth:`_show_sequence_results`,
        which also sets the status bar to ``status_message`` or to the failure text.

        Used by :meth:`apply_current_sequence` and by ``delete_timeline_step`` (with the
        message ``Sequence updated``).

        :param status_message: Status bar text to show when every step succeeds.
        :returns: The first failed :class:`physplot.execution.StepResult`, or ``None``.
        """
        self.sync_table_to_backend()
        steps = list(self.state.pp.workflow)
        results = self.state.pp.run_workflow_detailed(steps, allow_column_number_fallback=True)
        return self._show_sequence_results(results, status_message)

    def rerun_from_timeline_step(self, row_index: int) -> None:
        """Resume the sequence at a table row without replaying earlier rows.

        Triggered by *Rerun from this step* in the context menu of a Build Protocol row. The
        backend restores the state it saved before the row's first step during an earlier run
        (:meth:`physplot.PhysPlot.rerun_from`; when that snapshot is no longer kept, the latest
        valid earlier one is used) and runs from there to the end, so edits to that step or
        later ones take effect. Steps before the resume point are reported as OK. The results
        are shown like a full run
        (:meth:`_show_sequence_results`) with the status ``Reran from row N``, or the failure
        text when a step fails.

        Out-of-range rows are ignored. A row without backend steps (a display-only row) only
        sets the status to ``Row N has no replayable step``. When no saved state is usable
        (for example no full run yet, or earlier steps changed since that run), the backend's
        error is reported as "Rerun failed".

        :param row_index: 0-based row index in the protocol table.
        """
        if not 0 <= row_index < len(self.state.timeline):
            return
        indices = self._row_workflow_indices(self.state.timeline[row_index])
        if not indices:
            self.status.set_message(f"Row {row_index + 1} has no replayable step")
            return
        try:
            results = self.state.pp.rerun_from(min(indices), allow_column_number_fallback=True)
        except Exception as exc:
            self._error("Rerun failed", exc)
            return
        self._show_sequence_results(results, f"Reran from row {row_index + 1}")

    def _show_sequence_results(self, results, status_message: str):
        """Show the outcome of a sequence run in the table, status bar and protocol table.

        Redraws the central table from the backend dataset (when there is one) and makes the
        dataset's source file, if any, the status bar's *File*. Sets the status to the
        failure text from :meth:`_failure_message`, or to ``status_message`` when every step
        succeeded, and runs :meth:`_refresh_all`, which fills the Status column from
        ``pp.last_results``. No dialog is shown here.

        :param results: The ``StepResult`` list returned by the backend run.
        :param status_message: Status bar text for a fully successful run.
        :returns: The first failed ``StepResult``, or ``None``.
        """
        failure = first_failure(results)
        if self.state.pp.dataset is not None:
            self.central_table.set_dataframe(self.state.dataframe, self.state.roles)
            source_path = self.state.pp.dataset.source_path
            if source_path:
                # A replayed File Loader step reloads its file; show that file as current.
                self.state.current_file = Path(source_path)
        self.status.set_message(self._failure_message(failure) if failure is not None else status_message)
        self._refresh_all()
        return failure

    def _failure_message(self, failure) -> str:
        """Describe a failed step in terms of the protocol table.

        :param failure: The failed ``StepResult``.
        :returns: ``"Row N failed (<StepName>): <error>"``, where N is the 1-based protocol row
            that holds the step, or ``"Step N failed ..."`` with the 1-based step number when
            no row links to it.
        """
        row = self._timeline_row_for_step(failure.index)
        where = f"Row {row + 1}" if row is not None else f"Step {failure.index + 1}"
        return f"{where} failed ({failure.step_name}): {failure.error}"

    def _timeline_row_for_step(self, step_index: int) -> int | None:
        """Find the protocol row that contains a backend step.

        :param step_index: 0-based index into ``pp.workflow``.
        :returns: The 0-based index of the first row of ``state.timeline`` linked to that
            step, or ``None`` when no row is.
        """
        for row_index, row in enumerate(self.state.timeline):
            if step_index in self._row_workflow_indices(row):
                return row_index
        return None

    @staticmethod
    def _row_workflow_indices(row: dict) -> list[int]:
        """Return the backend step indices a protocol row stands for.

        Uses the row's ``workflow_indices`` list when present; otherwise its single
        ``workflow_index`` when that is an integer. Non-integer values are dropped.

        :param row: A ``state.timeline`` row dict.
        :returns: Sorted, unique 0-based indices into ``pp.workflow``; empty for a
            display-only row.
        """
        workflow_indices = row.get("workflow_indices")
        if workflow_indices is None:
            workflow_index = row.get("workflow_index")
            workflow_indices = [workflow_index] if isinstance(workflow_index, int) else []
        return sorted({index for index in workflow_indices if isinstance(index, int)})

    def _current_step_results(self) -> dict:
        """Map step index to its latest result, ignoring results for edited steps.

        Reads ``state.pp.last_results`` from the most recent run. A result is kept only while
        the step object at its index in ``pp.workflow`` is still the very same object that
        ran, so rows whose steps were replaced (for example by *Apply Code to Table* or
        *Import Sequence.py*) or shifted show no status until the next run. Used by
        ``timeline_row_status`` to fill the Build Protocol Status column.

        :returns: A dict from 0-based step index to its ``StepResult``.
        """
        workflow = self.state.pp.workflow
        current = {}
        for result in getattr(self.state.pp, "last_results", None) or []:
            if 0 <= result.index < len(workflow) and workflow[result.index] is result.step:
                current[result.index] = result
        return current

    def timeline_row_status(self, row: dict) -> tuple[str | None, str | None]:
        """Return ``(status, tooltip)`` for a Build Protocol row."""
        results = self._current_step_results()
        row_results = [results[index] for index in self._row_workflow_indices(row) if index in results]
        if not row_results:
            return None, None
        failed = [result for result in row_results if result.status == STATUS_FAILED]
        if failed:
            return STATUS_FAILED, failed[0].error
        if any(result.status == STATUS_SKIPPED for result in row_results):
            failure = first_failure(list(results.values()))
            if failure is not None:
                row = self._timeline_row_for_step(failure.index)
                where = f"row {row + 1}" if row is not None else f"step {failure.index + 1}"
                return STATUS_SKIPPED, f"Not run because {where} failed."
            return STATUS_SKIPPED, "Not run."
        duration = sum(result.duration_s for result in row_results)
        return STATUS_OK, f"Completed in {duration * 1000:.0f} ms"

    def apply_sequence_code(self, source: str) -> None:
        steps = load_workflow_source(source, name="physplot_sequence_editor")
        self.state.pp.workflow = list(steps)
        self.state.timeline = self._sequence_rows_from_steps(steps)
        self.status.set_message("Sequence code applied")
        self._refresh_all()

    def workflow_manager(self) -> None:
        QtWidgets.QMessageBox.information(self, "Sequence Manager", "Sequence actions are available in the Advanced panel.")

    def copy_workflow_script(self) -> None:
        QtWidgets.QApplication.clipboard().setText(self.sequence_code_text())
        self.status.set_message("Sequence script copied")

    def sequence_code_text(self) -> str:
        return self.state.pp.workflow_script()

    def clear_recording(self) -> None:
        self.state.timeline.clear()
        self.state.pp.workflow.clear()
        self._refresh_all()

    def delete_timeline_step(self, index: int) -> None:
        if 0 <= index < len(self.state.timeline):
            row = self.state.timeline.pop(index)
            removed = sorted(self._row_workflow_indices(row), reverse=True)
            for workflow_index in removed:
                if 0 <= workflow_index < len(self.state.pp.workflow):
                    self.state.pp.workflow.pop(workflow_index)
            if removed:
                self._reindex_sequence_rows_after_delete(set(removed))
            if self.state.pp.workflow:
                try:
                    self._run_current_sequence("Sequence updated")
                except Exception as exc:
                    self._error("Apply revised sequence failed", exc)
                    self._refresh_all()
                # A failing step is reported in the Status column and status
                # bar rather than a modal dialog so the user can keep editing.
            else:
                self.status.set_message("Sequence cleared")
                self._refresh_all()

    def browse_input_folder(self, field: QtWidgets.QLineEdit) -> None:
        """Pick the bulk-run input folder (Run Sequence, *Input Folder* > *Browse*).

        Opens an *Input Folder* directory dialog in the current working directory and writes
        the chosen path into ``field``. Cancelling leaves the field unchanged.

        :param field: The *Input Folder* line edit of the Bulk Run panel.
        """
        self._browse_folder(field, "Input Folder")

    def browse_output_folder(self, field: QtWidgets.QLineEdit) -> None:
        """Pick the bulk-run output folder (Run Sequence, *Output Folder* > *Browse*).

        Opens an *Output Folder* directory dialog in the current working directory and writes
        the chosen path into ``field``. Cancelling leaves the field unchanged.

        :param field: The *Output Folder* line edit of the Bulk Run panel.
        """
        self._browse_folder(field, "Output Folder")

    def browse_workflow_file(self, field: QtWidgets.QLineEdit) -> None:
        """Pick a sequence file for a bulk run (Run Sequence, *Sequence File* > *Browse*).

        Opens a *Sequence File* dialog in the writable ``config/sequences`` folder, filtered to
        Python files, and writes the chosen path into ``field``. Cancelling leaves the field
        unchanged. When the field stays empty, the bulk run uses the current protocol.

        :param field: The *Sequence File* line edit of the Bulk Run panel.
        """
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Sequence File",
            str(writable_plugin_dir("sequences")),
            "Python Files (*.py)",
        )
        if path:
            field.setText(path)

    def run_bulk_workflow(self, payload: dict) -> None:
        """Run a sequence over every matching file of a folder and export each result.

        Triggered by *Run Bulk Workflow* on the Advanced Mode *Run Sequence* tab. The sequence
        is the *Sequence File* when one is given (the backend loads it), otherwise a copy of
        the current protocol, including its load step, whose loader plugin is reused for every
        file; an empty protocol raises "Build or import a protocol sequence before running bulk
        automation.". :meth:`physplot.PhysPlot.run_bulk` (:func:`physplot.bulk.run_folder`)
        then processes each matching file of the input folder in name order with a fresh
        backend, replays the sequence with ``allow_column_number_fallback=True`` and exports
        the result to ``<output folder>/<file stem>/`` (``data.csv``, ``columns.csv``,
        ``workflow.py`` and, when present, ``fit.json`` and ``plot.png``). Which files match
        depends on the sequence's load step: a plugin format limits the run to that file
        extension, otherwise the built-in table formats are used.

        On success the status reads ``Bulk complete: N outputs``. The run happens in the GUI
        thread, so the window does not respond until it ends. The first failing file stops the
        run; the error is reported as "Bulk run failed" with the message ``Bulk run stopped at
        <file name>: <error>`` and a note that files before it were exported and later files
        were not run. Other errors are reported as "Bulk run failed" as they are. The folder
        texts are passed to the backend without checks here. The table and the protocol are
        not changed.

        :param payload: The Bulk Run panel's fields: ``input_folder``, ``workflow_file`` (may
            be empty) and ``output_folder``.
        """
        try:
            workflow_file = payload.get("workflow_file")
            workflow = workflow_file
            if not workflow:
                if not self.state.pp.workflow:
                    raise RuntimeError("Build or import a protocol sequence before running bulk automation.")
                # Keep the load step: bulk runs reuse its loader plugin for every file.
                workflow = list(self.state.pp.workflow)
            outputs = self.state.pp.run_bulk(
                workflow,
                payload["input_folder"],
                payload["output_folder"],
                allow_column_number_fallback=True,
            )
            self.status.set_message(f"Bulk complete: {len(outputs)} outputs")
        except Exception as exc:
            input_path = getattr(exc, "input_path", None)
            if input_path is not None:
                exc = RuntimeError(
                    f"Bulk run stopped at {Path(input_path).name}: {exc}\n\n"
                    "Files before it in the input folder were exported; later files were not run."
                )
            self._error("Bulk run failed", exc)

    def _browse_folder(self, field: QtWidgets.QLineEdit, title: str) -> None:
        """Ask for a folder and put its path into a line edit.

        :param field: The line edit that receives the chosen path.
        :param title: Title of the directory dialog, which opens in the current working
            directory. Cancelling leaves the field unchanged.
        """
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, title, str(Path.cwd()))
        if folder:
            field.setText(folder)

    def _append_sequence(
        self,
        action: str,
        details: str,
        target: str,
        workflow_step=None,
        workflow_steps: list | None = None,
        workflow_index=None,
    ) -> None:
        """Record one protocol row and, when given, its backend steps.

        This is the single place where the GUI adds rows to the protocol:

        1. Each step in ``workflow_steps`` is appended to ``state.pp.workflow`` and its index
           remembered.
        2. ``workflow_step``, when given, is appended as well and becomes the row's
           ``workflow_index``.
        3. Otherwise an integer ``workflow_index`` links the row to a step that the backend
           already recorded (transformations and plots).

        A row dict with the keys ``action``, ``details``, ``target``, ``workflow_index``,
        ``workflow_indices`` (``None`` when no step is linked) and ``code`` (a one-line code
        preview of the linked steps from :meth:`_sequence_code_for_indices`) is appended to
        ``state.timeline``. Without any step the row is display-only and is skipped by
        replays. The widgets are not refreshed here; callers do that.

        :param action: The *Operation* column text, for example ``"Transform"``.
        :param details: The *Details* column text.
        :param target: The *Target/File/Column* column text.
        :param workflow_step: One new step object to append to the backend sequence.
        :param workflow_steps: Several new step objects to append, in order (used for a load
            step followed by its role step).
        :param workflow_index: Index of a step already in ``pp.workflow``; ignored when
            ``workflow_step`` is given.
        """
        workflow_indices = []
        if workflow_steps:
            for step in workflow_steps:
                self.state.pp.workflow.append(step)
                workflow_indices.append(len(self.state.pp.workflow) - 1)
        if workflow_step is not None:
            self.state.pp.workflow.append(workflow_step)
            workflow_index = len(self.state.pp.workflow) - 1
            workflow_indices.append(workflow_index)
        elif isinstance(workflow_index, int):
            workflow_indices.append(workflow_index)
        code = self._sequence_code_for_indices(workflow_indices)
        self.state.timeline.append(
            {
                "action": action,
                "details": details,
                "target": target,
                "workflow_index": workflow_index,
                "workflow_indices": workflow_indices or None,
                "code": code,
            }
        )
        self._schedule_timeline_refresh()

    def _schedule_timeline_refresh(self) -> None:
        """Show newly recorded rows in Build Protocol once control returns to the event loop.

        Role changes, cell edits and row or column deletions record a step without a full
        :meth:`_refresh_all`, so without this their rows would appear only after the next
        refresh. The update is batched: a paste that records one *Edit Cell* step per cell
        rebuilds the protocol table once, not once per cell.
        """
        if getattr(self, "_timeline_refresh_pending", False) or not hasattr(self, "mode_manager"):
            return
        self._timeline_refresh_pending = True
        QtCore.QTimer.singleShot(0, self._flush_timeline_refresh)

    def _flush_timeline_refresh(self) -> None:
        """Redraw the protocol table and status bar after :meth:`_schedule_timeline_refresh`."""
        self._timeline_refresh_pending = False
        self.mode_manager.refresh_timeline(self.state.timeline)
        self.status.update_state(self.state)

    def _record(self, action: str, details: str, target: str) -> None:
        """Add a display-only protocol row that is not linked to any backend step.

        :param action: The *Operation* column text.
        :param details: The *Details* column text.
        :param target: The *Target/File/Column* column text.
        """
        self._append_sequence(action, details, target)

    def _append_role_sequence_steps(self) -> None:
        """Record all current non-Ignore column roles as one *Column Roles* row.

        Adds a row with the details "Apply selected column roles" and the target "Role setup",
        linked to the ``SetRoleStep`` from :meth:`_role_step_from_current_roles`. Nothing is
        recorded when every column is Ignore. Nothing in the current GUI calls this method.
        """
        role_step = self._role_step_from_current_roles()
        if role_step is not None:
            self._append_sequence("Column Roles", "Apply selected column roles", "Role setup", workflow_step=role_step)

    def _role_step_from_current_roles(self):
        """Build a ``SetRoleStep`` from the backend's current column roles.

        Every column whose role is not Ignore contributes ``<role key>: <column>`` (keys from
        :meth:`_role_key`, for example ``{"x": "Time", "y": "Voltage"}``). When several
        columns share a role, the last one wins. Used by :meth:`import_data` to record the
        roles a loader set up.

        :returns: The ``SetRoleStep``, or ``None`` when every column is Ignore.
        """
        roles = {}
        for column, role in self.state.roles.items():
            if role == "Ignore":
                continue
            roles[self._role_key(role)] = column
        return SetRoleStep(roles) if roles else None

    def _reindex_sequence_rows_after_delete(self, removed: set[int]) -> None:
        """Fix the step links of all protocol rows after steps were removed.

        Called by ``delete_timeline_step`` after the deleted row's steps were popped from
        ``pp.workflow``. For every remaining row, each linked index is shifted down by the
        number of removed indices before it, links to removed steps are dropped (a
        ``workflow_index`` pointing at a removed step becomes ``None``), and the row's
        ``code`` preview is regenerated from the new links.

        :param removed: The 0-based indices, in the old numbering, of the removed steps.
        """
        def adjust(index):
            """Return ``index`` in the new numbering, or ``None`` if it was removed or invalid."""
            if not isinstance(index, int) or index in removed:
                return None
            return index - sum(1 for removed_index in removed if removed_index < index)

        for row in self.state.timeline:
            if isinstance(row.get("workflow_index"), int):
                row["workflow_index"] = adjust(row["workflow_index"])
            if row.get("workflow_indices"):
                row["workflow_indices"] = [
                    adjusted for adjusted in (adjust(index) for index in row["workflow_indices"]) if adjusted is not None
                ]
            row["code"] = self._sequence_code_for_indices(row.get("workflow_indices") or [row.get("workflow_index")])

    @staticmethod
    def _role_key(role: str) -> str:
        """Convert a role label from the dropdown into a ``SetRoleStep`` keyword.

        ``X`` -> ``x``, ``Y`` -> ``y``, ``X Error`` -> ``xerr``, ``Y Error`` -> ``yerr``,
        ``Group`` -> ``group``, ``Label`` -> ``label``, ``Batch Key`` -> ``batch_key`` and
        ``Fit Weight`` -> ``fit_weight``; the same keywords :meth:`physplot.PhysPlot.set_roles`
        accepts. Any other text is returned unchanged.

        :param role: The role label, for example ``"Y Error"``.
        :returns: The keyword, for example ``"yerr"``.
        """
        return {
            "X": "x",
            "Y": "y",
            "X Error": "xerr",
            "Y Error": "yerr",
            "Group": "group",
            "Label": "label",
            "Batch Key": "batch_key",
            "Fit Weight": "fit_weight",
        }.get(role, role)

    @staticmethod
    def _sequence_rows_from_steps(steps: list) -> list[dict]:
        """Build protocol table rows for a list of backend steps.

        Used when a whole step list arrives at once: *Import Sequence.py*
        (:meth:`open_workflow`), *Apply Code to Table* (``apply_sequence_code``) and *Insert
        Protocol Module* (``insert_protocol_module``). Each row links to the step's position
        in ``steps`` (``workflow_index`` and ``workflow_indices``) and carries a one-line
        ``code`` preview. Row texts by step type (*Operation*, *Details*, *Target*):

        * ``LoadDataStep``: "File Loader", ``"<loader label> (...)"`` (see
          :func:`loader_label`), and the file name. When the next step is a ``SetRoleStep``,
          it joins this row and the details end in "(column names and role setup)";
          otherwise "(column names)".
        * ``SetRoleStep`` with one role: "Set <Role>", "Set column as <Role>", the column.
          With several roles: "Set Roles", ``<Role>: <column>`` pairs, "Table".
        * ``TransformColumnStep``: "Transform", :func:`transform_label`, ``<input> -> <output>``.
        * ``CalculateColumnStep``: "Calculate", the formula as written, the output column.
        * ``PlotModuleStep``: "Generate Plot", :func:`plot_details`, "Plotter Module".
        * ``RenameColumnStep``: "Rename Column", ``<old> -> <new>``, the new name.
        * ``SetCellValueStep``: "Edit Cell", ``Row <row>, <column>``, the value.
        * ``DeleteRowsStep`` / ``DeleteColumnsStep``: "Delete Rows" / "Delete Columns",
          ``Rows <rows>`` or the column names, "Table".
        * Any other step: its class name, with empty details and target.

        These are the texts the live actions record, so a reopened sequence reads the same as
        it did while it was being recorded.

        :param steps: The ordered step objects.
        :returns: The row dicts, in order.
        """
        rows = []
        index = 0
        while index < len(steps):
            step = steps[index]
            if isinstance(step, LoadDataStep):
                workflow_indices = [index]
                has_role_setup = index + 1 < len(steps) and isinstance(steps[index + 1], SetRoleStep)
                if has_role_setup:
                    workflow_indices.append(index + 1)
                setup_note = "column names and role setup" if has_role_setup else "column names"
                row = {
                    "action": "File Loader",
                    "details": f"{loader_label(step)} ({setup_note})",
                    "target": Path(str(step.path)).name if step.path else "",
                    "workflow_index": index,
                    "workflow_indices": workflow_indices,
                }
                row["code"] = MainWindow._sequence_code_for_steps([steps[i] for i in workflow_indices])
                rows.append(row)
                index += 2 if has_role_setup else 1
                continue
            elif isinstance(step, SetRoleStep):
                roles = {ROLE_LABELS.get(key, key): column for key, column in (step.roles or {}).items()}
                if len(roles) == 1:
                    (role, column), = roles.items()
                    row = {"action": f"Set {role}", "details": f"Set column as {role}", "target": str(column)}
                else:
                    pairs = ", ".join(f"{role}: {column}" for role, column in roles.items())
                    row = {"action": "Set Roles", "details": pairs, "target": "Table"}
            elif isinstance(step, TransformColumnStep):
                row = {
                    "action": "Transform",
                    "details": transform_label(step.function_name),
                    "target": f"{step.input_column} -> {step.output}",
                }
            elif isinstance(step, CalculateColumnStep):
                row = {"action": "Calculate", "details": step.formula_original, "target": step.output}
            elif isinstance(step, PlotModuleStep):
                lsq_fit = step.config.get("lsq_fit") if isinstance(step.config, dict) else None
                row = {
                    "action": "Generate Plot",
                    "details": plot_details(step.plotter_id, step.plot_type, lsq_fit),
                    "target": "Plotter Module",
                }
            elif isinstance(step, RenameColumnStep):
                row = {
                    "action": "Rename Column",
                    "details": f"{step.old_column} -> {step.new_column}",
                    "target": step.new_column,
                }
            elif isinstance(step, SetCellValueStep):
                row = {
                    "action": "Edit Cell",
                    "details": f"Row {step.row_index}, {step.column}",
                    "target": str(step.value),
                }
            elif isinstance(step, DeleteRowsStep):
                row = {"action": "Delete Rows", "details": f"Rows {', '.join(map(str, step.row_indices))}", "target": "Table"}
            elif isinstance(step, DeleteColumnsStep):
                row = {"action": "Delete Columns", "details": ", ".join(step.columns), "target": "Table"}
            else:
                row = {"action": step.__class__.__name__, "details": "", "target": ""}
            row["workflow_index"] = index
            row["workflow_indices"] = [index]
            row["code"] = MainWindow._sequence_code_for_steps([step])
            rows.append(row)
            index += 1
        return rows

    def _sequence_code_for_indices(self, indices) -> str:
        """Return the one-line code preview for steps of the current sequence.

        :param indices: Indices into ``pp.workflow``; non-integers and out-of-range values
            are skipped. ``None`` is treated as empty.
        :returns: The joined preview from :meth:`_sequence_code_for_steps`, or ``""``.
        """
        indices = [index for index in (indices or []) if isinstance(index, int)]
        steps = [self.state.pp.workflow[index] for index in indices if 0 <= index < len(self.state.pp.workflow)]
        return self._sequence_code_for_steps(steps)

    @staticmethod
    def _sequence_code_for_steps(steps: list) -> str:
        """Return a one-line code preview for a group of steps.

        The previews of the individual steps (:meth:`_step_code_line`) are joined with
        ``"; "``. The result is stored as a protocol row's ``code``; the Build Protocol
        *Code* view itself shows the full script from ``sequence_code_text``.

        :param steps: The step objects of one protocol row.
        :returns: The joined preview, or ``""`` for no steps.
        """
        lines = [MainWindow._step_code_line(step) for step in steps]
        return "; ".join(line for line in lines if line)

    @staticmethod
    def _step_code_line(step) -> str:
        """Return a single line of Python-like code that describes one step.

        Examples: ``pp.transform('Intensity', 'normalize_max', output='Intensity_norm')``,
        ``pp.set_roles(x='Angle', y='Intensity')``,
        ``pp.plot_with_module('basic', 'scatter')`` and, for a load step,
        ``LoadDataStep(path=..., loader=..., dataset_name=..., loader_plugin=...).apply(pp)``.
        Calculations, renames, cell edits and row or column deletions map to the matching
        ``pp`` methods. Other step types give ``# <ClassName>``. This preview is separate
        from the runnable script that *Export Sequence.py* writes.

        :param step: A backend workflow step.
        :returns: The code line.
        """
        if isinstance(step, LoadDataStep):
            return (
                "LoadDataStep("
                f"path={step.path!r}, loader={step.loader!r}, dataset_name={step.dataset_name!r}, "
                f"loader_plugin={step.loader_plugin!r}).apply(pp)"
            )
        if isinstance(step, SetRoleStep):
            return f"pp.set_roles({MainWindow._kwargs_code(step.roles)})"
        if isinstance(step, TransformColumnStep):
            params = dict(step.params)
            params_code = MainWindow._kwargs_code(params)
            suffix = f", {params_code}" if params_code else ""
            return f"pp.transform({step.input_column!r}, {step.function_name!r}, output={step.output!r}{suffix})"
        if isinstance(step, CalculateColumnStep):
            return f"pp.calculate({step.formula_original!r}, output={step.output!r})"
        if isinstance(step, PlotModuleStep):
            config_code = MainWindow._kwargs_code(step.config)
            suffix = f", {config_code}" if config_code else ""
            return f"pp.plot_with_module({step.plotter_id!r}, {step.plot_type!r}{suffix})"
        if isinstance(step, RenameColumnStep):
            return f"pp.rename_column({step.old_column!r}, {step.new_column!r})"
        if isinstance(step, SetCellValueStep):
            return f"pp.set_cell_value({step.row_index!r}, {step.column!r}, {step.value!r})"
        if isinstance(step, DeleteRowsStep):
            return f"pp.delete_rows({step.row_indices!r})"
        if isinstance(step, DeleteColumnsStep):
            return f"pp.delete_columns({step.columns!r})"
        return f"# {step.__class__.__name__}"

    @staticmethod
    def _kwargs_code(values: dict) -> str:
        """Format a dict as keyword arguments, for example ``factor=2.0, value='a'``.

        :param values: Argument names and values; values are written with ``repr``.
        :returns: The comma-separated arguments, or ``""`` for an empty dict.
        """
        return ", ".join(f"{key}={value!r}" for key, value in values.items())

    @staticmethod
    def _column_number_from_name(name: str) -> int | None:
        """Return N for a default column name ``Column N``.

        Matching ignores case and surrounding spaces. Used by :meth:`rename_column` for
        columns the backend dataset does not contain.

        :param name: A column name.
        :returns: The number, or ``None`` when the name is not of the form ``Column N``.
        """
        text = str(name or "").strip().lower()
        if text.startswith("column "):
            try:
                return int(text.split(None, 1)[1])
            except (IndexError, ValueError):
                return None
        return None

    def _current_plot_mode(self) -> str:
        """Return a short label for the active mode, used in *Generate Plot* row details.

        Asks the active panel for ``current_plot_mode()`` (the Advanced panel returns
        ``"Sequence"``), then for a ``plot_preview`` widget's mode, and falls back to
        ``"Single"``, which is what Simple Mode gives.

        :returns: The label, for example ``"Single"`` or ``"Sequence"``.
        """
        panel = self.mode_manager.panels.get(self.state.mode)
        if hasattr(panel, "current_plot_mode"):
            return panel.current_plot_mode()
        preview = getattr(panel, "plot_preview", None)
        return preview.current_plot_mode() if preview else "Single"

    @staticmethod
    def _parse_params(text: str) -> dict:
        """Parse parameter text such as ``"factor=2, label=raw"`` into a dict.

        The text is split at commas; parts without ``=`` are ignored. Keys and values are
        stripped, and values that can be read as numbers become floats.

        :param text: The parameter text; empty text gives an empty dict.
        :returns: For the example, ``{"factor": 2.0, "label": "raw"}``.
        """
        params = {}
        if not text:
            return params
        for part in text.split(","):
            if "=" not in part:
                continue
            key, value = part.split("=", 1)
            key = key.strip()
            value = value.strip()
            try:
                params[key] = float(value)
            except ValueError:
                params[key] = value
        return params

    @staticmethod
    def _format_params(params: dict) -> str:
        """Format transformation parameters for display, for example ``factor=2, value=0.5``.

        Floats use the compact ``g`` format; other values are written as text.

        :param params: Parameter names and values.
        :returns: The formatted text, or ``"-"`` when there are no parameters.
        """
        if not params:
            return "-"
        return ", ".join(f"{key}={value:g}" if isinstance(value, float) else f"{key}={value}" for key, value in params.items())

    def _error(self, title: str, exc: Exception) -> None:
        """Report an error in the status bar and in a warning dialog (stderr when headless).

        Action methods catch their exceptions and call this, so a failed action leaves the
        window open and usable. The status bar shows ``title`` and ``self.last_error`` is set
        to ``(title, exc)``.
        When the Qt platform is ``offscreen`` (headless smoke tests and CI, where no one can
        dismiss a modal dialog), ``<title>: <exc>`` is printed to stderr instead of showing a
        dialog. Otherwise a modal warning box with ``title`` as its title and the exception
        text as its message is shown until the user closes it. Nothing is logged to a file.

        :param title: A short description of what failed, for example ``"Import failed"``.
        :param exc: The exception; its text is shown to the user.
        """
        self.status.set_message(title)
        self.last_error = (title, exc)
        if QtGui.QGuiApplication.platformName() == "offscreen":
            # Headless smoke tests and CI cannot dismiss a modal dialog.
            print(f"{title}: {exc}", file=sys.stderr)
            return
        QtWidgets.QMessageBox.warning(self, title, str(exc))
