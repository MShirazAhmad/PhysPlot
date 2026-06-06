"""Bottom status bar."""

from pathlib import Path

from physplot.qt_compat import QtWidgets


class PhysPlotStatusBar(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("StatusBar")
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(22)
        self.ready_dot = QtWidgets.QLabel()
        self.ready_dot.setFixedSize(10, 10)
        self.ready_dot.setStyleSheet("background:#1fb34f;border-radius:5px;")
        self.status = QtWidgets.QLabel("Status: Ready")
        self.rows = QtWidgets.QLabel("Rows: 0")
        self.columns = QtWidgets.QLabel("Columns: 0")
        self.file = QtWidgets.QLabel("File: -")
        self.workflow = QtWidgets.QLabel("Workflow: Untitled")
        self.mode = QtWidgets.QLabel("Mode: Simple")
        layout.addWidget(self.ready_dot)
        layout.addWidget(self.status)
        layout.addStretch(1)
        for widget in (self.rows, self.columns, self.file, self.workflow, self.mode):
            layout.addWidget(widget)

    def update_state(self, state) -> None:
        simple = state.mode == "Simple"
        self.ready_dot.setVisible(not simple)
        self.workflow.setVisible(not simple)
        self.mode.setVisible(not simple)
        self.rows.setText(f"Rows: {state.row_count}")
        self.columns.setText(f"Columns: {state.column_count}")
        self.file.setText(f"File: {Path(state.current_file).name if state.current_file else '-'}")
        self.workflow.setText(f"Workflow: {Path(state.workflow_file).name if state.workflow_file else 'Untitled'}")
        self.mode.setText(f"Mode: {state.mode}")

    def set_message(self, message: str) -> None:
        self.status.setText(f"Status: {message}")
