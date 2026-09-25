"""Three-section Simple mode controls."""

from __future__ import annotations

from physplot.qt_compat import QtCore, QtGui, QtWidgets


class AutoWidthComboBox(QtWidgets.QComboBox):
    """Compact combo box whose popup expands to fit long scientific labels.

    The closed box is sized from a short minimum length instead of its longest
    item, so Simple Mode fits laptop-width windows; the popup and tooltip still
    show the full label.
    """

    def __init__(self, parent=None, minimum_characters: int = 6):
        super().__init__(parent)
        # Must be set before the first size query: QComboBox caches its minimum size.
        self.setSizeAdjustPolicy(QtWidgets.QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.setMinimumContentsLength(minimum_characters)
        self.currentIndexChanged.connect(self._update_tooltip)

    def _update_tooltip(self, index: int) -> None:
        """Show the selected item's description, or its full label when it has none."""
        tooltip = self.itemData(index, QtCore.Qt.ItemDataRole.ToolTipRole) if index >= 0 else None
        self.setToolTip(tooltip or self.currentText())

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
    height_changed = QtCore.pyqtSignal()

    def __init__(self, actions, parent=None):
        super().__init__(parent)
        self.actions = actions
        self._columns: list[str] = []
        self._data_key = None
        self._plotter_entries: list[dict] = []
        self._needs_scroll = False
        self._fitted = 0

        self._content = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(self._content)
        layout.setContentsMargins(0, 6, 0, 6)
        layout.setSpacing(6)
        layout.addWidget(self._data_importer_panel(), 4)
        layout.addWidget(self._transform_panel(), 5)
        layout.addWidget(self._plotter_panel(), 12)

        # On screens narrower than the three panels, scroll sideways instead of
        # forcing the main window wider than the screen.
        self._scroll = QtWidgets.QScrollArea()
        self._scroll.setWidget(self._content)
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self._scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._scroll.viewport().setAutoFillBackground(False)
        self._content.setAutoFillBackground(False)
        outer = QtWidgets.QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self._scroll)
        self._content.installEventFilter(self)
        self.refresh_plotters()

    def sizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(self._content.sizeHint().width(), self.fitted_height())

    def minimumSizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(0, self.fitted_height())

    def fitted_height(self) -> int:
        """Height of the three panels, plus the scrollbar while one is shown."""
        height = self._content.sizeHint().height()
        if self._needs_scroll:
            height += self._scroll.horizontalScrollBar().sizeHint().height()
        return height

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._refit()

    def eventFilter(self, watched, event) -> bool:
        # Panels ask for a new layout once styled and when their contents change.
        if watched is self._content and event.type() == QtCore.QEvent.Type.LayoutRequest:
            QtCore.QTimer.singleShot(0, self._refit)
        return super().eventFilter(watched, event)

    def _refit(self) -> None:
        """Re-fit to the panels' real height and toggle room for the scrollbar."""
        self._needs_scroll = self._content.minimumSizeHint().width() > self.width()
        height = self.fitted_height()
        if height != self._fitted:
            self._fitted = height
            self.updateGeometry()
            self.height_changed.emit()

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
        layout.addWidget(import_folder_button, 2, 1, 1, 2)
        layout.addWidget(export_button, 3, 0)
        layout.setColumnStretch(1, 1)
        layout.setRowStretch(4, 1)
        return frame

    def _transform_panel(self):
        frame = self._panel()
        layout = QtWidgets.QGridLayout(frame)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setHorizontalSpacing(8)
        layout.setVerticalSpacing(7)
        layout.addWidget(self._title("2. Mathematical Transformation"), 0, 0, 1, 8)

        self.input_column = AutoWidthComboBox()
        self.function = AutoWidthComboBox()
        self._fill_function_menu()
        self.offset = QtWidgets.QLineEdit("0")
        self.offset.setMaximumWidth(72)
        self.output_column = AutoWidthComboBox()
        self.output_column.setEditable(True)
        self.output_column.setInsertPolicy(QtWidgets.QComboBox.InsertPolicy.NoInsert)
        self.output_column.setPlaceholderText("Output column")
        apply_button = QtWidgets.QPushButton("Apply")
        apply_button.clicked.connect(self._apply)

        layout.addWidget(QtWidgets.QLabel("Input:"), 1, 0)
        layout.addWidget(self.input_column, 1, 1)
        layout.addWidget(QtWidgets.QLabel("Function:"), 1, 2)
        layout.addWidget(self.function, 1, 3)
        layout.addWidget(QtWidgets.QLabel("+"), 1, 4)
        layout.addWidget(self.offset, 1, 5)
        layout.addWidget(QtWidgets.QLabel("Output:"), 2, 0)
        layout.addWidget(self.output_column, 2, 1, 1, 5)
        layout.addWidget(apply_button, 1, 6, 2, 1)
        layout.setColumnStretch(1, 2)
        layout.setColumnStretch(3, 2)
        layout.setColumnStretch(5, 1)
        layout.setRowStretch(3, 1)
        return frame

    def _plotter_panel(self):
        frame = self._panel()
        layout = QtWidgets.QGridLayout(frame)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setHorizontalSpacing(8)
        layout.setVerticalSpacing(7)
        layout.addWidget(self._title("3. Plotter Module"), 0, 0, 1, 4)

        self.plotter = AutoWidthComboBox()
        self.plotter.currentIndexChanged.connect(self._plotter_changed)
        self.plot_type = AutoWidthComboBox()
        self.style_module = AutoWidthComboBox()
        self.fit_enabled = QtWidgets.QCheckBox("LSQ fit")
        self.fit_expression = QtWidgets.QLineEdit("a*x + b")
        self.fit_expression.setPlaceholderText("f(x)")
        self.fit_parameters = QtWidgets.QLineEdit("a,b")
        self.fit_parameters.setPlaceholderText("parameters")
        self.fit_initial = QtWidgets.QLineEdit("1,0")
        self.fit_initial.setPlaceholderText("initial guesses")
        self.fit_label = QtWidgets.QLineEdit("")
        self.fit_label.setPlaceholderText("label")
        self.fit_style_preset = AutoWidthComboBox()
        self.fit_style_preset.currentIndexChanged.connect(self._fit_style_changed)
        self.fit_line_style = AutoWidthComboBox(minimum_characters=2)
        self.fit_line_style.addItems(["--", "-", "-.", ":"])
        self.fit_line_width = QtWidgets.QLineEdit("2")
        self.fit_line_width.setMaximumWidth(52)
        self.fit_line_width.setToolTip("Fit line width")
        self.fit_show_legend = QtWidgets.QCheckBox("Legend")
        self.fit_show_legend.setChecked(True)
        reload_styles_button = QtWidgets.QPushButton("Reload")
        reload_styles_button.setToolTip("Re-scan config/templates")
        reload_styles_button.clicked.connect(self.refresh_styles)
        reload_fit_styles_button = QtWidgets.QPushButton("Reload")
        reload_fit_styles_button.setToolTip("Re-scan config/figureforge_fit_styles")
        reload_fit_styles_button.clicked.connect(self.refresh_fit_styles)
        generate_button = QtWidgets.QPushButton("Generate Plot")
        generate_button.setProperty("primary", True)
        generate_button.clicked.connect(self._generate_plot)
        export_button = QtWidgets.QPushButton("Export Plot")
        export_button.clicked.connect(self.actions.export_module_plot)

        # Left column: what to plot.
        layout.addWidget(QtWidgets.QLabel("Plotter Module:"), 1, 0)
        layout.addWidget(self.plotter, 1, 1)
        layout.addWidget(QtWidgets.QLabel("Plot Type:"), 2, 0)
        layout.addWidget(self.plot_type, 2, 1)
        layout.addWidget(QtWidgets.QLabel("Template:"), 3, 0)
        style_layout = QtWidgets.QHBoxLayout()
        style_layout.setSpacing(6)
        style_layout.addWidget(self.style_module, 1)
        style_layout.addWidget(reload_styles_button)
        layout.addLayout(style_layout, 3, 1)

        # Right column: optional least-squares fit.
        fit_layout = QtWidgets.QHBoxLayout()
        fit_layout.setSpacing(6)
        fit_layout.addWidget(self.fit_enabled)
        fit_layout.addWidget(self.fit_expression, 1)
        layout.addWidget(QtWidgets.QLabel("Fit Function:"), 1, 2)
        layout.addLayout(fit_layout, 1, 3)
        fit_params_layout = QtWidgets.QHBoxLayout()
        fit_params_layout.setSpacing(6)
        fit_params_layout.addWidget(self.fit_parameters, 1)
        fit_params_layout.addWidget(self.fit_initial, 1)
        layout.addWidget(QtWidgets.QLabel("Params / Initial:"), 2, 2)
        layout.addLayout(fit_params_layout, 2, 3)
        fit_style_layout = QtWidgets.QHBoxLayout()
        fit_style_layout.setSpacing(6)
        fit_style_layout.addWidget(self.fit_style_preset, 1)
        fit_style_layout.addWidget(reload_fit_styles_button)
        layout.addWidget(QtWidgets.QLabel("Fit Style:"), 3, 2)
        layout.addLayout(fit_style_layout, 3, 3)
        # Fit line options share the button row so the panel stays narrow.
        fit_line_layout = QtWidgets.QHBoxLayout()
        fit_line_layout.setSpacing(6)
        fit_line_layout.addWidget(self.fit_label, 1)
        fit_line_layout.addWidget(self.fit_line_style)
        fit_line_layout.addWidget(self.fit_line_width)
        fit_line_layout.addWidget(self.fit_show_legend)
        layout.addWidget(QtWidgets.QLabel("Fit Line:"), 4, 2)
        layout.addLayout(fit_line_layout, 4, 3)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setSpacing(8)
        button_layout.addWidget(generate_button, 1)
        button_layout.addWidget(export_button, 1)
        layout.addLayout(button_layout, 4, 0, 1, 2)
        layout.setColumnStretch(1, 2)
        layout.setColumnStretch(3, 3)
        self.refresh_styles()
        self.refresh_fit_styles()
        return frame

    def refresh_plugins(self) -> None:
        """Re-scan editable config folders and repopulate every plugin menu."""
        loader_current = self.loader.currentText()
        self.loader.blockSignals(True)
        self.loader.clear()
        for entry in self.actions.backend_loader_entries():
            self.loader.addItem(entry["display_name"], entry)
            if not entry.get("enabled", True):
                item = self.loader.model().item(self.loader.count() - 1)
                item.setFlags(item.flags() & ~QtCore.Qt.ItemFlag.ItemIsEnabled)
                item.setForeground(QtGui.QColor("#94a3b8"))
        index = self.loader.findText(loader_current)
        if index >= 0:
            self.loader.setCurrentIndex(index)
        self.loader.blockSignals(False)

        function_current = self.function.currentText()
        self.function.blockSignals(True)
        self.function.clear()
        self._fill_function_menu()
        index = self.function.findText(function_current)
        if index >= 0:
            self.function.setCurrentIndex(index)
        self.function.blockSignals(False)

        self.refresh_plotters()
        self.refresh_fit_styles()

    def _fill_function_menu(self) -> None:
        for entry in self.actions.simple_function_entries():
            self.function.addItem(entry["display_name"], entry)
            if entry.get("tooltip"):
                self.function.setItemData(self.function.count() - 1, entry["tooltip"], QtCore.Qt.ItemDataRole.ToolTipRole)
        self.function._update_tooltip(self.function.currentIndex())

    def refresh_columns(self, columns: list[str]) -> None:
        """Refresh input/output column menus without duplicating default names.

        New data (not just added output columns) selects the Y-role column as
        the transformation input, since that is what is usually transformed.
        """
        self._columns = list(columns)
        current = self.input_column.currentData()
        state = getattr(self.actions, "state", None)
        dataset = getattr(getattr(state, "pp", None), "dataset", None)
        data_key = (dataset.name, str(dataset.source_path)) if dataset is not None else None
        new_data = data_key != self._data_key
        self._data_key = data_key
        roles = getattr(state, "roles", {}) or {}
        y_column = next((column for column in columns if roles.get(column) == "Y"), None)
        if new_data and y_column is not None:
            current = y_column
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
        return

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

    def refresh_fit_styles(self) -> None:
        current = self.fit_style_preset.currentData() if hasattr(self, "fit_style_preset") else None
        current = str(current) if current else None
        self.fit_style_preset.blockSignals(True)
        self.fit_style_preset.clear()
        for entry in self.actions.fit_style_entries():
            path = str(entry["path"]) if entry["path"] else None
            self.fit_style_preset.addItem(entry["name"], path)
            self.fit_style_preset.setItemData(self.fit_style_preset.count() - 1, entry.get("style"), QtCore.Qt.ItemDataRole.UserRole + 1)
        if current:
            index = self.fit_style_preset.findData(current)
            if index >= 0:
                self.fit_style_preset.setCurrentIndex(index)
        self.fit_style_preset.blockSignals(False)

    def current_style_module(self):
        path = self.style_module.currentData()
        return str(path) if path else None

    def _plotter_changed(self) -> None:
        plotter_id = self.plotter.currentData()
        self.plot_type.clear()
        if not plotter_id:
            return
        self.plot_type.addItems(self.actions.plot_type_entries(plotter_id))

    def _fit_style_changed(self) -> None:
        payload = self.fit_style_preset.currentData(QtCore.Qt.ItemDataRole.UserRole + 1)
        if not payload:
            return
        self.fit_label.setText(str(payload.get("label", "")))
        style_index = self.fit_line_style.findText(str(payload.get("line_style", "--")))
        if style_index >= 0:
            self.fit_line_style.setCurrentIndex(style_index)
        self.fit_line_width.setText(str(payload.get("line_width", 2.0)))
        self.fit_show_legend.setChecked(bool(payload.get("show_legend", True)))

    def _apply(self) -> None:
        self.actions.apply_backend_transform(
            self.input_column.currentData() or self.input_column.currentText(),
            self.function.currentData() or self.function.currentText(),
            1.0,
            self._float_value(self.offset.text(), 0.0),
            self._combo_value(self.output_column),
        )

    def _generate_plot(self) -> None:
        self.actions.generate_module_plot(
            self.plotter.currentData(),
            self.plot_type.currentText(),
            self.current_style_module(),
            fit_config=self._fit_config(),
        )

    def _fit_config(self) -> dict | None:
        if not self.fit_enabled.isChecked():
            return None
        return {
            "enabled": True,
            "expression": self.fit_expression.text().strip() or "a*x + b",
            "parameters": self.fit_parameters.text().strip() or "a,b",
            "initial": self.fit_initial.text().strip() or "1,0",
            "label": self.fit_label.text().strip(),
            "line_style": self.fit_line_style.currentText() or "--",
            "line_width": self._float_value(self.fit_line_width.text(), 2.0),
            "show_legend": self.fit_show_legend.isChecked(),
        }

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
