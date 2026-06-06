"""Transformation controls and applied pipeline table."""

from physplot.qt_compat import QtCore, QtWidgets
from physplot_gui.panels.simple_mode_panel import AutoWidthComboBox


FUNCTIONS = ["multiply", "normalize_max", "add", "subtract", "divide", "log", "log10", "baseline_subtract"]


class TransformationPanel(QtWidgets.QFrame):
    def __init__(self, actions, advanced: bool = True, parent=None):
        super().__init__(parent)
        self.setObjectName("Panel")
        self.actions = actions
        self.advanced = advanced
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)
        title = QtWidgets.QLabel("Transformation Pipeline" if advanced else "Apply Mathematical Transformation to Column")
        title.setObjectName("PanelTitle")
        layout.addWidget(title)
        form = QtWidgets.QGridLayout()
        form.setHorizontalSpacing(8)
        form.setVerticalSpacing(6)
        self.input_column = AutoWidthComboBox()
        self.output_column = AutoWidthComboBox()
        self.output_column.setEditable(True)
        self.output_column.setPlaceholderText("New Column...")
        self.category = AutoWidthComboBox()
        self.category.addItems(["Arithmetic", "Normalize", "Log", "Baseline"])
        self.function = AutoWidthComboBox()
        self.function.addItems(FUNCTIONS)
        self.params = QtWidgets.QLineEdit()
        self.params.setPlaceholderText("factor=1000")
        form.addWidget(QtWidgets.QLabel("Input Column:"), 0, 0)
        form.addWidget(self.input_column, 0, 1)
        form.addWidget(QtWidgets.QLabel("Output Column:"), 0, 2)
        form.addWidget(self.output_column, 0, 3)
        if advanced:
            form.addWidget(QtWidgets.QLabel("Category:"), 1, 0)
            form.addWidget(self.category, 1, 1)
            form.addWidget(QtWidgets.QLabel("Function:"), 1, 2)
            form.addWidget(self.function, 1, 3)
            form.addWidget(QtWidgets.QLabel("Parameters:"), 2, 0)
            form.addWidget(self.params, 2, 1, 1, 3)
        else:
            form.addWidget(QtWidgets.QLabel("Function:"), 1, 0)
            form.addWidget(self.function, 1, 1)
            form.addWidget(QtWidgets.QLabel("Parameters:"), 1, 2)
            form.addWidget(self.params, 1, 3)
        form.setColumnStretch(1, 1)
        form.setColumnStretch(3, 1)
        layout.addLayout(form)
        buttons = QtWidgets.QHBoxLayout()
        self.add_button = QtWidgets.QPushButton("+ Add Step")
        self.add_button.clicked.connect(lambda: self.actions.add_pipeline_step(self.step_payload()))
        self.apply_button = QtWidgets.QPushButton("Apply")
        self.apply_button.clicked.connect(lambda: self.actions.apply_pipeline_step(self.step_payload()))
        buttons.addWidget(self.add_button)
        buttons.addWidget(self.apply_button)
        buttons.addStretch(1)
        layout.addLayout(buttons)
        if advanced:
            subtitle = QtWidgets.QLabel("Applied Transformations (Executed in Order)")
            subtitle.setObjectName("PanelTitle")
            layout.addWidget(subtitle)
            self.table = QtWidgets.QTableWidget(0, 6)
            self.table.setHorizontalHeaderLabels(["Step", "Input Column", "Function", "Parameters", "Output Column", "Delete"])
            self.table.horizontalHeader().setStretchLastSection(False)
            self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Interactive)
            self.table.setColumnWidth(0, 48)
            self.table.setColumnWidth(1, 150)
            self.table.setColumnWidth(2, 132)
            self.table.setColumnWidth(3, 150)
            self.table.setColumnWidth(4, 158)
            self.table.setColumnWidth(5, 74)
            self.table.verticalHeader().hide()
            self.table.setMinimumHeight(118)
            layout.addWidget(self.table, 1)
            footer = QtWidgets.QHBoxLayout()
            for text, callback in (
                ("Clear All", self.actions.clear_pipeline),
                ("Import Pipeline", self.actions.import_pipeline),
                ("Export Pipeline", self.actions.export_pipeline),
            ):
                button = QtWidgets.QPushButton(text)
                button.clicked.connect(callback)
                footer.addWidget(button)
            footer.addStretch(1)
            layout.addLayout(footer)

    def step_payload(self) -> dict:
        return {
            "input": self.input_column.currentData() or self.input_column.currentText(),
            "function": self.function.currentText(),
            "params": self.params.text().strip(),
            "output": self._combo_value(self.output_column),
        }

    def refresh_columns(self, columns: list[str]) -> None:
        current_input = self.input_column.currentData()
        output_current = self.output_column.currentData() or self.output_column.currentText()
        self.input_column.clear()
        self.output_column.clear()
        for index, column in enumerate(columns, start=1):
            label = self._column_label(index, column)
            self.input_column.addItem(label, column)
            self.output_column.addItem(label, column)
        if current_input in columns:
            self.input_column.setCurrentText(self._column_label(columns.index(current_input) + 1, current_input))
        elif columns:
            self.input_column.setCurrentIndex(0)
        if output_current in columns:
            self.output_column.setCurrentText(self._column_label(columns.index(output_current) + 1, output_current))
        else:
            self.output_column.setEditText(str(output_current or ""))

    def refresh_pipeline(self, rows: list[dict]) -> None:
        if not self.advanced:
            return
        self.table.setRowCount(len(rows))
        for index, row in enumerate(rows):
            values = [
                str(index + 1),
                row.get("input", ""),
                row.get("function", ""),
                row.get("params", ""),
                row.get("output", ""),
            ]
            for column, value in enumerate(values):
                item = QtWidgets.QTableWidgetItem(value)
                item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
                self.table.setItem(index, column, item)
            delete_button = QtWidgets.QPushButton("Delete")
            delete_button.clicked.connect(lambda checked=False, i=index: self.actions.delete_pipeline_step(i))
            self.table.setCellWidget(index, 5, delete_button)

    @staticmethod
    def _column_label(index: int, column: str) -> str:
        default_name = f"Column {index}"
        column = str(column or default_name)
        return default_name if column == default_name else f"{index}: {column}"

    @staticmethod
    def _combo_value(combo: QtWidgets.QComboBox) -> str:
        text = combo.currentText().strip()
        if combo.currentIndex() >= 0 and text == combo.itemText(combo.currentIndex()):
            return combo.currentData() or text
        return text
