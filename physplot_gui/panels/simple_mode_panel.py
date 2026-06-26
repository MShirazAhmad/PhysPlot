"""Three-section Simple mode controls."""

from __future__ import annotations

from physplot.qt_compat import QtCore, QtGui, QtWidgets


class AutoWidthComboBox(QtWidgets.QComboBox):
    """Compact combo box whose popup expands to fit long scientific labels."""

    def showPopup(self) -> None:
        self._resize_popup_to_contents()
        super().showPopup()

    def _resize_popup_to_contents(self) -> None:
        view = self.view()
        width = self.width()
        metrics = self.fontMetrics()
        for index in range(self.count()):
            width = max(width, metrics.horizontalAdvance(self.itemText(index)) + 42)
        scrollbar_width = self.style().pixelMetric(QtWidgets.QStyle.PixelMetric.PM_ScrollBarExtent)
        view.setMinimumWidth(width + scrollbar_width)


class SimpleModePanel(QtWidgets.QWidget):
    def __init__(self, actions, parent=None):
        super().__init__(parent)
        self.actions = actions
        self._columns: list[str] = []
        self._plotter_entries: list[dict] = []

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 6, 0, 6)
        layout.setSpacing(6)
        layout.addWidget(self._data_importer_panel(), 1)
        layout.addWidget(self._transform_panel(), 2)
        layout.addWidget(self._plotter_panel(), 1)
        self.refresh_plotters()

    def _data_importer_panel(self):
        frame = self._panel()
        layout = QtWidgets.QGridLayout(frame)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setHorizontalSpacing(8)
        layout.setVerticalSpacing(7)
        title = self._title("1. Data Importer")

        self.loader = AutoWidthComboBox()
        for entry in self.actions.backend_loader_entries():
            self.loader.addItem(entry["display_name"], entry)
            if not entry.get("enabled", True):
                item = self.loader.model().item(self.loader.count() - 1)
                item.setFlags(item.flags() & ~QtCore.Qt.ItemFlag.ItemIsEnabled)
                item.setForeground(QtGui.QColor("#94a3b8"))

        import_button = QtWidgets.QPushButton("Import Data")
        import_button.clicked.connect(lambda: self.actions.import_data(self._loader_entry()))
        import_folder_button = QtWidgets.QPushButton("Import Folder")
        import_folder_button.clicked.connect(self.actions.import_folder)
        export_button = QtWidgets.QPushButton("Export Data")
        export_button.clicked.connect(self.actions.export_data)

        layout.addWidget(title, 0, 0, 1, 3)
        layout.addWidget(QtWidgets.QLabel("Data Loader:"), 1, 0)
        layout.addWidget(self.loader, 1, 1, 1, 2)
        layout.addWidget(import_button, 2, 0)
        layout.addWidget(import_folder_button, 2, 1)
        layout.addWidget(export_button, 2, 2)
        layout.setColumnStretch(1, 1)
        return frame

    def _transform_panel(self):
        frame = self._panel()
        layout = QtWidgets.QGridLayout(frame)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setHorizontalSpacing(8)
        layout.setVerticalSpacing(7)
        layout.addWidget(self._title("2. Apply Mathematical Transformation"), 0, 0, 1, 6)

        self.input_column = AutoWidthComboBox()
        self.function = AutoWidthComboBox()
        for entry in self.actions.simple_function_entries():
            self.function.addItem(entry["display_name"], entry)
        self.offset = QtWidgets.QLineEdit("0")
        self.offset.setMaximumWidth(84)
        self.output_column = AutoWidthComboBox()
        self.output_column.setEditable(True)
        self.output_column.setInsertPolicy(QtWidgets.QComboBox.InsertPolicy.NoInsert)
        self.output_column.setPlaceholderText("Output column")
        apply_button = QtWidgets.QPushButton("Apply")
        apply_button.clicked.connect(self._apply)

        formula = QtWidgets.QHBoxLayout()
        formula.setSpacing(7)
        formula.addWidget(QtWidgets.QLabel("Output"))
        formula.addWidget(self.output_column, 2)
        formula.addWidget(QtWidgets.QLabel("="))
        formula.addWidget(self.function, 2)
        formula.addWidget(QtWidgets.QLabel("("))
        formula.addWidget(QtWidgets.QLabel("Input"))
        formula.addWidget(self.input_column, 2)
        formula.addWidget(QtWidgets.QLabel("+"))
        formula.addWidget(self.offset)
        formula.addWidget(QtWidgets.QLabel(")"))
        formula.addWidget(apply_button)
        layout.addLayout(formula, 1, 0, 1, 6)

        applied_label = QtWidgets.QLabel("Applied:")
        applied_label.setObjectName("MutedLabel")
        self.applied = QtWidgets.QListWidget()
        self.applied.setObjectName("CompactList")
        self.applied.setMaximumHeight(54)
        self.applied.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
        layout.addWidget(applied_label, 2, 0)
        layout.addWidget(self.applied, 2, 1, 1, 5)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(3, 1)
        return frame

    def _plotter_panel(self):
        frame = self._panel()
        layout = QtWidgets.QGridLayout(frame)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setHorizontalSpacing(8)
        layout.setVerticalSpacing(7)
        layout.addWidget(self._title("3. Plotter Module"), 0, 0, 1, 2)

        self.plotter = AutoWidthComboBox()
        self.plotter.currentIndexChanged.connect(self._plotter_changed)
        self.plot_type = AutoWidthComboBox()
        self.style_module = AutoWidthComboBox()
        reload_styles_button = QtWidgets.QPushButton("Reload")
        reload_styles_button.clicked.connect(self.refresh_styles)
        generate_button = QtWidgets.QPushButton("Generate Plot")
        generate_button.setProperty("primary", True)
        generate_button.clicked.connect(self._generate_plot)
        export_button = QtWidgets.QPushButton("Export Plot")
        export_button.clicked.connect(self.actions.export_module_plot)

        layout.addWidget(QtWidgets.QLabel("Plotter Module:"), 1, 0)
        layout.addWidget(self.plotter, 1, 1)
        layout.addWidget(QtWidgets.QLabel("Plot Type / Protocol:"), 2, 0)
        layout.addWidget(self.plot_type, 2, 1)
        layout.addWidget(QtWidgets.QLabel("Template:"), 3, 0)
        style_layout = QtWidgets.QHBoxLayout()
        style_layout.setSpacing(6)
        style_layout.addWidget(self.style_module, 1)
        style_layout.addWidget(reload_styles_button)
        layout.addLayout(style_layout, 3, 1)
        layout.addWidget(generate_button, 4, 0)
        layout.addWidget(export_button, 4, 1)
        layout.setColumnStretch(1, 1)
        self.refresh_styles()
        return frame

    def refresh_columns(self, columns: list[str]) -> None:
        """Refresh input/output column menus without duplicating default names."""
        self._columns = list(columns)
        current = self.input_column.currentData()
        output_current = self.output_column.currentData() or self.output_column.currentText()
        self.input_column.clear()
        self.output_column.clear()
        for index, column in enumerate(columns, start=1):
            label = self._column_label(index, column)
            self.input_column.addItem(label, column)
            self.output_column.addItem(label, column)
        if current in columns:
            self.input_column.setCurrentText(self._column_label(columns.index(current) + 1, current))
        elif columns:
            self.input_column.setCurrentIndex(0)
        if output_current in columns:
            self.output_column.setCurrentText(self._column_label(columns.index(output_current) + 1, output_current))
        else:
            self.output_column.setEditText(str(output_current or ""))

    def refresh_pipeline(self, rows: list[dict]) -> None:
        self.applied.clear()
        compact_rows = rows[-2:]
        if not compact_rows:
            self.applied.addItem("No transformations yet")
            return
        start = len(rows) - len(compact_rows) + 1
        for offset, row in enumerate(compact_rows):
            params = row.get("params", "-")
            function = row.get("function", "")
            label = f"{start + offset} {row.get('input', '')} -> {function}"
            if params and params != "-":
                label += f"({params})"
            label += f" -> {row.get('output', '')}"
            self.applied.addItem(label)

    def refresh_plotters(self) -> None:
        current = self.plotter.currentData() if hasattr(self, "plotter") else None
        self._plotter_entries = self.actions.plotter_entries()
        self.plotter.blockSignals(True)
        self.plotter.clear()
        for entry in self._plotter_entries:
            self.plotter.addItem(entry["name"], entry["plotter_id"])
        if current:
            index = self.plotter.findData(current)
            if index >= 0:
                self.plotter.setCurrentIndex(index)
        self.plotter.blockSignals(False)
        self._plotter_changed()
        self.refresh_styles()

    def refresh_styles(self) -> None:
        current = self.style_module.currentData() if hasattr(self, "style_module") else None
        current = str(current) if current else None
        self.style_module.blockSignals(True)
        self.style_module.clear()
        for entry in self.actions.style_module_entries():
            path = str(entry["path"]) if entry["path"] else None
            self.style_module.addItem(entry["name"], path)
        if current:
            index = self.style_module.findData(current)
            if index >= 0:
                self.style_module.setCurrentIndex(index)
        self.style_module.blockSignals(False)

    def current_style_module(self):
        path = self.style_module.currentData()
        return str(path) if path else None

    def _plotter_changed(self) -> None:
        plotter_id = self.plotter.currentData()
        self.plot_type.clear()
        if not plotter_id:
            return
        self.plot_type.addItems(self.actions.plot_type_entries(plotter_id))

    def _apply(self) -> None:
        self.actions.apply_backend_transform(
            self.input_column.currentData() or self.input_column.currentText(),
            self.function.currentData() or self.function.currentText(),
            1.0,
            self._float_value(self.offset.text(), 0.0),
            self._combo_value(self.output_column),
        )

    def _generate_plot(self) -> None:
        self.actions.generate_module_plot(self.plotter.currentData(), self.plot_type.currentText(), self.current_style_module())

    def _loader_entry(self) -> dict | str:
        return self.loader.currentData() or "auto"

    @staticmethod
    def _float_value(text: str, fallback: float) -> float:
        try:
            return float(text)
        except ValueError:
            return fallback

    @staticmethod
    def _column_label(index: int, column: str) -> str:
        """Show ``Column N`` for defaults and ``N: name`` for real names."""
        default_name = f"Column {index}"
        column = str(column or default_name)
        return default_name if column == default_name else f"{index}: {column}"

    @staticmethod
    def _combo_value(combo: QtWidgets.QComboBox) -> str:
        """Return typed output text when it differs from the selected item label."""
        line_edit = combo.lineEdit() if combo.isEditable() else None
        text = (line_edit.text() if line_edit is not None else combo.currentText()).strip()
        if combo.currentIndex() >= 0 and text == combo.itemText(combo.currentIndex()):
            return combo.currentData() or text
        return text

    @staticmethod
    def _panel():
        frame = QtWidgets.QFrame()
        frame.setObjectName("Panel")
        return frame

    @staticmethod
    def _title(text: str):
        label = QtWidgets.QLabel(text)
        label.setObjectName("SectionTitle")
        return label
