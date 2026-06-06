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
        layout.addWidget(title, 0, 0, 1, 5)
        self.input_folder = self._path_row(layout, 1, "Input Folder:", actions.browse_input_folder)
        self.workflow_file = self._path_row(layout, 2, "Workflow File:", actions.browse_workflow_file)
        self.output_folder = self._path_row(layout, 3, "Output Folder:", actions.browse_output_folder)
        self.plot_mode = QtWidgets.QComboBox()
        self.plot_mode.addItems(["Individual", "Overlay", "Subplot Grid", "Grouped Subplot"])
        layout.addWidget(QtWidgets.QLabel("Plot Mode:"), 1, 3)
        layout.addWidget(self.plot_mode, 1, 4)
        file_types = QtWidgets.QHBoxLayout()
        self.png = QtWidgets.QCheckBox("PNG")
        self.pdf = QtWidgets.QCheckBox("PDF")
        self.svg = QtWidgets.QCheckBox("SVG")
        self.csv = QtWidgets.QCheckBox("CSV")
        self.png.setChecked(True)
        self.pdf.setChecked(True)
        for checkbox in (self.png, self.pdf, self.svg, self.csv):
            file_types.addWidget(checkbox)
        layout.addWidget(QtWidgets.QLabel("File Types:"), 2, 3)
        layout.addLayout(file_types, 2, 4)
        self.dpi = QtWidgets.QSpinBox()
        self.dpi.setRange(72, 1200)
        self.dpi.setValue(300)
        layout.addWidget(QtWidgets.QLabel("DPI:"), 3, 3)
        layout.addWidget(self.dpi, 3, 4)
        self.run_button = QtWidgets.QPushButton("Run Bulk Workflow")
        self.run_button.setProperty("primary", True)
        self.run_button.setMinimumHeight(74)
        self.run_button.clicked.connect(lambda: actions.run_bulk_workflow(self.payload()))
        layout.addWidget(self.run_button, 4, 0, 1, 5)

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
            "plot_mode": self.plot_mode.currentText(),
            "dpi": self.dpi.value(),
        }
