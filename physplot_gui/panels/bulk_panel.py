"""Bulk automation controls for recorder mode."""

from physplot.qt_compat import QtWidgets


class BulkPanel(QtWidgets.QFrame):
    def __init__(self, actions, parent=None):
        super().__init__(parent)
        self.setObjectName("Panel")
        self.actions = actions
        layout = QtWidgets.QGridLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setHorizontalSpacing(8)
        layout.setVerticalSpacing(6)
        title = QtWidgets.QLabel("Bulk Run")
        title.setObjectName("PanelTitle")
        layout.addWidget(title, 0, 0, 1, 3)
        note = QtWidgets.QLabel("Plot modules and formatting are read from the sequence.")
        note.setObjectName("MutedLabel")
        layout.addWidget(note, 1, 0, 1, 3)
        self.input_folder = self._path_row(layout, 2, "Input Folder:", actions.browse_input_folder)
        self.workflow_file = self._path_row(layout, 3, "Sequence File:", actions.browse_workflow_file)
        self.workflow_file.setPlaceholderText("Optional; blank uses current Build Protocol sequence")
        self.output_folder = self._path_row(layout, 4, "Output Folder:", actions.browse_output_folder)
        self.run_button = QtWidgets.QPushButton("Run Bulk Workflow")
        self.run_button.setProperty("primary", True)
        self.run_button.setMinimumHeight(74)
        self.run_button.clicked.connect(lambda: actions.run_bulk_workflow(self.payload()))
        layout.addWidget(self.run_button, 5, 0, 1, 3)

    def _path_row(self, layout, row: int, label: str, callback):
        field = QtWidgets.QLineEdit()
        browse = QtWidgets.QPushButton("Browse")
        browse.clicked.connect(lambda: callback(field))
        layout.addWidget(QtWidgets.QLabel(label), row, 0)
        layout.addWidget(field, row, 1)
        layout.addWidget(browse, row, 2)
        return field

    def payload(self) -> dict:
        return {
            "input_folder": self.input_folder.text().strip(),
            "workflow_file": self.workflow_file.text().strip(),
            "output_folder": self.output_folder.text().strip(),
        }
