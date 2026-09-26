"""Build the Advanced Mode controls: the **Build Protocol** and **Run Sequence** tabs.

Advanced Mode replaces the three Simple Mode panels under the central table
when the header's mode switcher (or *View > Advanced Mode*, ``Ctrl+2``) selects
**Advanced**. The :class:`~physplot_gui.app.mode_manager.ModeManager` gives it a
taller lower area (300 to 430 px) than Simple Mode so the sequence table has
room. The central table stays visible above it, so the effect of replaying a
protocol is seen immediately.

Everything the user does in the GUI is recorded by the main window as a row of
the protocol: file imports (with column names and roles), role changes, column
renames, cell edits, row and column deletions, transformations and plots. Each
row is backed by one or more ``physplot.steps`` objects in the backend
``PhysPlot.workflow`` list, so the protocol can be replayed, exported as a
normal Python file, and run headlessly over folders. The **Build Protocol** tab
is the editable source of truth for that sequence; the **Run Sequence** tab
applies it to whole folders.

The user documentation describes the same screens with screenshots: see
*GUI Walkthrough* (``docs/getting_started.rst``, section *Building and
Replaying the Protocol Sequence*, and ``wiki/GUI-Walkthrough.md``) and the
*UI Reference* wiki (``wiki/UI-Reference.md``, pages
``wiki/UI-Build-Protocol.md`` and ``wiki/UI-Run-Sequence.md``).

.. rubric:: Layout

A document-mode :class:`QTabWidget` with two tabs::

    [Build Protocol]   Run Sequence
    +- Protocol Sequence from Simple Mode ---------------- [Table] [Code]  Tracking: ON -+
    | # | Operation     | Details              | Target/File/Column | Status  | Delete   |
    |---+---------------+----------------------+--------------------+---------+----------|
    | 1 | File Loader   | Auto Loader (colu... | scan.xrdml         | OK      | [Delete] |
    | 2 | Transform     | normalize_max        | Y -> Y_norm        | Failed  | [Delete] |
    | 3 | Generate Plot | Create basic scatter | Plotter Module     | Skipped | [Delete] |
    |                                                                                    |
    | [Import Sequence.py] [Export Sequence.py] [Apply This Sequence]                    |
    | [Apply Code to Table] [Copy as Script] [Clear Sequence]                            |
    +------------------------------------------------------------------------------------+

     Build Protocol   [Run Sequence]
    +- Bulk Run ---------------------------+ +- Current Protocol Sequence -----------------+
    | Plot modules and formatting are read | |              [Table] [Code]  Tracking: ON   |
    | from the sequence.                   | | # | Operation   | ... | Status  | Delete    |
    | Input Folder:  [__________] [Browse] | |---+-------------+-----+---------+-----------|
    | Sequence File: [__________] [Browse] | | 1 | File Loader | ... | OK      |           |
    | Output Folder: [__________] [Browse] | | 2 | Transform   | ... | OK      |           |
    | [        Run Bulk Workflow         ] | |                                             |
    +--------------------------------------+ +---------------------------------------------+

In the GUI the six Build Protocol buttons sit in one row, and
**Apply Code to Table** is only visible while the **Code** view is shown.

.. rubric:: Build Protocol tab

An editable
:class:`~physplot_gui.panels.recorder_mode_panel.SequenceTablePanel` titled
*Protocol Sequence from Simple Mode*, with every control enabled:

- **Table** / **Code** toggle: the rows as a table, or the whole sequence as
  editable Python (the same text that **Export Sequence.py** writes).
- The six-column table (**#**, **Operation**, **Details**,
  **Target/File/Column**, **Status**, **Delete**). **Status** shows **OK**,
  **Failed** or **Skipped** after the sequence runs, with details in the
  tooltip. A row's **Delete** button removes that step and replays the
  remaining sequence on the table. Right-click a row and choose
  **Rerun from this step** to resume the sequence there without replaying the
  earlier rows.
- **Import Sequence.py** / **Export Sequence.py** load or save the sequence as
  a Python file (``MainWindow.open_workflow`` / ``MainWindow.save_workflow``).
- **Apply This Sequence** (primary) replays the whole sequence on the table
  (``MainWindow.apply_current_sequence``, also *Protocol > Apply This
  Sequence*, ``Ctrl+R``).
- **Apply Code to Table** rebuilds the rows from the edited code
  (``MainWindow.apply_sequence_code``) without running them; invalid code is
  reported (a syntax error with its line number) and nothing changes.
- **Copy as Script** copies the sequence's Python code to the clipboard
  (``MainWindow.copy_workflow_script``).
- **Clear Sequence** removes every row and step (``MainWindow.clear_recording``).

The *Protocol* menu offers the same import, export, apply, copy and clear
commands, plus *Insert Protocol Module* to append a reusable module from
``config/protocol_modules``. The
:mod:`~physplot_gui.panels.recorder_mode_panel` docstring describes every
control of the sequence table in full.

.. rubric:: Run Sequence tab

A :class:`~physplot_gui.panels.recorder_mode_panel.RecorderModePanel`: the
:class:`~physplot_gui.panels.bulk_panel.BulkPanel` (**Input Folder**,
**Sequence File**, **Output Folder**, **Run Bulk Workflow**) on the left and a
read-only copy of the sequence table titled *Current Protocol Sequence* on the
right, showing the protocol that a bulk run uses when **Sequence File** is left
blank. Plot types and settings come from the sequence's plot steps, not from
Simple Mode's controls.
"""

from physplot.qt_compat import QtWidgets

from .recorder_mode_panel import RecorderModePanel, SequenceTablePanel


class AdvancedModePanel(QtWidgets.QWidget):
    """Show the Advanced Mode tabs: **Build Protocol** and **Run Sequence**.

    The :class:`~physplot_gui.app.mode_manager.ModeManager` creates one instance
    and shows it in the lower control area when **Advanced** is selected. The
    panel forwards timeline updates from the main window to both sequence
    tables and contains no protocol logic of its own; every button calls a
    method of ``actions`` (the :class:`~physplot_gui.app.main_window.MainWindow`).

    .. rubric:: Layout

    A vertical layout (margins 8, 6, 8, 8) holding a document-mode
    :class:`QTabWidget`:

    - tab 0, **Build Protocol** -- :attr:`sequence_builder`;
    - tab 1, **Run Sequence** -- :attr:`recorder`.

    .. rubric:: Public widget attributes

    ``tabs``
        The :class:`QTabWidget` holding both tabs.
    ``sequence_builder``
        The editable
        :class:`~physplot_gui.panels.recorder_mode_panel.SequenceTablePanel`
        titled *Protocol Sequence from Simple Mode*, with the button row, an
        editable **Code** view, and the **Delete** column and right-click
        **Rerun from this step** menu.
    ``recorder``
        The :class:`~physplot_gui.panels.recorder_mode_panel.RecorderModePanel`
        shown on the **Run Sequence** tab (bulk-run controls plus a read-only
        sequence table). Its ``bulk`` attribute is the
        :class:`~physplot_gui.panels.bulk_panel.BulkPanel`.

    The panel defines no Qt signals.

    :param actions: The main window (or a compatible object) that performs
        every action; it is passed on to both tabs.
    :param parent: Optional parent widget.
    """
    def __init__(self, actions, parent=None):
        """Create the tab widget with the **Build Protocol** and **Run Sequence** tabs.

        :param actions: The main window (or a compatible object) passed to the
            sequence tables and the bulk-run panel.
        :param parent: Optional parent widget.
        """
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 8)
        layout.setSpacing(6)
        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.addTab(self._protocol_tab(actions), "Build Protocol")
        self.recorder = RecorderModePanel(actions)
        self.tabs.addTab(self.recorder, "Run Sequence")
        layout.addWidget(self.tabs)

    def _protocol_tab(self, actions):
        """Build the **Build Protocol** tab around an editable sequence table.

        Creates :attr:`sequence_builder` with the title *Protocol Sequence from
        Simple Mode*, the button row (**Import Sequence.py**, **Export
        Sequence.py**, **Apply This Sequence**, **Apply Code to Table**,
        **Copy as Script**, **Clear Sequence**), an editable **Code** view, and
        per-row **Delete** buttons with the **Rerun from this step** context
        menu. The table fills the tab with no margins.

        :param actions: The main window (or a compatible object) that performs
            the sequence commands.
        :returns: The tab's container widget.
        """
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.sequence_builder = SequenceTablePanel(
            actions,
            title="Protocol Sequence from Simple Mode",
            show_buttons=True,
            editable_code=True,
            show_delete=True,
        )
        layout.addWidget(self.sequence_builder, 1)
        return widget

    def refresh_columns(self, columns: list[str]) -> None:
        """Ignore column updates; Advanced Mode has no column menus.

        Kept so the :class:`~physplot_gui.app.mode_manager.ModeManager` can call
        ``refresh_columns`` on every panel.

        :param columns: The central table's column names (unused).
        :returns: ``None``.
        """
        return None

    def refresh_pipeline(self, rows: list[dict]) -> None:
        """Ignore transformation-pipeline updates; the protocol table shows them.

        :param rows: The main window's recorded transformations (unused).
        :returns: ``None``.
        """
        return None

    def refresh_timeline(self, rows: list[dict]) -> None:
        """Show the current protocol rows on both tabs.

        Called by the :class:`~physplot_gui.app.mode_manager.ModeManager` each
        time the main window refreshes (``MainWindow._refresh_all``), so a step
        recorded in Simple Mode appears in **Build Protocol** and
        **Run Sequence** right away. Both tables rebuild their rows, **Status**
        cells and **Code** view (see
        :class:`~physplot_gui.panels.recorder_mode_panel.SequenceTablePanel`).

        :param rows: The main window's timeline rows, one ``dict`` per protocol
            row with ``action``, ``details``, ``target``, ``workflow_index``,
            ``workflow_indices`` and ``code`` keys.
        """
        self.sequence_builder.refresh_timeline(rows)
        self.recorder.refresh_timeline(rows)

    def set_recording(self, active: bool) -> None:
        """Keep both tracking badges at **Tracking: ON**.

        Sequence tracking is always on in PhysPlot: every action is recorded.
        The Build Protocol badge is set to on regardless of ``active``, and
        ``active`` is passed to :attr:`recorder`, which also shows on.

        :param active: The backend's ``recording`` flag.
        """
        self.sequence_builder.set_tracking(True)
        self.recorder.set_recording(active)

    def refresh_plot(self) -> None:
        """Do nothing; Advanced Mode has no plot preview to redraw.

        Kept so ``ModeManager.refresh_plots`` can call it.

        :returns: ``None``.
        """
        return None

    def current_plot_mode(self) -> str:
        """Return the plot-mode label used while Advanced Mode is active.

        ``MainWindow._current_plot_mode`` uses it to describe plots made from
        *Plot > Generate Plot* in the protocol row, for example
        *Create Sequence plot*.

        :returns: ``"Sequence"``.
        """
        return "Sequence"
