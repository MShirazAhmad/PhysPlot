"""Spreadsheet-style central table with role dropdowns.

:class:`CentralTable` is the heart of the table-first PhysPlot window. The main window places
it between the branded header (logos and the Simple/Advanced switcher) and the mode panels,
with a stretch factor so it takes all spare vertical space. Everything the user types,
pastes, clears, renames or deletes here is mirrored into the backend
:class:`physplot.PhysPlot` dataset by the main window, and most of it is recorded as a
replayable protocol step.

.. rubric:: Layout

The widget has no margins and wraps a single ``QTableWidget``, exposed as
``CentralTable.table``.

* **Row 0 is the role row.** Every column holds a ``QComboBox`` with the object name
  ``RoleCombo`` (styled more compactly by the application stylesheet). Its items are
  :data:`physplot_gui.widgets.column_role_header.ROLE_OPTIONS`: ``Ignore``, ``X``, ``Y``,
  ``X Error``, ``Y Error``, ``Group``, ``Label``, ``Batch Key`` and ``Fit Weight``. A column
  with no assigned role, and every added placeholder column, shows ``Ignore``. Row 0 is
  34 px tall and its row-header label is blank.
* **Data rows start at table row 1.** The vertical header numbers them ``1``, ``2``,
  ``3`` ..., so the number shown next to a row is the same 1-based row number used by the
  signals below and by the recorded protocol steps. The vertical header is a fixed 60 px
  wide; data rows default to 27 px (minimum 24 px).
* **Column header labels.** A column whose name equals its placeholder ``Column N`` (``N``
  being its 1-based position) is labelled just ``Column N``. Any other name is labelled
  with its position as ``N: name`` (for example ``2: Voltage``), so the column number that
  the protocol can fall back on is always visible.
* **Minimum grid.** The grid always has at least :attr:`CentralTable.MIN_DATA_ROWS` (100)
  data rows and :attr:`CentralTable.MIN_DATA_COLUMNS` (26) columns, however small the
  loaded data is. Columns beyond the data get placeholder names ``Column N``. A freshly
  created widget shows a blank sheet (17 rows by 19 columns of empty text, padded to the
  minimum grid).
* **Automatic growth.** The sheet grows as it is used:

  - scrolling to within 5 steps of the end of the vertical scroll bar appends 100 rows;
  - scrolling to within 3 steps of the end of the horizontal scroll bar appends
    10 columns;
  - committing an edit in one of the last two rows appends 50 rows, and committing an
    edit in one of the last two columns appends 10 columns;
  - pasting a block that does not fit appends rows (100 at a time) and columns (10 at a
    time) until it does.

  Appended columns get placeholder names, the role ``Ignore`` and their own role dropdown.
* **Column widths.** Columns default to 82 px (minimum 64 px). Whenever the headers are
  refreshed or a column is renamed, any column whose header label would be clipped is
  widened to fit it. Widths are never reduced, so a width the user dragged is kept, even
  when new data is loaded.
* **Cells** hold centre-aligned plain text. Alternating row colours are enabled and both
  scroll bars appear only when needed.

.. rubric:: Mouse and keyboard

Selection is a single contiguous rectangular block of cells (click, drag or Shift+click).

Editing cells
    Double-click a cell, press the platform edit key (for example F2), or simply start
    typing to edit the current cell; typing replaces its content. Committing the edit
    emits :attr:`CentralTable.cell_value_changed` followed by
    :attr:`CentralTable.table_edited`.

Renaming a column
    Double-click a column header, or choose **Rename Column** from its context menu. A
    "Rename Column" dialog asks for the new name, pre-filled with the current one.
    Cancelling changes nothing. An empty name, or a name already used by another column,
    is rejected with a warning message box and the column keeps its old name. Surrounding
    whitespace is stripped, and the column keeps its role under the new name.

Column header context menu (right-click a column header)
    The whole column is selected first. The menu offers **Rename Column**, a separator,
    then **Copy Column**, **Paste Column** and **Delete Column**. *Copy Column* copies all
    of the column's data rows (including trailing empty ones); *Paste Column* pastes the
    clipboard starting at the current cell, which Qt moves into the selected column;
    *Delete Column* removes that column together with its name and role.

Row header context menu (right-click a row number)
    The whole row is selected first. The menu offers **Copy Row**, **Paste Row** and
    **Delete Row**, which act on that row in the same way as the column actions. The blank
    header of the role row (row 0) opens no menu.

Cell context menu (right-click inside the grid)
    **Copy** copies the selected block, **Paste** pastes the clipboard at the current
    cell, and **Clear** empties every selected data cell. The role dropdowns are never
    cleared.

Keyboard shortcuts
    The platform Copy and Paste shortcuts (``Cmd+C``/``Cmd+V`` on macOS,
    ``Ctrl+C``/``Ctrl+V`` elsewhere) copy the selected block and paste at the current
    cell.

Clipboard format
    Copy writes tab-separated text, one line per row, which pastes directly into other
    spreadsheet programs. Only the first selected block is copied and the role row is
    never included. Paste splits the clipboard text into lines and each line on tabs, then
    writes the block with its top-left corner at the current cell; it never writes above
    data row 1.

.. rubric:: Signals

``role_changed(column_name: str, role: str)``
    The user picked a role in a row-0 dropdown. ``MainWindow.set_column_role`` sets the
    role on the backend dataset (the backend clears the single-use roles ``X``, ``Y``,
    ``X Error``, ``Y Error`` and ``Fit Weight`` from any other column), records a
    ``SetRoleStep`` protocol step unless the new role is ``Ignore``, and pushes the
    resulting roles back into the dropdowns with :meth:`CentralTable.set_roles`.
``column_renamed(old_name: str, new_name: str)``
    A column was renamed. ``MainWindow.rename_column`` renames the backend column and
    records a ``RenameColumnStep``.
``cell_value_changed(row: int, column_name: str, value: str, column_number: int)``
    One cell received a new value by typing, pasting or clearing. ``row`` is the 1-based
    data row (the number shown in the row header), ``column_name`` the column's current
    name, ``value`` the new cell text and ``column_number`` the 1-based column position.
    ``MainWindow.record_cell_edit`` records one ``SetCellValueStep`` per signal.
``rows_deleted(rows: list[int])``
    Rows were deleted. ``rows`` holds their sorted, 1-based data row numbers as they were
    before the deletion. ``MainWindow.record_row_delete`` records a ``DeleteRowsStep``.
``columns_deleted(names: list[str], numbers: list[int])``
    Columns were deleted. ``names`` and their 1-based ``numbers`` are listed in ascending
    position order. ``MainWindow.record_column_delete`` records a ``DeleteColumnsStep``.
``table_edited()``
    Emitted after every change the user makes to the contents: each committed cell edit,
    a paste, a clear, a rename, and a row or column deletion. ``MainWindow`` connects it
    to ``sync_table_to_backend``, which reloads the backend dataset from
    :meth:`CentralTable.to_dataframe` (keeping roles and metadata, see
    :meth:`physplot_gui.app.gui_state.GuiState.refresh_dataset_values`) and updates the
    status bar counts.
``structure_changed()``
    The set of columns changed: columns were appended, renamed or deleted. The main
    window does not currently connect to it.

Because the main window records a protocol step for each of the first five signals, the
Build Protocol sequence can replay the manual edits made in this table. The one exception
is setting a column back to ``Ignore``, which is not recorded.

No cell, role or edit signal is emitted while the table is filled programmatically by
:meth:`CentralTable.set_dataframe`, :meth:`CentralTable.set_blank`,
:meth:`CentralTable.resize_table` or :meth:`CentralTable.set_roles`.

.. rubric:: Reading the table back

:meth:`CentralTable.to_dataframe` reads every data row (row 0 is skipped) into a
:class:`pandas.DataFrame` whose columns are the current column names.

* With ``trim_empty=True`` (the default) the frame is cut to the used extent: up to the
  last row and the last column that contain a non-blank cell (whitespace-only cells count
  as blank), widened to include every column whose role is not ``Ignore``. A sheet with
  no data at all yields :attr:`CentralTable.DEFAULT_EXPORT_ROWS` by
  :attr:`CentralTable.DEFAULT_EXPORT_COLUMNS` (17 by 19) empty cells. With
  ``trim_empty=False`` the whole grid is returned.
* Each column is then converted to numbers when at least one of its values parses as a
  number and every non-empty value does. Empty cells in a converted column become
  ``NaN``. Any other column keeps its text; a cell holding only spaces counts as
  non-numeric text here.
"""

from __future__ import annotations

import pandas as pd
from physplot.qt_compat import QtCore, QtGui, QtWidgets

from .column_role_header import ROLE_OPTIONS


class CentralTable(QtWidgets.QWidget):
    """Show the editable data sheet with a column-role dropdown above every column.

    See the module documentation above for the full user guide (layout, mouse and keyboard
    interactions, signals and export rules). In short: table row 0 holds one role
    ``QComboBox`` per column, data rows start at table row 1, and every user edit is
    reported through Qt signals so that ``MainWindow`` can update the backend dataset and
    record protocol steps. The widget never talks to the backend itself.

    Signals (see the module documentation for who listens):

    * ``role_changed(str column_name, str role)``
    * ``column_renamed(str old_name, str new_name)``
    * ``cell_value_changed(int row, str column_name, str value, int column_number)``
    * ``rows_deleted(list rows)``
    * ``columns_deleted(list names, list numbers)``
    * ``table_edited()``
    * ``structure_changed()``

    Class constants:

    * ``MIN_DATA_ROWS = 100``: fewest data rows the grid ever shows (row 0 comes on top).
    * ``MIN_DATA_COLUMNS = 26``: fewest columns the grid ever shows.
    * ``DEFAULT_EXPORT_ROWS = 17`` and ``DEFAULT_EXPORT_COLUMNS = 19``: the size of the
      frame :meth:`to_dataframe` returns when trimming finds no data at all. They match
      the 17 by 19 blank sheet shown on start-up.

    :ivar table: The wrapped ``QTableWidget``. Row 0 holds the role dropdowns as cell
        widgets; rows 1 and up hold the data as ``QTableWidgetItem`` objects.
    """
    role_changed = QtCore.pyqtSignal(str, str)
    column_renamed = QtCore.pyqtSignal(str, str)
    cell_value_changed = QtCore.pyqtSignal(int, str, str, int)
    rows_deleted = QtCore.pyqtSignal(list)
    columns_deleted = QtCore.pyqtSignal(list, list)
    table_edited = QtCore.pyqtSignal()
    structure_changed = QtCore.pyqtSignal()

    MIN_DATA_ROWS = 100
    MIN_DATA_COLUMNS = 26
    DEFAULT_EXPORT_ROWS = 17
    DEFAULT_EXPORT_COLUMNS = 19

    def __init__(self, parent=None):
        """Build the table, connect its menus and signals, and show a blank sheet.

        The grid is configured with contiguous cell selection, editing on double-click, on
        the edit key and on any typed key, custom context menus on the cells and on both
        headers, double-click-to-rename on column headers, and scroll-bar watchers that
        grow the grid. It then shows a blank 17 by 19 sheet (padded to the minimum grid)
        with every role set to ``Ignore``.

        :param parent: Optional Qt parent widget.
        """
        super().__init__(parent)
        self._loading = False
        self._column_names: list[str] = []
        self._roles: dict[str, str] = {}
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.table = QtWidgets.QTableWidget(self.MIN_DATA_ROWS + 1, self.MIN_DATA_COLUMNS)
        self.table.setAlternatingRowColors(True)
        self.table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.table.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.table.horizontalHeader().setDefaultSectionSize(82)
        self.table.horizontalHeader().setMinimumSectionSize(64)
        self.table.verticalHeader().setDefaultSectionSize(27)
        self.table.verticalHeader().setMinimumSectionSize(24)
        self.table.verticalHeader().setFixedWidth(60)
        self.table.setRowHeight(0, 34)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.ContiguousSelection)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.table.setEditTriggers(
            QtWidgets.QAbstractItemView.DoubleClicked
            | QtWidgets.QAbstractItemView.EditKeyPressed
            | QtWidgets.QAbstractItemView.AnyKeyPressed
        )
        self.table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.table.horizontalHeader().setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.table.verticalHeader().setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_cell_menu)
        self.table.horizontalHeader().customContextMenuRequested.connect(self._show_column_menu)
        self.table.horizontalHeader().sectionDoubleClicked.connect(self.rename_column)
        self.table.verticalHeader().customContextMenuRequested.connect(self._show_row_menu)
        self.table.cellChanged.connect(self._on_cell_changed)
        self.table.verticalScrollBar().valueChanged.connect(self._maybe_extend_rows)
        self.table.horizontalScrollBar().valueChanged.connect(self._maybe_extend_columns)
        layout.addWidget(self.table)
        self.set_blank(17, 19)

    def set_blank(self, rows: int, columns: int) -> None:
        """Replace the sheet with an empty table of placeholder columns.

        Builds a ``rows`` by ``columns`` frame of empty strings named ``Column 1`` ...
        ``Column <columns>`` and shows it through :meth:`set_dataframe` with no roles, so
        every dropdown reads ``Ignore``. The visible grid is still padded to
        :attr:`MIN_DATA_ROWS` by :attr:`MIN_DATA_COLUMNS`. No signals are emitted.

        :param rows: Number of empty data rows to create.
        :param columns: Number of placeholder columns to create.
        """
        data = pd.DataFrame("", index=range(rows), columns=[f"Column {i}" for i in range(1, columns + 1)])
        self.set_dataframe(data, {})

    def set_dataframe(self, df: pd.DataFrame, roles: dict[str, str] | None = None) -> None:
        """Replace the whole sheet with ``df`` and show ``roles`` in the dropdowns.

        This is how the main window displays a freshly loaded or transformed dataset. The
        frame is copied and its column names converted to strings. The grid is resized to
        ``max(len(df), MIN_DATA_ROWS)`` data rows plus the role row, and to
        ``max(len(df.columns), MIN_DATA_COLUMNS)`` columns; columns beyond the data get
        placeholder names ``Column N`` that continue the numbering. All previous items are
        cleared, the headers are relabelled (widening clipped columns, never shrinking
        any), and a fresh role dropdown is installed in every column showing its role from
        ``roles`` or ``Ignore``. Each value is shown as text, missing values (``NaN``,
        ``None``) as empty cells, all centre-aligned. The current cell is then set to data
        row 1, column 1.

        The widget keeps its own copy of ``roles``, used to keep role columns when
        trimming in :meth:`to_dataframe`. No signals are emitted while the sheet is filled.

        :param df: Data to show; row ``i`` of the frame becomes data row ``i + 1``.
        :param roles: Optional mapping of column name to role name taken from
            :data:`~physplot_gui.widgets.column_role_header.ROLE_OPTIONS`. Columns missing
            from the mapping show ``Ignore``.
        """
        roles = roles or {}
        self._loading = True
        try:
            df = df.copy()
            df.columns = [str(column) for column in df.columns]
            self._roles = dict(roles)
            data_rows = max(len(df.index), self.MIN_DATA_ROWS)
            data_columns = max(len(df.columns), self.MIN_DATA_COLUMNS)
            self._column_names = list(df.columns) + [
                f"Column {index}" for index in range(len(df.columns) + 1, data_columns + 1)
            ]
            self.table.clear()
            self.table.setRowCount(data_rows + 1)
            self.table.setColumnCount(data_columns)
            self._refresh_headers()
            self.table.setRowHeight(0, 34)
            for column_index, column_name in enumerate(self._column_names):
                self._install_role_combo(column_index, roles.get(column_name, "Ignore"))
            for row_index in range(data_rows):
                for column_index, column_name in enumerate(self._column_names):
                    value = "" if row_index >= len(df.index) or column_index >= len(df.columns) else df.iloc[row_index, column_index]
                    item = QtWidgets.QTableWidgetItem("" if pd.isna(value) else str(value))
                    item.setTextAlignment(QtCore.Qt.AlignCenter)
                    self.table.setItem(row_index + 1, column_index, item)
            self.table.setCurrentCell(1, 0)
        finally:
            self._loading = False

    def set_roles(self, roles: dict[str, str]) -> None:
        """Show ``roles`` in the row-0 dropdowns without emitting :attr:`role_changed`.

        Every column's dropdown is set to its role from ``roles``, or to ``Ignore`` when
        the column is not in the mapping. The main window calls this after the backend has
        changed roles (for example after clearing a single-use role such as ``X`` from the
        column that held it before) so the dropdowns match the dataset.

        Only the dropdowns are updated. The widget's internal role map, which
        :meth:`to_dataframe` uses to decide which columns to keep when trimming, is not
        changed by this method.

        :param roles: Mapping of column name to role name.
        """
        self._loading = True
        try:
            for column_index, column_name in enumerate(self._column_names):
                combo = self.table.cellWidget(0, column_index)
                if isinstance(combo, QtWidgets.QComboBox):
                    combo.setCurrentText(roles.get(column_name, "Ignore"))
        finally:
            self._loading = False

    def to_dataframe(self, trim_empty: bool = True) -> pd.DataFrame:
        """Return the sheet's data rows as a :class:`pandas.DataFrame`.

        Every data row (table rows 1 and up, never the role row) is read as text into a
        frame whose columns are the current column names, in display order. Missing items
        read as empty strings.

        When ``trim_empty`` is true the frame is cut to the used extent: up to the last row
        and last column holding a non-blank cell (cells with only whitespace count as
        blank), widened to include every column whose role is not ``Ignore`` in the
        widget's role map. If no cell holds data, :attr:`DEFAULT_EXPORT_ROWS` rows and
        :attr:`DEFAULT_EXPORT_COLUMNS` columns are kept (17 by 19). The result always has
        at least one row and one column.

        Each column is then converted to numbers when at least one value parses as a
        number and every value that is not exactly ``""`` parses too; the empty cells of a
        converted column become ``NaN``. All other columns keep their text.

        The main window calls this with the default to sync the backend after every edit,
        and with ``trim_empty=False`` to check that a transformation's input column holds
        any values before applying it.

        :param trim_empty: Trim trailing empty rows and columns (default ``True``); when
            ``False`` the full grid, including all padding rows and columns, is returned.
        :returns: A new DataFrame; the table is not modified.
        """
        data = []
        for row in range(1, self.table.rowCount()):
            values = []
            for column in range(self.table.columnCount()):
                item = self.table.item(row, column)
                values.append(item.text() if item else "")
            data.append(values)
        df = pd.DataFrame(data, columns=self._column_names)
        if trim_empty:
            df = self._trim_empty_extent(df)
        for column in df.columns:
            numeric = pd.to_numeric(df[column], errors="coerce")
            nonempty = df[column].replace("", pd.NA).notna()
            if numeric.notna().any() and numeric[nonempty].notna().all():
                df[column] = numeric
        return df

    def column_names(self) -> list[str]:
        """Return the names of all grid columns in display order.

        The list covers every column of the grid, including the padding columns with
        placeholder names such as ``Column 20``, not only the columns that hold data. The
        main window passes it to the mode panels to fill their column pickers.

        :returns: A copy of the column-name list; changing it does not affect the table.
        """
        return list(self._column_names)

    def resize_table(self, rows: int, columns: int, delete_old: bool) -> pd.DataFrame:
        """Start a new sheet of the requested size, optionally keeping the current data.

        Used by ``MainWindow.new_table``, which loads the returned frame into the backend
        as a new ``Untitled`` dataset.

        * When ``delete_old`` is true (or the table has no columns yet) the sheet is
          replaced by :meth:`set_blank` and the result of :meth:`to_dataframe` is returned.
          Because that sheet is empty, the returned frame is trimmed to
          :attr:`DEFAULT_EXPORT_ROWS` by :attr:`DEFAULT_EXPORT_COLUMNS`.
        * Otherwise the current data is read with :meth:`to_dataframe` (trimmed and
          numerically converted), then padded with empty ``Column N`` columns and empty
          rows, or cut down, to exactly ``rows`` by ``columns``, and shown again with
          :meth:`set_dataframe`. All roles are reset to ``Ignore``.

        No signals are emitted.

        :param rows: Requested number of data rows.
        :param columns: Requested number of columns.
        :param delete_old: Discard the current contents instead of keeping them.
        :returns: The frame now shown in the table (see above for its size).
        """
        if delete_old or not self._column_names:
            self.set_blank(rows, columns)
            return self.to_dataframe()
        df = self.to_dataframe()
        current_rows, current_columns = df.shape
        if columns > current_columns:
            for index in range(current_columns + 1, columns + 1):
                df[f"Column {index}"] = ""
        elif columns < current_columns:
            df = df.iloc[:, :columns]
        if rows > current_rows:
            padding = pd.DataFrame("", index=range(rows - current_rows), columns=df.columns)
            df = pd.concat([df, padding], ignore_index=True)
        elif rows < current_rows:
            df = df.iloc[:rows].copy()
        self.set_dataframe(df, {})
        return df

    def _on_cell_changed(self, row: int, column: int) -> None:
        """React to a changed cell reported by the table's ``cellChanged`` signal.

        Ignored while the sheet is being filled programmatically and for the role row.
        Otherwise the grid first grows when the cell is near its edge (50 rows when it is
        in one of the last two rows, 10 columns when it is in one of the last two
        columns), then :attr:`cell_value_changed` is emitted with the 1-based data row,
        the column name, the cell text and the 1-based column number, and finally
        :attr:`table_edited` is emitted.

        :param row: Table row of the cell; equal to its 1-based data row number.
        :param column: 0-based table column of the cell.
        """
        if not self._loading and row > 0:
            if row >= self.table.rowCount() - 2:
                self._append_rows(50)
            if column >= self.table.columnCount() - 2:
                self._append_columns(10)
            if column < len(self._column_names):
                item = self.table.item(row, column)
                self.cell_value_changed.emit(row, self._column_names[column], item.text() if item else "", column + 1)
            self.table_edited.emit()

    def _trim_empty_extent(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cut ``df`` down to the rows and columns that are actually in use.

        Keeps rows up to the last one with a non-blank cell and columns up to the last one
        with a non-blank cell, where a cell is blank when it is empty after stripping
        whitespace. The column range is widened to include every column whose role in the
        widget's role map is not ``Ignore``. With no data at all,
        :attr:`DEFAULT_EXPORT_ROWS` rows and :attr:`DEFAULT_EXPORT_COLUMNS` columns are
        kept. Both counts are at least 1 and at most the size of ``df``. Interior empty
        rows and columns are kept.

        :param df: Full-grid frame read from the table.
        :returns: A copy of the leading block of ``df``.
        """
        values = df.fillna("").astype(str)
        nonempty_rows = values.apply(lambda row: row.str.strip().ne("").any(), axis=1)
        nonempty_cols = values.apply(lambda column: column.str.strip().ne("").any(), axis=0)
        role_cols = [index for index, name in enumerate(df.columns) if self._roles.get(name, "Ignore") != "Ignore"]
        row_positions = [index for index, has_data in enumerate(nonempty_rows.to_numpy()) if has_data]
        col_positions = [index for index, has_data in enumerate(nonempty_cols.to_numpy()) if has_data]
        last_row = max(row_positions) + 1 if row_positions else self.DEFAULT_EXPORT_ROWS
        last_col = max(col_positions) + 1 if col_positions else self.DEFAULT_EXPORT_COLUMNS
        if role_cols:
            last_col = max(last_col, max(role_cols) + 1)
        last_row = min(max(last_row, 1), len(df.index))
        last_col = min(max(last_col, 1), len(df.columns))
        return df.iloc[:last_row, :last_col].copy()

    def _install_role_combo(self, column_index: int, role: str = "Ignore") -> None:
        """Place a new role dropdown in row 0 of a column.

        The dropdown has the object name ``RoleCombo``, lists
        :data:`~physplot_gui.widgets.column_role_header.ROLE_OPTIONS` and starts at
        ``role``. Its selection changes are routed to :meth:`_role_combo_changed` together
        with ``column_index``, so the dropdown must be re-installed if its column moves
        (see :meth:`_rewire_role_combos`). Any widget already in that cell is replaced.

        :param column_index: 0-based column that receives the dropdown.
        :param role: Role to show initially (default ``Ignore``).
        """
        combo = QtWidgets.QComboBox()
        combo.setObjectName("RoleCombo")
        combo.addItems(ROLE_OPTIONS)
        combo.setCurrentText(role)
        combo.currentTextChanged.connect(
            lambda selected_role, col=column_index: self._role_combo_changed(col, selected_role)
        )
        self.table.setCellWidget(0, column_index, combo)

    def _role_combo_changed(self, column_index: int, role: str) -> None:
        """Record a role picked in a dropdown and emit :attr:`role_changed`.

        Does nothing while the sheet is being filled programmatically or when the column
        index is out of range. Otherwise the widget's role map is updated for that column
        and ``role_changed(column_name, role)`` is emitted.

        :param column_index: 0-based column whose dropdown changed.
        :param role: The newly selected role name.
        """
        if self._loading:
            return
        if column_index >= len(self._column_names):
            return
        column_name = self._column_names[column_index]
        self._roles[column_name] = role
        self.role_changed.emit(column_name, role)

    def _refresh_headers(self) -> None:
        """Relabel both headers and widen any column whose label would be clipped.

        Column headers use :meth:`_display_column_header` (``Column N`` or ``N: name``).
        Row headers are blank for the role row and ``1``, ``2``, ... for the data rows, so
        the numbering is always contiguous after rows are added or removed.
        """
        self.table.setHorizontalHeaderLabels(
            [self._display_column_header(index, name) for index, name in enumerate(self._column_names)]
        )
        self.table.setVerticalHeaderLabels([""] + [str(index) for index in range(1, self.table.rowCount())])
        self._fit_columns_to_headers()

    def _fit_columns_to_headers(self, columns=None) -> None:
        """Widen columns whose header label would be clipped; never shrink user-sized columns.

        For each column the header's size hint (the width its label needs) is compared
        with the current width, and the column is widened only when the hint is larger.
        A column the user made wider by dragging therefore keeps its width.

        :param columns: Iterable of 0-based column indices to check, or ``None`` (the
            default) to check every column.
        """
        header = self.table.horizontalHeader()
        header.ensurePolished()
        for column in range(self.table.columnCount()) if columns is None else columns:
            needed = header.sectionSizeHint(column)
            if needed > self.table.columnWidth(column):
                self.table.setColumnWidth(column, needed)

    def _display_column_header(self, index: int, name: str) -> str:
        """Return the header label shown for a column.

        A column named exactly like its placeholder (``Column 3`` at position 3), or with
        an empty name, is labelled ``Column N``. Any other name is prefixed with the
        1-based position, for example ``3: Voltage``.

        :param index: 0-based column position.
        :param name: The column's current name.
        :returns: The label text.
        """
        default_name = f"Column {index + 1}"
        name = name or default_name
        return default_name if name == default_name else f"{index + 1}: {name}"

    def _append_rows(self, count: int) -> None:
        """Add empty data rows at the bottom of the grid.

        Each new cell gets an empty, centre-aligned item, and the headers are refreshed so
        the new rows are numbered. Cell signals are suppressed while the rows are added
        and no signal is emitted; the rows are padding and do not change the data.

        :param count: Number of rows to add.
        """
        previous_loading = self._loading
        self._loading = True
        start = self.table.rowCount()
        try:
            self.table.setRowCount(start + count)
            for row in range(start, start + count):
                for column in range(self.table.columnCount()):
                    item = QtWidgets.QTableWidgetItem("")
                    item.setTextAlignment(QtCore.Qt.AlignCenter)
                    self.table.setItem(row, column, item)
            self._refresh_headers()
        finally:
            self._loading = previous_loading

    def _append_columns(self, count: int) -> None:
        """Add empty placeholder columns at the right of the grid.

        Each new column is named ``Column N`` after its 1-based position, gets the role
        ``Ignore`` and its own role dropdown, and an empty centre-aligned item in every
        data row. The headers are refreshed and, once the columns exist,
        :attr:`structure_changed` is emitted.

        :param count: Number of columns to add.
        """
        previous_loading = self._loading
        self._loading = True
        start = self.table.columnCount()
        try:
            self.table.setColumnCount(start + count)
            for column in range(start, start + count):
                self._column_names.append(f"Column {column + 1}")
                self._roles.setdefault(self._column_names[-1], "Ignore")
                self._install_role_combo(column, "Ignore")
                for row in range(1, self.table.rowCount()):
                    item = QtWidgets.QTableWidgetItem("")
                    item.setTextAlignment(QtCore.Qt.AlignCenter)
                    self.table.setItem(row, column, item)
            self._refresh_headers()
        finally:
            self._loading = previous_loading
        self.structure_changed.emit()

    def _maybe_extend_rows(self, value: int) -> None:
        """Append 100 rows when the vertical scroll bar nears its end.

        Connected to the vertical scroll bar's ``valueChanged`` signal; rows are added
        when the new position is within 5 steps of the maximum, so scrolling down never
        runs out of rows.

        :param value: New scroll bar position.
        """
        bar = self.table.verticalScrollBar()
        if value >= max(0, bar.maximum() - 5):
            self._append_rows(100)

    def _maybe_extend_columns(self, value: int) -> None:
        """Append 10 columns when the horizontal scroll bar nears its end.

        Connected to the horizontal scroll bar's ``valueChanged`` signal; columns are
        added when the new position is within 3 steps of the maximum, which also emits
        :attr:`structure_changed`.

        :param value: New scroll bar position.
        """
        bar = self.table.horizontalScrollBar()
        if value >= max(0, bar.maximum() - 3):
            self._append_columns(10)

    def _show_cell_menu(self, position) -> None:
        """Open the right-click menu for the grid cells.

        The menu offers **Copy** (:meth:`copy_selection`), **Paste**
        (:meth:`paste_from_clipboard`, at the current cell) and **Clear**
        (:meth:`clear_selection`).

        :param position: Click position in viewport coordinates, as given by
            ``customContextMenuRequested``.
        """
        menu = QtWidgets.QMenu(self)
        menu.addAction("Copy", self.copy_selection)
        menu.addAction("Paste", self.paste_from_clipboard)
        menu.addAction("Clear", self.clear_selection)
        menu.exec(self.table.viewport().mapToGlobal(position))

    def _show_row_menu(self, position) -> None:
        """Open the right-click menu for a row number in the vertical header.

        Nothing happens for the role row (row 0) or for a click below the last row.
        Otherwise the clicked row is selected and the menu offers **Copy Row**
        (:meth:`copy_selection`), **Paste Row** (:meth:`paste_from_clipboard`) and
        **Delete Row** (:meth:`delete_rows` for that single row).

        :param position: Click position in vertical-header coordinates.
        """
        row = self.table.verticalHeader().logicalIndexAt(position)
        if row <= 0:
            return
        self.table.selectRow(row)
        menu = QtWidgets.QMenu(self)
        menu.addAction("Copy Row", self.copy_selection)
        menu.addAction("Paste Row", self.paste_from_clipboard)
        menu.addAction("Delete Row", lambda: self.delete_rows([row]))
        menu.exec(self.table.verticalHeader().mapToGlobal(position))

    def _show_column_menu(self, position) -> None:
        """Open the right-click menu for a column header.

        Nothing happens for a click beside the last column. Otherwise the clicked column
        is selected and the menu offers **Rename Column** (:meth:`rename_column`), a
        separator, **Copy Column** (:meth:`copy_selection`), **Paste Column**
        (:meth:`paste_from_clipboard`) and **Delete Column** (:meth:`delete_columns` for
        that single column).

        :param position: Click position in horizontal-header coordinates.
        """
        column = self.table.horizontalHeader().logicalIndexAt(position)
        if column < 0:
            return
        self.table.selectColumn(column)
        menu = QtWidgets.QMenu(self)
        menu.addAction("Rename Column", lambda: self.rename_column(column))
        menu.addSeparator()
        menu.addAction("Copy Column", self.copy_selection)
        menu.addAction("Paste Column", self.paste_from_clipboard)
        menu.addAction("Delete Column", lambda: self.delete_columns([column]))
        menu.exec(self.table.horizontalHeader().mapToGlobal(position))

    def rename_column(self, column: int) -> None:
        """Ask the user for a new column name and apply it.

        Runs when a column header is double-clicked or **Rename Column** is chosen from
        the header menu. A modal "Rename Column" dialog asks for the "Column name:",
        pre-filled with the current name. Cancelling leaves the column unchanged. The
        accepted text is passed to :meth:`rename_column_to`; if that rejects it (empty or
        duplicate name) a warning message box explains why and the old name is kept.

        :param column: 0-based column to rename; out-of-range indices are ignored.
        """
        if column < 0 or column >= len(self._column_names):
            return
        old_name = self._column_names[column]
        new_name, accepted = QtWidgets.QInputDialog.getText(
            self,
            "Rename Column",
            "Column name:",
            QtWidgets.QLineEdit.EchoMode.Normal,
            old_name,
        )
        if not accepted:
            return
        try:
            self.rename_column_to(column, new_name)
        except ValueError as exc:
            QtWidgets.QMessageBox.warning(self, "Rename Column", str(exc))

    def rename_column_to(self, column: int, new_name: str) -> None:
        """Rename a column without asking the user.

        Surrounding whitespace is stripped from ``new_name``. Renaming to the current name,
        or an out-of-range column, does nothing. Otherwise the column's role moves to the
        new name, the header is relabelled (normally ``N: new_name``, see
        :meth:`_display_column_header`) and widened if the label would be clipped, and the
        signals :attr:`column_renamed` ``(old_name, new_name)``,
        :attr:`structure_changed` and :attr:`table_edited` are emitted in that order.

        :param column: 0-based column to rename.
        :param new_name: The new column name.
        :raises ValueError: If the stripped name is empty or already used by another
            column.
        """
        if column < 0 or column >= len(self._column_names):
            return
        old_name = self._column_names[column]
        new_name = str(new_name).strip()
        if not new_name:
            raise ValueError("Column name cannot be empty.")
        if new_name != old_name and new_name in self._column_names:
            raise ValueError(f"Column '{new_name}' already exists.")
        if new_name == old_name:
            return
        role = self._roles.pop(old_name, "Ignore")
        self._column_names[column] = new_name
        self._roles[new_name] = role
        self.table.setHorizontalHeaderItem(column, QtWidgets.QTableWidgetItem(self._display_column_header(column, new_name)))
        self._fit_columns_to_headers([column])
        self.column_renamed.emit(old_name, new_name)
        self.structure_changed.emit()
        self.table_edited.emit()

    def copy_selection(self) -> None:
        """Copy the selected block to the clipboard as tab-separated text.

        Only the first selected range is copied, and the role row is skipped if the
        selection includes it. Each table row becomes one line with its cells joined by
        tabs; lines are joined with newlines. Nothing happens when nothing is selected.
        Used by the Copy shortcut and by the Copy, Copy Row and Copy Column menu items.
        """
        ranges = self.table.selectedRanges()
        if not ranges:
            return
        selected = ranges[0]
        lines = []
        for row in range(max(1, selected.topRow()), selected.bottomRow() + 1):
            values = []
            for column in range(selected.leftColumn(), selected.rightColumn() + 1):
                item = self.table.item(row, column)
                values.append(item.text() if item else "")
            lines.append("\t".join(values))
        QtWidgets.QApplication.clipboard().setText("\n".join(lines))

    def paste_from_clipboard(self) -> None:
        """Paste tab-separated clipboard text into the sheet at the current cell.

        The clipboard text is split into lines and each line on tabs, giving a block whose
        top-left corner lands on the current cell (moved down to data row 1 if the current
        cell is in the role row). The grid first grows, 100 rows and 10 columns at a time,
        until the block fits. The cells are then written in one go, after which
        :attr:`cell_value_changed` is emitted once for every pasted cell and
        :attr:`table_edited` once. Nothing happens when the clipboard holds no text. Used
        by the Paste shortcut and by the Paste, Paste Row and Paste Column menu items.
        """
        text = QtWidgets.QApplication.clipboard().text()
        if not text:
            return
        start_row = max(1, self.table.currentRow())
        start_column = max(0, self.table.currentColumn())
        rows = [line.split("\t") for line in text.splitlines()]
        while start_row + len(rows) >= self.table.rowCount():
            self._append_rows(100)
        while rows and start_column + max(len(row) for row in rows) > self.table.columnCount():
            self._append_columns(10)
        self._loading = True
        try:
            for row_offset, row_values in enumerate(rows):
                for column_offset, value in enumerate(row_values):
                    item = QtWidgets.QTableWidgetItem(value)
                    item.setTextAlignment(QtCore.Qt.AlignCenter)
                    self.table.setItem(start_row + row_offset, start_column + column_offset, item)
        finally:
            self._loading = False
        for row_offset, row_values in enumerate(rows):
            for column_offset, value in enumerate(row_values):
                column = start_column + column_offset
                if column < len(self._column_names):
                    self.cell_value_changed.emit(start_row + row_offset, self._column_names[column], value, column + 1)
        self.table_edited.emit()

    def clear_selection(self) -> None:
        """Empty every selected data cell.

        Role dropdowns are never touched. Each cell whose text changes goes through the
        normal edit path, so :attr:`cell_value_changed` and :attr:`table_edited` are
        emitted for it; :attr:`table_edited` is emitted once more at the end. Used by the
        **Clear** item of the cell context menu.
        """
        for item in self.table.selectedItems():
            if item.row() > 0:
                item.setText("")
        self.table_edited.emit()

    def delete_rows(self, rows: list[int]) -> None:
        """Remove data rows from the sheet.

        Row 0 and duplicate numbers are ignored; the remaining rows are removed from the
        bottom up so the numbers keep referring to the rows as they were. If fewer than
        :attr:`MIN_DATA_ROWS` data rows remain, empty rows are added back at the bottom.
        The row headers are renumbered, then :attr:`rows_deleted` is emitted with the
        sorted row numbers (only if there were any) and :attr:`table_edited` is emitted.
        The main window records the deletion as a ``DeleteRowsStep``.

        :param rows: Table row indices to delete, which equal the 1-based data row numbers
            shown in the row header.
        """
        deleted = sorted({row for row in rows if row > 0})
        for row in sorted(deleted, reverse=True):
            self.table.removeRow(row)
        if self.table.rowCount() < self.MIN_DATA_ROWS + 1:
            self._append_rows(self.MIN_DATA_ROWS + 1 - self.table.rowCount())
        self._refresh_headers()
        if deleted:
            self.rows_deleted.emit(deleted)
        self.table_edited.emit()

    def delete_columns(self, columns: list[int]) -> None:
        """Remove columns, with their names and roles, from the sheet.

        Out-of-range indices and duplicates are ignored; the columns are removed from the
        right so the indices keep referring to the columns as they were. If fewer than
        :attr:`MIN_DATA_COLUMNS` columns remain, placeholder columns are added back at the
        right (which emits :attr:`structure_changed` as well). Every role dropdown is then
        re-installed so it is bound to its column's new position, and the headers are
        relabelled, which renumbers the ``N: name`` labels.
        Finally :attr:`structure_changed`, :attr:`columns_deleted` (only if any column was
        removed) and :attr:`table_edited` are emitted. The main window records the
        deletion as a ``DeleteColumnsStep``.

        :param columns: 0-based column indices to delete.
        """
        deleted_names = []
        deleted_numbers = []
        for column in sorted(set(columns)):
            if 0 <= column < len(self._column_names):
                deleted_names.append(self._column_names[column])
                deleted_numbers.append(column + 1)
        for column in sorted(set(columns), reverse=True):
            if 0 <= column < self.table.columnCount():
                self.table.removeColumn(column)
                if column < len(self._column_names):
                    self._roles.pop(self._column_names[column], None)
                    self._column_names.pop(column)
        if self.table.columnCount() < self.MIN_DATA_COLUMNS:
            self._append_columns(self.MIN_DATA_COLUMNS - self.table.columnCount())
        self._rewire_role_combos()
        self._refresh_headers()
        self.structure_changed.emit()
        if deleted_names:
            self.columns_deleted.emit(deleted_names, deleted_numbers)
        self.table_edited.emit()

    def _rewire_role_combos(self) -> None:
        """Re-install every role dropdown so it reports its column's current position.

        Needed after columns are removed, because each dropdown is bound to the column
        index it was created for. Each new dropdown shows the column's role from the
        widget's role map (``Ignore`` if none) and emits no signal while being created.
        """
        for column_index, column_name in enumerate(self._column_names):
            self._install_role_combo(column_index, self._roles.get(column_name, "Ignore"))

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        """Handle the platform Copy and Paste shortcuts for the sheet.

        The standard Copy key sequence (``Cmd+C`` on macOS, ``Ctrl+C`` elsewhere) runs
        :meth:`copy_selection` and the standard Paste sequence (``Cmd+V``/``Ctrl+V``) runs
        :meth:`paste_from_clipboard`. Every other key is passed on to the default
        ``QWidget`` handling.

        :param event: The key press event.
        """
        if event.matches(QtGui.QKeySequence.StandardKey.Copy):
            self.copy_selection()
            return
        if event.matches(QtGui.QKeySequence.StandardKey.Paste):
            self.paste_from_clipboard()
            return
        super().keyPressEvent(event)
