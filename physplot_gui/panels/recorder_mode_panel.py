"""Recorder mode controls."""

from physplot.qt_compat import QtCore, QtWidgets

from .bulk_panel import BulkPanel
from .workflow_panel import WorkflowPanel


class SequenceTablePanel(QtWidgets.QFrame):
    def __init__(self, actions, title: str = "Sequence", show_buttons: bool = True, parent=None):
        super().__init__(parent)
        self.setObjectName("Panel")
        self.actions = actions
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
        self.timeline = QtWidgets.QTableWidget(0, 5)
        self.timeline.setHorizontalHeaderLabels(["#", "Operation", "Details", "Target/File/Column", "Delete"])
        self.timeline.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.timeline.verticalHeader().hide()
        self.code_view = QtWidgets.QPlainTextEdit()
        self.code_view.setReadOnly(True)
        self.code_view.setObjectName("CodeView")
        self.stack.addWidget(self.timeline)
        self.stack.addWidget(self.code_view)
        layout.addWidget(self.stack, 1)
        if show_buttons:
            buttons = QtWidgets.QHBoxLayout()
            for text, callback in (
                ("Save Sequence.py", actions.save_workflow),
                ("Copy as Script", actions.copy_workflow_script),
                ("Clear Sequence", actions.clear_recording),
            ):
                button = QtWidgets.QPushButton(text)
                button.clicked.connect(callback)
                buttons.addWidget(button)
            buttons.addStretch(1)
            layout.addLayout(buttons)

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
            delete_button = QtWidgets.QPushButton("Delete")
            delete_button.clicked.connect(lambda checked=False, i=index: self._delete_row(i))
            self.timeline.setCellWidget(index, 4, delete_button)
        if hasattr(self.actions, "sequence_code_text"):
            self.code_view.setPlainText(self.actions.sequence_code_text())
        else:
            self.code_view.setPlainText("\n".join(row.get("code") or self._fallback_code_line(row) for row in rows))

    def _set_view_mode(self, index: int) -> None:
        self.stack.setCurrentIndex(index)

    @staticmethod
    def _fallback_code_line(row: dict) -> str:
        return f"# {row.get('action', 'Step')}: {row.get('details', '')} -> {row.get('target', '')}"

    def _delete_row(self, index: int) -> None:
        window = self.window()
        if hasattr(window, "delete_timeline_step"):
            window.delete_timeline_step(index)


class RecorderModePanel(QtWidgets.QWidget):
    def __init__(self, actions, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 8)
        layout.setSpacing(8)
        left = QtWidgets.QVBoxLayout()
        self.workflow = WorkflowPanel(actions, recorder=True)
        left.addWidget(self.workflow)
        left.addWidget(BulkPanel(actions), 2)
        layout.addLayout(left, 3)
        self.sequence = SequenceTablePanel(actions, title="Sequence", show_buttons=True)
        layout.addWidget(self.sequence, 6)

    def set_recording(self, active: bool) -> None:
        self.sequence.set_tracking(True)
        self.workflow.set_recording(active)

    def refresh_timeline(self, rows: list[dict]) -> None:
        self.sequence.refresh_timeline(rows)

    def refresh_plot(self) -> None:
        return None
