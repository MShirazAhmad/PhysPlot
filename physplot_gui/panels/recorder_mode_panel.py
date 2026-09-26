"""Build the protocol sequence table and the Advanced Mode **Run Sequence** tab.

PhysPlot records every user action as a row of the protocol: file imports (a
``LoadDataStep`` plus the column roles as a ``SetRoleStep``), role changes,
column renames, cell edits, row and column deletions, transformations and
plots. Each row is backed by one or more ``physplot.steps`` objects in the
backend ``PhysPlot.workflow`` list, so the protocol replays in the GUI, exports
as a normal Python file, and runs headlessly or over folders. This module holds
the widgets that show that protocol:

- :class:`SequenceTablePanel` -- the protocol viewer and editor. Advanced Mode
  uses it twice: fully editable on the **Build Protocol** tab (title
  *Protocol Sequence from Simple Mode*), which is the source of truth for the
  sequence, and read-only on the **Run Sequence** tab (title
  *Current Protocol Sequence*).
- :class:`RecorderModePanel` -- the **Run Sequence** tab: the
  :class:`~physplot_gui.panels.bulk_panel.BulkPanel` on the left and the
  read-only sequence table on the right.

The panels hold no protocol logic. Every command calls a method of ``actions``,
the :class:`~physplot_gui.app.main_window.MainWindow`, which updates the backend
workflow and its timeline rows and then refreshes both tables. The user
documentation describes these screens with screenshots in the
*GUI Walkthrough* (``docs/getting_started.rst``, *Building and Replaying the
Protocol Sequence*, and ``wiki/GUI-Walkthrough.md``) and in the
*UI Reference* wiki (``wiki/UI-Reference.md``, pages
``wiki/UI-Build-Protocol.md`` and ``wiki/UI-Run-Sequence.md``).

.. rubric:: Layout of the sequence table

**Table** view, as configured on **Build Protocol** (in the GUI the buttons
form a single row, and **Apply Code to Table** is hidden in this view)::

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

**Code** view of the same sequence (abridged)::

    +- Protocol Sequence from Simple Mode -------------------- [Table] [Code]  Tracking: ON -+
    | from physplot import PhysPlot                                                          |
    | ...                                                                                    |
    | WORKFLOW_STEPS = [                                                                     |
    |     LoadDataStep(path='scan.xrdml', loader='auto', ...),                               |
    |     SetRoleStep(roles={'x': 'Angle', 'y': 'Intensity'}),                               |
    |     TransformColumnStep(input_column='Intensity', function_name='normalize_max', ...), |
    | ]                                                                                      |
    | def build_workflow(): ...                                                              |
    | def run(input_path=None, output_dir='outputs/sequence_run', loader='auto'): ...        |
    |                                                                                        |
    | [Import Sequence.py] [Export Sequence.py] [Apply This Sequence]                        |
    | [Apply Code to Table] [Copy as Script] [Clear Sequence]                                |
    +----------------------------------------------------------------------------------------+

**Run Sequence** tab: :class:`RecorderModePanel` with the read-only table,
which has no buttons, no **Delete** buttons, no right-click menu and a
read-only **Code** view::

    +- Bulk Run ---------------------------+ +- Current Protocol Sequence -----------------+
    | Plot modules and formatting are read | |              [Table] [Code]  Tracking: ON   |
    | from the sequence.                   | | # | Operation   | ... | Status  | Delete    |
    | Input Folder:  [__________] [Browse] | |---+-------------+-----+---------+-----------|
    | Sequence File: [__________] [Browse] | | 1 | File Loader | ... | OK      |           |
    | Output Folder: [__________] [Browse] | | 2 | Transform   | ... | OK      |           |
    | [        Run Bulk Workflow         ] | |                                             |
    +--------------------------------------+ +---------------------------------------------+

.. rubric:: Header controls

**Table** / **Code** (two checkable push buttons in an exclusive button group)
    Switch between the timeline table and the Python code of the whole
    sequence. On **Build Protocol**, returning to **Table** with unapplied code
    edits first applies them exactly like **Apply Code to Table**; if that
    fails, the error is shown and the **Code** view stays open.

**Tracking: ON** (bold green label)
    Sequence tracking is always on: every action is recorded. The badge never
    changes to off.

.. rubric:: Timeline table (Table view)

A six-column :class:`QTableWidget` with read-only cells and no row header. The
**#** and **Status** columns fit their contents; the others share the rest of
the width. Column indices 4 and 5 are ``STATUS_COLUMN`` and ``DELETE_COLUMN``.

**#**
    One-based row number.
**Operation**
    What was done, for example *File Loader*, *Set X*, *Set Roles*,
    *Rename Column*, *Edit Cell*, *Delete Rows*, *Delete Columns*,
    *Transform*, *Calculate* or *Generate Plot*.
**Details**
    For example the loader name with *(column names and role setup)*, the
    transformation name, ``old -> new`` for a rename, or
    ``Create <plotter> <plot type>`` for a plot.
**Target/File/Column**
    The file, the column, ``input -> output`` for a transformation, the new
    value of an edited cell, *Plotter Module* or *Table*.
**Status**
    Result of the row's backend steps in the last run, from
    ``MainWindow.timeline_row_status`` and styled by ``STATUS_STYLES``:

    - **OK** in green (``#12823b``); tooltip *Completed in N ms*;
    - **Failed** in bold red (``#d21f2b``); tooltip is the error message;
    - **Skipped** in grey (``#94a3b8``); tooltip *Not run because row N
      failed.*;
    - blank when the row has not run since it was recorded or edited.

    Statuses are filled by **Apply This Sequence**, **Rerun from this step**
    and the replay that follows a **Delete**. After a failure the later rows
    are skipped and the central table keeps the state reached before it.
**Delete** (Build Protocol only)
    A **Delete** push button in every row. It calls
    ``MainWindow.delete_timeline_step`` on the top-level window, which removes
    the row and its backend steps without confirmation, renumbers the
    remaining rows' step references, and replays the remaining sequence on the
    central table (status *Sequence updated*; a failing step is reported in
    **Status** and the status bar instead of a dialog). When no step remains,
    the status bar shows *Sequence cleared*. On **Run Sequence** the column is
    left blank.

**Right-click a row > Rerun from this step** (Build Protocol only)
    Calls ``MainWindow.rerun_from_timeline_step``, which restores the state
    saved before that row's first step during the last run and replays from
    there, without replaying the earlier rows (status *Reran from row N*).
    A row without a backend step reports *Row N has no replayable step*. When
    no saved state exists (for example when the sequence has not been run, or
    earlier steps changed since), the *Rerun failed* warning asks to run the
    whole sequence first. The menu item is disabled when ``actions`` has no
    ``rerun_from_timeline_step`` method.

.. rubric:: Code view

A :class:`QPlainTextEdit` (object name ``CodeView``: dark background,
monospaced font) showing ``MainWindow.sequence_code_text()``, which is
``PhysPlot.workflow_script()``: a complete Python module with a
``WORKFLOW_STEPS`` list, ``build_workflow()`` and ``run()``. It is the same text
that **Export Sequence.py** writes and **Copy as Script** copies. The view is
editable only on **Build Protocol**. A timeline refresh rewrites the text,
except while the Build Protocol **Code** view is shown with unapplied edits.

.. rubric:: Buttons (Build Protocol only)

**Import Sequence.py**
    ``MainWindow.open_workflow``: opens a *Load Sequence.py* dialog in the
    ``config/sequences`` folder, loads the file's steps, and replaces the
    sequence and its rows (a load step followed by a role step forms one
    *File Loader* row). The status bar shows *Sequence loaded*; errors show
    *Load sequence failed*. The steps are not run until
    **Apply This Sequence**.
**Export Sequence.py**
    ``MainWindow.save_workflow``: opens a *Save Sequence.py* dialog (default
    ``config/sequences/sequence.py``) and writes the sequence as runnable
    Python. The status bar shows *Sequence saved*.
**Apply This Sequence** (primary)
    ``MainWindow.apply_current_sequence`` (also *Protocol > Apply This
    Sequence*, ``Ctrl+R``): syncs the table, then replays the whole sequence
    on it and fills **Status**. Success shows *Sequence complete*; a failure
    shows the *Apply sequence failed* warning with
    *Row N failed (<step>): <error>*. An empty sequence shows *Build or import
    a protocol sequence first.*
**Apply Code to Table** (visible only in the **Code** view)
    Parses the edited code with ``MainWindow.apply_sequence_code``, replaces
    the sequence and rebuilds the rows (status *Sequence code applied*). The
    steps are not run. Invalid code shows the *Apply code to table failed*
    warning; a Python syntax error names the line and its text and selects
    that line in the editor. The table and sequence are then left unchanged.
**Copy as Script**
    ``MainWindow.copy_workflow_script``: copies the sequence code to the
    clipboard (status *Sequence script copied*).
**Clear Sequence**
    ``MainWindow.clear_recording``: removes every row and backend step without
    confirmation. The data in the central table is not changed.
"""

from physplot.qt_compat import QtCore, QtGui, QtWidgets

from .bulk_panel import BulkPanel

STATUS_COLUMN = 4
DELETE_COLUMN = 5
STATUS_STYLES = {
    "ok": ("OK", "#12823b"),
    "failed": ("Failed", "#d21f2b"),
    "skipped": ("Skipped", "#94a3b8"),
}


class SequenceTablePanel(QtWidgets.QFrame):
    """Show the protocol sequence as a timeline table or as Python code.

    A ``Panel``-styled frame used twice in Advanced Mode: on **Build Protocol**
    (``show_buttons=True``, ``editable_code=True``, ``show_delete=True``) as the
    editable source of truth, and on **Run Sequence** (all three ``False``) as a
    read-only mirror. The module docstring describes each control's end-to-end
    behaviour.

    .. rubric:: Layout

    - Header row: the title label, a stretch, the **Table** and **Code** toggle
      buttons, and the **Tracking: ON** badge.
    - A stacked widget: page 0 is the timeline table, page 1 the code editor.
    - Optional button row: **Import Sequence.py**, **Export Sequence.py**,
      **Apply This Sequence** (primary), **Apply Code to Table**,
      **Copy as Script** and **Clear Sequence**, then a stretch.

    .. rubric:: Public attributes

    ``actions``
        The object that performs every command, normally the
        :class:`~physplot_gui.app.main_window.MainWindow`.
    ``editable_code``, ``show_delete``
        The construction options (see the parameters).
    ``tracking_badge``
        :class:`QLabel` reading **Tracking: ON** in bold green (``#12823b``).
    ``table_button``, ``code_button``
        Checkable :class:`QPushButton` toggles **Table** (checked at start) and
        **Code**.
    ``view_buttons``
        The exclusive :class:`QButtonGroup` holding the toggles with ids 0
        (Table) and 1 (Code); a click switches the stacked page.
    ``stack``
        :class:`QStackedWidget` with the table (index 0) and the code editor
        (index 1).
    ``timeline``
        The six-column :class:`QTableWidget`: **#**, **Operation**,
        **Details**, **Target/File/Column**, **Status** (``STATUS_COLUMN``)
        and **Delete** (``DELETE_COLUMN``). Cells are read-only. With
        ``show_delete`` each row has a **Delete** button and right-clicking a
        row offers **Rerun from this step**; otherwise the column is blank and
        there is no context menu.
    ``code_view``
        :class:`QPlainTextEdit` (object name ``CodeView``) with the sequence's
        Python code; read-only unless ``editable_code``.
    ``apply_code_button``
        The **Apply Code to Table** button, or ``None`` without a button row.
        It is visible only when ``editable_code`` is true and the **Code** view
        is shown.

    .. rubric:: Public methods

    ``set_tracking(active=True)``
        Show **Tracking: ON** in green. The argument is ignored because
        tracking is always on.
    ``refresh_timeline(rows)``
        Rebuild the table from the main window's timeline rows (``dict`` with
        ``action``, ``details``, ``target`` and ``code`` keys, plus the step
        indices used for status): number, operation, details and target
        cells; a **Status** cell from ``actions.timeline_row_status(row)``
        coloured by ``STATUS_STYLES`` (**OK** green, **Failed** bold red,
        **Skipped** grey, with the message as tooltip); and a **Delete**
        button or a blank cell. The code view is then reloaded from
        ``actions.sequence_code_text()`` (or, without that method, one line per
        row from each row's ``code`` or a ``# Operation: details -> target``
        comment), unless the editable **Code** view is shown with unapplied
        edits.
    ``status_text(index)``
        Return the raw status key of a row (``"ok"``, ``"failed"``,
        ``"skipped"``) or ``""`` when it has none.

    .. rubric:: Interaction details

    - A **Delete** button calls ``delete_timeline_step(row)`` on the top-level
      window (``self.window()``), not on ``actions``.
    - **Rerun from this step** calls
      ``actions.rerun_from_timeline_step(row)``.
    - **Apply Code to Table**, and switching from **Code** back to **Table**
      with unapplied edits, call ``actions.apply_sequence_code(text)``. A
      failure opens an *Apply code to table failed* warning that explains the
      error in its message (macOS hides dialog titles); for a syntax error it
      gives the line number and text and selects that line in the editor.
      The sequence is left unchanged and the **Code** view stays open.
    - The other buttons call ``actions.open_workflow``,
      ``actions.save_workflow``, ``actions.apply_current_sequence``,
      ``actions.copy_workflow_script`` and ``actions.clear_recording``.

    The panel defines no Qt signals.

    :param actions: The main window (or a compatible object). Optional methods
        ``timeline_row_status``, ``sequence_code_text``,
        ``rerun_from_timeline_step`` and ``apply_sequence_code`` are used when
        present.
    :param title: Text of the title label, for example *Protocol Sequence from
        Simple Mode* or *Current Protocol Sequence*.
    :param show_buttons: Add the six-button row under the table.
    :param editable_code: Let the user edit the **Code** view and apply it.
    :param show_delete: Add a **Delete** button to every row and the
        right-click **Rerun from this step** menu.
    :param parent: Optional parent widget.
    """
    def __init__(
        self,
        actions,
        title: str = "Sequence",
        show_buttons: bool = True,
        editable_code: bool = False,
        show_delete: bool = True,
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("Panel")
        self.actions = actions
        self.editable_code = editable_code
        self.show_delete = show_delete
        self._code_dirty = False
        self._updating_code = False
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        header = QtWidgets.QHBoxLayout()
        title_label = QtWidgets.QLabel(title)
        title_label.setObjectName("PanelTitle")
        self.tracking_badge = QtWidgets.QLabel("Tracking: ON")
        self.tracking_badge.setStyleSheet("color:#12823b;font-weight:700;")
        header.addWidget(title_label)
        header.addStretch(1)
        self.table_button = QtWidgets.QPushButton("Table")
        self.table_button.setCheckable(True)
        self.table_button.setChecked(True)
        self.code_button = QtWidgets.QPushButton("Code")
        self.code_button.setCheckable(True)
        self.view_buttons = QtWidgets.QButtonGroup(self)
        self.view_buttons.setExclusive(True)
        self.view_buttons.addButton(self.table_button, 0)
        self.view_buttons.addButton(self.code_button, 1)
        self.view_buttons.idClicked.connect(self._set_view_mode)
        header.addWidget(self.table_button)
        header.addWidget(self.code_button)
        header.addWidget(self.tracking_badge)
        layout.addLayout(header)
        self.stack = QtWidgets.QStackedWidget()
        self.timeline = QtWidgets.QTableWidget(0, 6)
        self.timeline.setHorizontalHeaderLabels(["#", "Operation", "Details", "Target/File/Column", "Status", "Delete"])
        header_view = self.timeline.horizontalHeader()
        header_view.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        header_view.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(STATUS_COLUMN, QtWidgets.QHeaderView.ResizeToContents)
        self.timeline.verticalHeader().hide()
        if show_delete:
            self.timeline.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
            self.timeline.customContextMenuRequested.connect(self._show_row_menu)
        self.code_view = QtWidgets.QPlainTextEdit()
        self.code_view.setReadOnly(not editable_code)
        self.code_view.setObjectName("CodeView")
        self.code_view.textChanged.connect(self._code_changed)
        self.stack.addWidget(self.timeline)
        self.stack.addWidget(self.code_view)
        layout.addWidget(self.stack, 1)
        self.apply_code_button = None
        if show_buttons:
            buttons = QtWidgets.QHBoxLayout()
            for text, callback in (
                ("Import Sequence.py", actions.open_workflow),
                ("Export Sequence.py", actions.save_workflow),
                ("Apply This Sequence", actions.apply_current_sequence),
                ("Apply Code to Table", self._apply_code_changes),
                ("Copy as Script", actions.copy_workflow_script),
                ("Clear Sequence", actions.clear_recording),
            ):
                button = QtWidgets.QPushButton(text)
                if text == "Apply This Sequence":
                    button.setProperty("primary", True)
                if text == "Apply Code to Table":
                    self.apply_code_button = button
                button.clicked.connect(callback)
                buttons.addWidget(button)
            buttons.addStretch(1)
            layout.addLayout(buttons)
        self._update_code_button_visibility()

    def set_tracking(self, active: bool = True) -> None:
        self.tracking_badge.setText("Tracking: ON")
        self.tracking_badge.setStyleSheet("color:#12823b;font-weight:700;")

    def refresh_timeline(self, rows: list[dict]) -> None:
        self.timeline.setRowCount(len(rows))
        for index, row in enumerate(rows):
            values = [
                str(index + 1),
                row.get("action", ""),
                row.get("details", ""),
                row.get("target", ""),
            ]
            for column, value in enumerate(values):
                item = QtWidgets.QTableWidgetItem(value)
                item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
                self.timeline.setItem(index, column, item)
            self.timeline.setItem(index, STATUS_COLUMN, self._status_item(row))
            if self.show_delete:
                delete_button = QtWidgets.QPushButton("Delete")
                delete_button.clicked.connect(lambda checked=False, i=index: self._delete_row(i))
                self.timeline.setCellWidget(index, DELETE_COLUMN, delete_button)
            else:
                item = QtWidgets.QTableWidgetItem("")
                item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
                self.timeline.setItem(index, DELETE_COLUMN, item)
        if not (self.editable_code and self._code_dirty and self.stack.currentIndex() == 1):
            if hasattr(self.actions, "sequence_code_text"):
                source = self.actions.sequence_code_text()
            else:
                source = "\n".join(row.get("code") or self._fallback_code_line(row) for row in rows)
            self._set_code_text(source)

    def _set_view_mode(self, index: int) -> None:
        if index == 0 and self.editable_code and self._code_dirty:
            if not self._apply_code_changes():
                self.code_button.setChecked(True)
                return
        self.stack.setCurrentIndex(index)
        self._update_code_button_visibility()

    @staticmethod
    def _fallback_code_line(row: dict) -> str:
        return f"# {row.get('action', 'Step')}: {row.get('details', '')} -> {row.get('target', '')}"

    def _status_item(self, row: dict) -> QtWidgets.QTableWidgetItem:
        """Build the Status cell from the backend step results for ``row``."""
        status, message = (None, None)
        if hasattr(self.actions, "timeline_row_status"):
            status, message = self.actions.timeline_row_status(row)
        text, color = STATUS_STYLES.get(status, ("", None))
        item = QtWidgets.QTableWidgetItem(text)
        item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
        item.setData(QtCore.Qt.ItemDataRole.UserRole, status)
        if color:
            item.setForeground(QtGui.QBrush(QtGui.QColor(color)))
            font = item.font()
            font.setBold(status == "failed")
            item.setFont(font)
        if message:
            item.setToolTip(message)
        return item

    def status_text(self, index: int) -> str:
        item = self.timeline.item(index, STATUS_COLUMN)
        if item is None:
            return ""
        return item.data(QtCore.Qt.ItemDataRole.UserRole) or ""

    def _show_row_menu(self, position) -> None:
        index = self.timeline.rowAt(position.y())
        if index < 0:
            return
        menu = QtWidgets.QMenu(self.timeline)
        rerun = menu.addAction("Rerun from this step")
        rerun.setEnabled(hasattr(self.actions, "rerun_from_timeline_step"))
        rerun.triggered.connect(lambda checked=False, i=index: self.actions.rerun_from_timeline_step(i))
        menu.exec(self.timeline.viewport().mapToGlobal(position))

    def _delete_row(self, index: int) -> None:
        window = self.window()
        if hasattr(window, "delete_timeline_step"):
            window.delete_timeline_step(index)

    def _set_code_text(self, source: str) -> None:
        self._updating_code = True
        try:
            self.code_view.setPlainText(source)
            self._code_dirty = False
        finally:
            self._updating_code = False

    def _code_changed(self) -> None:
        if not self._updating_code and self.editable_code:
            self._code_dirty = True

    def _apply_code_changes(self) -> bool:
        if not self.editable_code:
            return True
        if not hasattr(self.actions, "apply_sequence_code"):
            return False
        try:
            self.actions.apply_sequence_code(self.code_view.toPlainText())
            self._code_dirty = False
            return True
        except Exception as exc:
            self._show_code_error(exc)
            return False

    def _show_code_error(self, exc: Exception) -> None:
        """Explain a failed code apply in the message itself; macOS hides dialog titles."""
        if isinstance(exc, SyntaxError) and exc.lineno:
            detail = f"Python syntax error on line {exc.lineno}: {exc.msg}."
            if exc.text and exc.text.strip():
                detail += f"\n\n    {exc.text.strip()}"
            self._select_code_line(exc.lineno)
        else:
            detail = f"{type(exc).__name__}: {exc}"
        QtWidgets.QMessageBox.warning(
            self,
            "Apply code to table failed",
            f"The sequence code could not be applied.\n\n{detail}\n\nThe table and sequence were not changed.",
        )

    def _select_code_line(self, line: int) -> None:
        block = self.code_view.document().findBlockByLineNumber(max(0, line - 1))
        if block.isValid():
            cursor = QtGui.QTextCursor(block)
            cursor.select(QtGui.QTextCursor.SelectionType.LineUnderCursor)
            self.code_view.setTextCursor(cursor)
            self.code_view.setFocus()

    def _update_code_button_visibility(self) -> None:
        if self.apply_code_button is not None:
            self.apply_code_button.setVisible(self.editable_code and self.stack.currentIndex() == 1)


class RecorderModePanel(QtWidgets.QWidget):
    """Show the **Run Sequence** tab: bulk-run controls beside the current sequence.

    Advanced Mode adds this panel as its second tab. The user fills in the
    :class:`~physplot_gui.panels.bulk_panel.BulkPanel` on the left and clicks
    **Run Bulk Workflow** to apply a sequence to every file in a folder; the
    read-only table on the right shows the protocol that runs when
    **Sequence File** is left blank. The sequence is edited on
    **Build Protocol**, never here.

    .. rubric:: Layout

    A horizontal layout (margins 8, 6, 8, 8; spacing 8) with the bulk panel at
    stretch 3 on the left and the sequence table at stretch 6 on the right.

    .. rubric:: Public widget attributes

    ``bulk``
        The :class:`~physplot_gui.panels.bulk_panel.BulkPanel` (**Input
        Folder**, **Sequence File**, **Output Folder**, **Run Bulk Workflow**).
    ``sequence``
        A :class:`SequenceTablePanel` titled *Current Protocol Sequence*, with
        no button row, a read-only **Code** view, and no **Delete** buttons or
        right-click menu.

    The panel defines no Qt signals.

    :param actions: The main window (or a compatible object) passed to both
        child panels.
    :param parent: Optional parent widget.
    """
    def __init__(self, actions, parent=None):
        """Create the bulk-run panel and the read-only sequence table.

        :param actions: The main window (or a compatible object) that runs bulk
            workflows and provides the sequence rows' status and code.
        :param parent: Optional parent widget.
        """
        super().__init__(parent)
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 8)
        layout.setSpacing(8)
        left = QtWidgets.QVBoxLayout()
        self.bulk = BulkPanel(actions)
        left.addWidget(self.bulk, 1)
        layout.addLayout(left, 3)
        self.sequence = SequenceTablePanel(
            actions,
            title="Current Protocol Sequence",
            show_buttons=False,
            editable_code=False,
            show_delete=False,
        )
        layout.addWidget(self.sequence, 6)

    def set_recording(self, active: bool) -> None:
        """Keep the table's badge at **Tracking: ON**.

        Tracking is always on, so ``active`` does not change what is shown.

        :param active: The backend's ``recording`` flag (ignored).
        """
        self.sequence.set_tracking(True)

    def refresh_timeline(self, rows: list[dict]) -> None:
        """Mirror the current protocol rows in the read-only table.

        Called through :meth:`AdvancedModePanel.refresh_timeline
        <physplot_gui.panels.advanced_mode_panel.AdvancedModePanel.refresh_timeline>`
        whenever the main window refreshes, so this tab always shows the same
        rows, statuses and code as **Build Protocol**.

        :param rows: The main window's timeline rows.
        """
        self.sequence.refresh_timeline(rows)

    def refresh_plot(self) -> None:
        """Do nothing; the Run Sequence tab has no plot preview.

        Kept so the panel offers the same refresh methods as the other mode
        panels.

        :returns: ``None``.
        """
        return None
