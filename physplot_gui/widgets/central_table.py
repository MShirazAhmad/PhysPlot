"""Spreadsheet-style central table with role dropdowns."""

from __future__ import annotations

import pandas as pd
from physplot.qt_compat import QtCore, QtGui, QtWidgets

from .column_role_header import ROLE_OPTIONS


class CentralTable(QtWidgets.QWidget):
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
        data = pd.DataFrame("", index=range(rows), columns=[f"Column {i}" for i in range(1, columns + 1)])
        self.set_dataframe(data, {})

    def set_dataframe(self, df: pd.DataFrame, roles: dict[str, str] | None = None) -> None:
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
        self._loading = True
        try:
            for column_index, column_name in enumerate(self._column_names):
                combo = self.table.cellWidget(0, column_index)
                if isinstance(combo, QtWidgets.QComboBox):
                    combo.setCurrentText(roles.get(column_name, "Ignore"))
        finally:
            self._loading = False

    def to_dataframe(self, trim_empty: bool = True) -> pd.DataFrame:
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
        return list(self._column_names)

    def resize_table(self, rows: int, columns: int, delete_old: bool) -> pd.DataFrame:
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
        combo = QtWidgets.QComboBox()
        combo.setObjectName("RoleCombo")
        combo.addItems(ROLE_OPTIONS)
        combo.setCurrentText(role)
        combo.currentTextChanged.connect(
            lambda selected_role, col=column_index: self._role_combo_changed(col, selected_role)
        )
        self.table.setCellWidget(0, column_index, combo)

    def _role_combo_changed(self, column_index: int, role: str) -> None:
        if self._loading:
            return
        if column_index >= len(self._column_names):
            return
        column_name = self._column_names[column_index]
        self._roles[column_name] = role
        self.role_changed.emit(column_name, role)

    def _refresh_headers(self) -> None:
        self.table.setHorizontalHeaderLabels(
            [self._display_column_header(index, name) for index, name in enumerate(self._column_names)]
        )
        self.table.setVerticalHeaderLabels([""] + [str(index) for index in range(1, self.table.rowCount())])

    def _display_column_header(self, index: int, name: str) -> str:
        default_name = f"Column {index + 1}"
        name = name or default_name
        return default_name if name == default_name else f"{index + 1}: {name}"

    def _append_rows(self, count: int) -> None:
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
        bar = self.table.verticalScrollBar()
        if value >= max(0, bar.maximum() - 5):
            self._append_rows(100)

    def _maybe_extend_columns(self, value: int) -> None:
        bar = self.table.horizontalScrollBar()
        if value >= max(0, bar.maximum() - 3):
            self._append_columns(10)

    def _show_cell_menu(self, position) -> None:
        menu = QtWidgets.QMenu(self)
        menu.addAction("Copy", self.copy_selection)
        menu.addAction("Paste", self.paste_from_clipboard)
        menu.addAction("Clear", self.clear_selection)
        menu.exec(self.table.viewport().mapToGlobal(position))

    def _show_row_menu(self, position) -> None:
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
        self.column_renamed.emit(old_name, new_name)
        self.structure_changed.emit()
        self.table_edited.emit()

    def copy_selection(self) -> None:
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
        for item in self.table.selectedItems():
            if item.row() > 0:
                item.setText("")
        self.table_edited.emit()

    def delete_rows(self, rows: list[int]) -> None:
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
        for column_index, column_name in enumerate(self._column_names):
            self._install_role_combo(column_index, self._roles.get(column_name, "Ignore"))

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.matches(QtGui.QKeySequence.StandardKey.Copy):
            self.copy_selection()
            return
        if event.matches(QtGui.QKeySequence.StandardKey.Paste):
            self.paste_from_clipboard()
            return
        super().keyPressEvent(event)
