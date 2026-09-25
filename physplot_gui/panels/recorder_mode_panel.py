"""Recorder mode controls."""

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
    def __init__(self, actions, parent=None):
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
        self.sequence.set_tracking(True)

    def refresh_timeline(self, rows: list[dict]) -> None:
        self.sequence.refresh_timeline(rows)

    def refresh_plot(self) -> None:
        return None
