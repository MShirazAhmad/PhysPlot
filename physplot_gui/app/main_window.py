"""Modern three-mode PhysPlot main window."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from physplot.qt_compat import QtCore, QtGui, QtWidgets
from physplot.core.transformations import list_transforms
from physplot.loaders import list_loaders
from physplot.plotting_modules import PlotterRegistry
from physplot.workflow import load_workflow_source
from physplot.steps import (
    CalculateColumnStep,
    DeleteColumnsStep,
    DeleteRowsStep,
    LoadDataStep,
    PlotModuleStep,
    RenameColumnStep,
    SetCellValueStep,
    SetRoleStep,
    TransformColumnStep,
)

from physplot_gui.app.gui_state import GuiState
from physplot_gui.app.mode_manager import ModeManager
from physplot_gui.app.plugin_discovery import discover_fileloaders, discover_functions, discover_loader_plotters
from physplot_gui.style.theme import APP_STYLESHEET
from physplot_gui.widgets.central_table import CentralTable
from physplot_gui.widgets.mode_switcher import ModeSwitcher
from physplot_gui.widgets.status_bar import PhysPlotStatusBar


LOGO_WIDE = Path(__file__).resolve().parents[2] / "physplot" / "inc" / "PhysPlotWide1.png"
LOGO_ICON = Path(__file__).resolve().parents[2] / "physplot" / "inc" / "PhysPlot.png"


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.state = GuiState()
        self._active_loader_entry = None
        self._custom_plotters: dict[str, dict] = {}
        self.setWindowTitle("PhysPlot")
        self.resize(1500, 900)
        self.setStyleSheet(APP_STYLESHEET)
        if LOGO_ICON.exists():
            self.setWindowIcon(QtGui.QIcon(str(LOGO_ICON)))
        self._build_ui()
        self._bootstrap_blank_table()
        self._refresh_all()

    def _build_ui(self) -> None:
        self._build_menu_bar()
        root = QtWidgets.QWidget()
        self.setCentralWidget(root)
        layout = QtWidgets.QVBoxLayout(root)
        layout.setContentsMargins(12, 8, 12, 0)
        layout.setSpacing(7)
        self.mode_manager = ModeManager(self)
        self.mode_manager.mode_changed.connect(self._mode_changed)
        layout.addLayout(self._header())
        layout.addSpacing(10)
        self.central_table = CentralTable()
        self.central_table.role_changed.connect(self.set_column_role)
        self.central_table.column_renamed.connect(self.rename_column)
        self.central_table.cell_value_changed.connect(self.record_cell_edit)
        self.central_table.rows_deleted.connect(self.record_row_delete)
        self.central_table.columns_deleted.connect(self.record_column_delete)
        self.central_table.table_edited.connect(self.sync_table_to_backend)
        layout.addWidget(self.central_table, 1)
        layout.addWidget(self.mode_manager.stack, 0)
        self.status = PhysPlotStatusBar()
        layout.addWidget(self.status)

    def _build_menu_bar(self) -> None:
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("File")
        self._add_menu_action(file_menu, "Import Data...", lambda: self.import_data("auto"), "Ctrl+O")
        self._add_menu_action(file_menu, "Import Folder...", self.import_folder)
        self._add_menu_action(file_menu, "Export Data...", self.export_data, "Ctrl+E")

        protocol_menu = menu_bar.addMenu("Protocol")
        self._add_menu_action(protocol_menu, "Import Sequence.py...", self.open_workflow)
        self._add_menu_action(protocol_menu, "Export Sequence.py...", self.save_workflow, "Ctrl+S")
        self._add_menu_action(protocol_menu, "Apply This Sequence", self.apply_current_sequence, "Ctrl+R")
        self._add_menu_action(protocol_menu, "Copy Sequence Code", self.copy_workflow_script)
        self._add_menu_action(protocol_menu, "Clear Sequence", self.clear_recording)

        view_menu = menu_bar.addMenu("View")
        self._add_menu_action(view_menu, "Simple Mode", lambda: self.mode_manager.set_mode("Simple"), "Ctrl+1")
        self._add_menu_action(view_menu, "Advanced Mode", lambda: self.mode_manager.set_mode("Advanced"), "Ctrl+2")

        plot_menu = menu_bar.addMenu("Plot")
        self._add_menu_action(plot_menu, "Generate Plot", self.generate_plot, "Ctrl+G")
        self._add_menu_action(plot_menu, "Update Integrated Preview", self.generate_integrated_plot)

    def _add_menu_action(self, menu, text: str, callback, shortcut: str | None = None):
        action = QtWidgets.QAction(text, self)
        if shortcut:
            action.setShortcut(shortcut)
        action.triggered.connect(lambda checked=False: callback())
        menu.addAction(action)
        return action

    def _header(self):
        header = QtWidgets.QHBoxLayout()
        header.setContentsMargins(4, 0, 4, 0)
        header.setSpacing(0)
        header.addStretch(1)
        title_wrap = QtWidgets.QHBoxLayout()
        if LOGO_WIDE.exists():
            logo = QtWidgets.QLabel()
            pixmap = QtGui.QPixmap(str(LOGO_WIDE))
            logo.setPixmap(pixmap.scaledToHeight(72, QtCore.Qt.SmoothTransformation))
            title_wrap.addWidget(logo)
        else:
            labels = QtWidgets.QVBoxLayout()
            title = QtWidgets.QLabel("PhysPlot")
            title.setStyleSheet("font-size:30px;font-weight:800;color:#0f172a;")
            subtitle = QtWidgets.QLabel("Advanced Plotting Made Simple")
            subtitle.setStyleSheet("color:#0b65d8;font-weight:600;")
            labels.addWidget(title, alignment=QtCore.Qt.AlignCenter)
            labels.addWidget(subtitle, alignment=QtCore.Qt.AlignCenter)
            title_wrap.addLayout(labels)
        header.addLayout(title_wrap)
        header.addStretch(1)
        self.mode_switcher = ModeSwitcher()
        self.mode_switcher.mode_changed.connect(self.mode_manager.set_mode)
        header.addWidget(self.mode_switcher)
        return header

    def _bootstrap_blank_table(self) -> None:
        df = pd.DataFrame("", index=range(17), columns=[f"Column {i}" for i in range(1, 20)])
        self.state.load_dataframe(df, name="Untitled")
        self.central_table.set_dataframe(df, self.state.roles)

    def discover_function_entries(self) -> list[dict]:
        entries = discover_functions()
        if not entries:
            entries = [{"display_name": "x", "path": None, "module": None}]
        return entries

    def discover_loader_entries(self) -> list[dict]:
        entries = discover_fileloaders()
        if not entries:
            entries = [{"display_name": "Auto Loader", "path": None, "module": None, "loader_id": "auto"}]
        return entries

    def backend_loader_entries(self) -> list[dict]:
        entries = [
            {"display_name": loader.name, "loader_id": loader.loader_id, "enabled": loader.loader_id != "dataframe"}
            for loader in list_loaders()
        ]
        entries.extend(discover_fileloaders())
        return entries

    def backend_transform_entries(self) -> list[str]:
        return list_transforms()

    def simple_function_entries(self) -> list[dict]:
        entries = [{"display_name": "identity", "function_name": "identity"}]
        entries.extend({"display_name": name, "function_name": name} for name in list_transforms())
        entries.extend(discover_functions())
        seen = set()
        unique = []
        for entry in entries:
            key = entry.get("display_name")
            if key in seen:
                continue
            seen.add(key)
            unique.append(entry)
        return unique

    def plotter_entries(self) -> list[dict]:
        dataset = self.state.pp.dataset
        entries = [
            {"plotter_id": plotter.plotter_id, "name": plotter.name, "category": plotter.category}
            for plotter in PlotterRegistry.default().list_plotters(dataset)
        ]
        self._custom_plotters = {}
        if isinstance(self._active_loader_entry, dict) and self._active_loader_entry.get("module") is not None:
            for entry in discover_loader_plotters(self._active_loader_entry["module"]):
                plotter_id = entry.get("backend_plotter_id") or f"loader:{entry['plotter_id']}"
                if "callable" in entry:
                    plotter_id = f"loader:{entry['plotter_id']}"
                    self._custom_plotters[plotter_id] = entry
                if any(existing["plotter_id"] == plotter_id for existing in entries):
                    continue
                entries.append(
                    {
                        "plotter_id": plotter_id,
                        "name": entry.get("name", plotter_id),
                        "category": "Loader",
                    }
                )
        return entries

    def plot_type_entries(self, plotter_id: str) -> list[str]:
        if plotter_id in self._custom_plotters:
            return list(self._custom_plotters[plotter_id].get("plot_types") or ["publication_ready"])
        dataset = self.state.pp.dataset
        return PlotterRegistry.default().list_plot_types(plotter_id, dataset) if plotter_id else []

    def _mode_changed(self, mode: str) -> None:
        self.state.mode = mode
        self.mode_switcher.set_mode(mode)
        self.status.set_message("Ready")
        self._refresh_all()

    def _refresh_all(self) -> None:
        columns = self.central_table.column_names() if hasattr(self, "central_table") else list(self.state.dataframe.columns)
        self.mode_switcher.setVisible(True)
        self.central_table.set_roles(self.state.roles)
        self.mode_manager.refresh_columns(columns)
        self.mode_manager.refresh_pipeline(self.state.transformations)
        self.mode_manager.refresh_timeline(self.state.timeline)
        self.mode_manager.set_recording(bool(getattr(self.state.pp, "recording", False)))
        self.mode_manager.refresh_plots()
        self.status.update_state(self.state)

    def sync_table_to_backend(self) -> None:
        self.state.refresh_dataset_values(self.central_table.to_dataframe())
        self.status.update_state(self.state)

    def new_table(self, rows: int, columns: int, delete_old: bool) -> None:
        df = self.central_table.resize_table(rows, columns, delete_old)
        self.state.load_dataframe(df, name="Untitled")
        self._active_loader_entry = None
        self.state.current_file = None
        self.status.set_message("Ready")
        self._refresh_all()

    def import_data(self, loader: str | dict = "auto") -> None:
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Import Data",
            str(Path.cwd()),
            "Data Files (*.csv *.txt *.dat *.xls *.xlsx);;All Files (*)",
        )
        if not path:
            return
        try:
            loader_id = loader.get("loader_id") if isinstance(loader, dict) else loader
            loader_display = loader.get("display_name") if isinstance(loader, dict) else str(loader_id or "auto")
            if isinstance(loader, dict) and not loader.get("enabled", True):
                raise ValueError(f"{loader.get('display_name', 'Selected loader')} is not available yet.")
            if isinstance(loader, dict) and loader.get("module") is not None:
                loaded = loader["module"].load_data(path)
                if isinstance(loaded, pd.DataFrame):
                    table_data = loaded.to_numpy()
                    column_names = self._plugin_column_names(loader["module"], len(loaded.columns), list(loaded.columns))
                else:
                    table_data = np.asarray(loaded)
                    column_names = self._plugin_column_names(loader["module"], table_data.shape[1] if table_data.ndim > 1 else 1)
                if table_data.ndim == 1:
                    table_data = table_data.reshape(-1, 1)
                if table_data.ndim != 2:
                    raise ValueError("Loader must return a 2D table-like array.")
                df = pd.DataFrame(
                    table_data,
                    columns=column_names,
                )
                self.state.load_dataframe(df, name=Path(path).stem)
                self.state.pp.dataset.metadata["loader_plugin"] = str(loader.get("path", ""))
                self.state.pp.dataset.metadata["loader_name"] = loader.get("display_name")
                self._apply_loader_roles(loader, df.columns)
                self._active_loader_entry = loader
                workflow_step = LoadDataStep(
                    path=str(path),
                    loader="dataframe",
                    dataset_name=Path(path).stem,
                    loader_plugin=str(loader.get("path")) if loader.get("path") else None,
                )
            else:
                self.state.pp.load(path, loader=loader_id or "auto")
                self.state.pp.dataset.apply_suggested_roles()
                self._active_loader_entry = None
                workflow_step = LoadDataStep(path=str(path), loader=loader_id or "auto", dataset_name=Path(path).stem)
            self.state.current_file = Path(path)
            self.central_table.set_dataframe(self.state.dataframe, self.state.roles)
            workflow_steps = [workflow_step]
            role_step = self._role_step_from_current_roles()
            if role_step is not None:
                workflow_steps.append(role_step)
            setup_note = "column names"
            if role_step is not None:
                setup_note += " and role setup"
            self._append_sequence(
                "File Loader",
                f"{loader_display or 'Auto Loader'} ({setup_note})",
                Path(path).name,
                workflow_steps=workflow_steps,
            )
            self.status.set_message("Ready")
            self._refresh_all()
        except Exception as exc:
            self._error("Import failed", exc)

    def _apply_loader_roles(self, loader: dict, columns) -> None:
        role_map = {
            "x": "X",
            "x-axis": "X",
            "y": "Y",
            "y-axis": "Y",
            "x error": "X Error",
            "x-error": "X Error",
            "y error": "Y Error",
            "y-error": "Y Error",
            "group": "Group",
            "label": "Label",
        }
        roles = getattr(loader["module"], "DEFAULT_COLUMN_ROLES", [])
        for column, role in zip(columns, roles):
            normalized = role_map.get(str(role).strip().lower(), str(role).strip())
            if normalized:
                self.state.set_role(str(column), normalized)

    @staticmethod
    def _plugin_column_names(module, column_count: int, fallback_names=None) -> list[str]:
        raw_names = getattr(module, "COLUMN_NAMES", None) or getattr(module, "column_names", None)
        if callable(raw_names):
            raw_names = raw_names()
        names = [str(name).strip() for name in (raw_names or fallback_names or []) if str(name).strip()]
        if len(names) < column_count:
            names.extend(f"Column {index}" for index in range(len(names) + 1, column_count + 1))
        return names[:column_count]

    def import_folder(self) -> None:
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Import Folder", str(Path.cwd()))
        if folder:
            self.status.set_message(f"Folder selected: {Path(folder).name}")

    def export_data(self) -> None:
        self.sync_table_to_backend()
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Export Data", str(Path.cwd()))
        if not folder:
            return
        try:
            self.state.pp.export(folder)
            self.status.set_message("Exported")
        except Exception as exc:
            self._error("Export failed", exc)

    def generate_plot(self) -> None:
        self.sync_table_to_backend()
        try:
            self._open_legacy_plot_windows()
            self._record("Generate Plot", f"Create {self._current_plot_mode()} plot", "X vs Y")
            self.status.set_message("Plot generated")
            self._refresh_all()
        except Exception as exc:
            self._error("Plot failed", exc)

    def generate_integrated_plot(self) -> None:
        self.sync_table_to_backend()
        try:
            self.mode_manager.refresh_plots()
            self._record("Generate Plot", f"Create {self._current_plot_mode()} integrated plot", "Plot Preview")
            self.status.set_message("Plot preview updated")
            self.status.update_state(self.state)
        except Exception as exc:
            self._error("Plot failed", exc)

    def _open_legacy_plot_windows(self) -> None:
        from physplot import app as legacy_app

        self._prepare_legacy_plot_state(legacy_app)
        self._main_window = self
        if getattr(self, "plot_config_window", None) is None or not self.plot_config_window.isVisible():
            self.plot_config_window = QtWidgets.QMainWindow()
            self.plot_config_ui = legacy_app.Ui_ConfigWindow()
            self.plot_config_ui.setupUiConfigWindow(self.plot_config_window)
            self.plot_config_ui.owner = self
            self.plot_config_window.show()
        else:
            self.plot_config_window.raise_()
            self.plot_config_window.activateWindow()

        if getattr(self, "plot_window", None) is None or not self.plot_window.isVisible():
            self.plot_window = legacy_app.Plot_Window()
            self.plot_window.show()
        else:
            self.plot_window.refresh_plot()
            self.plot_window.raise_()
            self.plot_window.activateWindow()
        self._tile_legacy_plot_windows()

    def _tile_legacy_plot_windows(self) -> None:
        config_window = getattr(self, "plot_config_window", None)
        plot_window = getattr(self, "plot_window", None)
        if config_window is None or plot_window is None:
            return
        screen = self.screen() or QtWidgets.QApplication.primaryScreen()
        if screen is None:
            return
        available = screen.availableGeometry()
        gap = 12
        margin = 24
        top = max(available.top() + margin, self.y() + 40)
        height = min(max(620, config_window.height(), plot_window.height()), max(420, available.height() - top - margin))
        config_width = min(max(430, config_window.width()), max(380, int(available.width() * 0.32)))
        plot_width = min(max(860, plot_window.width()), max(620, available.width() - config_width - gap - margin * 2))
        total_width = config_width + gap + plot_width
        left = available.left() + max(margin, (available.width() - total_width) // 2)
        config_window.setGeometry(left, top, config_width, height)
        plot_window.setGeometry(left + config_width + gap, top, plot_width, height)
        config_window.raise_()
        plot_window.raise_()

    def _prepare_legacy_plot_state(self, legacy_app) -> None:
        df = self.central_table.to_dataframe()
        numeric = df.apply(pd.to_numeric, errors="coerce").fillna(0.0)
        legacy_app.OutPut_Table = numeric.to_numpy(dtype=float)
        legacy_app.tableLabels = np.zeros(max(100, len(numeric.columns)), dtype=int)
        role_map = {"X": 1, "X Error": 2, "Y": 3, "Y Error": 4}
        for column_index, column_name in enumerate(numeric.columns):
            role = self.state.roles.get(column_name, "Ignore")
            legacy_app.tableLabels[column_index] = role_map.get(role, 0)
        if int(np.count_nonzero(legacy_app.tableLabels == 1)) != 1 or int(np.count_nonzero(legacy_app.tableLabels == 3)) != 1:
            raise ValueError(
                "Select exactly one X column and one Y column from the column dropdowns before generating a plot."
            )

    def set_column_role(self, column: str, role: str) -> None:
        try:
            self.state.set_role(column, role)
            if role != "Ignore":
                key = self._role_key(role)
                self._append_sequence(
                    f"Set {role}",
                    f"Set column as {role}",
                    column,
                    workflow_step=SetRoleStep({key: column}),
                )
            self.central_table.set_roles(self.state.roles)
            self.status.update_state(self.state)
        except Exception as exc:
            self._error("Role update failed", exc)

    def rename_column(self, old_name: str, new_name: str) -> None:
        try:
            old_number = self._column_number_from_name(old_name)
            if self.state.pp.dataset is not None and old_name in self.state.pp.dataset.dataframe.columns:
                old_number = self.state.pp.dataset.get_column_number(old_name)
                self.state.pp.rename_column(old_name, new_name)
            self._append_sequence(
                "Rename Column",
                f"{old_name} -> {new_name}",
                new_name,
                workflow_step=RenameColumnStep(old_name, new_name, old_column_number=old_number),
            )
            self._refresh_all()
        except Exception as exc:
            self._error("Column rename failed", exc)

    def record_cell_edit(self, row_index: int, column: str, value: str, column_number: int) -> None:
        self._append_sequence(
            "Edit Cell",
            f"Row {row_index}, {column}",
            value,
            workflow_step=SetCellValueStep(row_index, column, value, column_number=column_number),
        )

    def record_row_delete(self, row_indices: list[int]) -> None:
        self._append_sequence(
            "Delete Rows",
            f"Rows {', '.join(str(row) for row in row_indices)}",
            "Table",
            workflow_step=DeleteRowsStep(row_indices),
        )

    def record_column_delete(self, columns: list[str], column_numbers: list[int]) -> None:
        self._append_sequence(
            "Delete Columns",
            ", ".join(columns),
            "Table",
            workflow_step=DeleteColumnsStep(columns, column_numbers=column_numbers),
        )

    def apply_simple_transform(self, input_column: str, output: str, function_name: str | dict, multiplier: float, offset: float):
        if not input_column:
            return
        output = output or input_column
        if isinstance(function_name, dict) and function_name.get("module") is not None:
            self._apply_function_plugin(input_column, output, function_name, multiplier, offset)
            return
        params = {}
        function_to_run = function_name
        if function_name == "identity":
            function_to_run = "multiply"
            params["factor"] = multiplier
        elif function_name == "multiply":
            params["factor"] = multiplier
        elif function_name in {"add", "subtract"}:
            params["value"] = offset
        elif function_name == "divide":
            params["divisor"] = multiplier or 1
        self._apply_transform({"input": input_column, "function": function_to_run, "params": params, "output": output})
        if function_name not in {"add", "subtract"} and offset:
            self._apply_transform({"input": output, "function": "add", "params": {"value": offset}, "output": output})

    def apply_backend_transform(
        self,
        input_column: str,
        function_entry: str | dict,
        multiplier: float,
        offset: float,
        output: str,
    ) -> None:
        if not input_column:
            return
        if isinstance(function_entry, dict):
            function_name = function_entry.get("function_name") or function_entry.get("display_name", "")
            function_to_run = function_entry if function_entry.get("module") is not None else function_name
        else:
            function_name = str(function_entry)
            function_to_run = function_name
        output = output or f"{input_column}_{function_name}"
        self.apply_simple_transform(input_column, output, function_to_run, multiplier, offset)

    def _apply_function_plugin(self, input_column: str, output_column: str, entry: dict, multiplier: float, offset: float) -> None:
        self.sync_table_to_backend()
        try:
            df = self.central_table.to_dataframe()
            if input_column not in df.columns:
                raise ValueError(f"Input column '{input_column}' does not exist.")
            if output_column not in df.columns:
                df[output_column] = ""
            values = pd.to_numeric(df[input_column], errors="coerce").fillna(0.0).to_numpy(dtype=float)
            transformed = np.asarray(entry["module"].transform(values), dtype=float) * multiplier + offset
            df[output_column] = transformed[: len(df.index)]
            self.state.refresh_dataset_values(df)
            self.central_table.set_dataframe(self.state.dataframe, self.state.roles)
            self._record("Transform", entry["display_name"], f"{input_column} -> {output_column}")
            self.status.set_message("Transformation applied")
            self._refresh_all()
        except Exception as exc:
            self._error("Transformation failed", exc)

    def add_pipeline_step(self, payload: dict) -> None:
        self.apply_pipeline_step(payload)

    def apply_pipeline_step(self, payload: dict) -> None:
        params = self._parse_params(payload.get("params", ""))
        step = {
            "input": payload.get("input", ""),
            "function": payload.get("function", "multiply"),
            "params": self._format_params(params),
            "output": payload.get("output") or f"{payload.get('input')}_{payload.get('function')}",
        }
        self._apply_transform({**step, "params": params})

    def _apply_transform(self, step: dict) -> None:
        self.sync_table_to_backend()
        try:
            self.state.pp.transform(step["input"], step["function"], output=step["output"], **step.get("params", {}))
            workflow_index = len(self.state.pp.workflow) - 1 if self.state.pp.workflow else None
            display_step = {
                "input": step["input"],
                "function": step["function"],
                "params": self._format_params(step.get("params", {})),
                "output": step["output"],
            }
            self.state.transformations.append(display_step)
            self.central_table.set_dataframe(self.state.dataframe, self.state.roles)
            self._append_sequence(
                "Transform",
                step["function"],
                f"{step['input']} -> {step['output']}",
                workflow_index=workflow_index,
            )
            self.status.set_message("Transformation applied")
            self._refresh_all()
        except Exception as exc:
            self._error("Transformation failed", exc)

    def generate_module_plot(self, plotter_id: str, plot_type: str) -> None:
        if not plotter_id:
            return
        self.sync_table_to_backend()
        try:
            if plotter_id == "basic":
                self.state.pp.plot_with_module(plotter_id, plot_type)
                workflow_index = len(self.state.pp.workflow) - 1 if self.state.pp.workflow else None
                self._open_legacy_plot_windows()
            elif plotter_id in self._custom_plotters:
                figure = self._run_custom_plotter(plotter_id, plot_type)
                workflow_index = None
                self._show_module_figure(figure, f"{plotter_id}: {plot_type}")
            else:
                figure = self.state.pp.plot_with_module(plotter_id, plot_type)
                workflow_index = len(self.state.pp.workflow) - 1 if self.state.pp.workflow else None
                self._show_module_figure(figure, f"{plotter_id}: {plot_type}")
            self._append_sequence(
                "Generate Plot",
                f"Create {plotter_id} {plot_type}",
                "Plotter Module",
                workflow_index=workflow_index,
            )
            self.status.set_message("Plot generated")
            self._refresh_all()
        except Exception as exc:
            self._error("Plot failed", exc)

    def _run_custom_plotter(self, plotter_id: str, plot_type: str):
        entry = self._custom_plotters[plotter_id]
        function = entry["callable"]
        dataset = self.state.pp.get_active_dataset()
        config = dict(entry.get("config") or {})
        for call in (
            lambda: function(dataset, plot_type=plot_type, config=config),
            lambda: function(dataset, plot_type),
            lambda: function(dataset),
            lambda: function(dataset.dataframe, roles=dataset.column_roles, metadata=dataset.metadata, plot_type=plot_type),
            lambda: function(dataset.dataframe),
        ):
            try:
                figure = call()
                break
            except TypeError:
                continue
        else:
            figure = function(dataset)
        self.state.pp.last_figure = figure
        return figure

    def export_module_plot(self) -> None:
        figure = getattr(self.state.pp, "last_figure", None)
        if figure is None:
            self._error("Export plot failed", RuntimeError("Generate a plot before exporting."))
            return
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Export Plot",
            str(Path.cwd() / "physplot_plot.png"),
            "PNG Files (*.png);;PDF Files (*.pdf);;SVG Files (*.svg);;All Files (*)",
        )
        if not path:
            return
        try:
            figure.savefig(path, dpi=300)
            self.status.set_message("Plot exported")
        except Exception as exc:
            self._error("Export plot failed", exc)

    def _show_module_figure(self, figure, title: str) -> None:
        from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
        from matplotlib.backends.backend_qtagg import NavigationToolbar2QT

        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle(f"PhysPlot - {title}")
        dialog.resize(820, 620)
        layout = QtWidgets.QVBoxLayout(dialog)
        canvas = FigureCanvas(figure)
        toolbar = NavigationToolbar2QT(canvas, dialog)
        layout.addWidget(toolbar)
        layout.addWidget(canvas)
        canvas.draw()
        self._module_plot_dialogs = getattr(self, "_module_plot_dialogs", [])
        self._module_plot_dialogs.append(dialog)
        dialog.show()

    def delete_pipeline_step(self, index: int) -> None:
        if 0 <= index < len(self.state.transformations):
            self.state.transformations.pop(index)
            self._refresh_all()

    def clear_pipeline(self) -> None:
        self.state.transformations.clear()
        self._refresh_all()

    def import_pipeline(self) -> None:
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Import Pipeline", str(Path.cwd()), "JSON Files (*.json)")
        if not path:
            return
        try:
            self.state.transformations = json.loads(Path(path).read_text(encoding="utf-8"))
            self._refresh_all()
        except Exception as exc:
            self._error("Import pipeline failed", exc)

    def export_pipeline(self) -> None:
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Export Pipeline", str(Path.cwd() / "pipeline.json"), "JSON Files (*.json)")
        if path:
            Path(path).write_text(json.dumps(self.state.transformations, indent=2), encoding="utf-8")
            self.status.set_message("Pipeline exported")

    def fit_model(self) -> None:
        try:
            self.sync_table_to_backend()
            self.state.pp.fit("linear")
            self.status.set_message("Fit complete")
            self._refresh_all()
        except Exception as exc:
            self._error("Fit failed", exc)

    def show_fit_results(self) -> None:
        result = self.state.pp.fit_result
        text = "No fit result yet."
        if result:
            text = "\n".join(f"{key}: {value}" for key, value in result.items())
        QtWidgets.QMessageBox.information(self, "Fit Results", text)

    def start_recording(self) -> None:
        self.state.pp.start_recording()
        self._append_sequence("Start Tracking", "Sequence tracking is always on", "Advanced")
        self._refresh_all()

    def stop_recording(self) -> None:
        self._append_sequence("Tracking", "Sequence tracking stays on", "Advanced")
        self.state.pp.stop_recording()
        self._refresh_all()

    def save_workflow(self) -> None:
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save Sequence.py",
            str(Path.cwd() / "sequence.py"),
            "Python Files (*.py)",
        )
        if not path:
            return
        try:
            self.state.pp.save_workflow(path)
            self.state.workflow_file = Path(path)
            self.status.set_message("Sequence saved")
            self._refresh_all()
        except Exception as exc:
            self._error("Save workflow failed", exc)

    def open_workflow(self) -> None:
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Load Sequence.py", str(Path.cwd()), "Python Files (*.py)")
        if path:
            try:
                steps = self.state.pp.load_workflow(path)
                self.state.pp.workflow = list(steps)
                self.state.timeline = self._sequence_rows_from_steps(steps)
                self.state.workflow_file = Path(path)
                self.status.set_message("Sequence loaded")
            except Exception as exc:
                self._error("Load sequence failed", exc)
            self._refresh_all()

    def run_workflow(self) -> None:
        self.apply_current_sequence()

    def apply_current_sequence(self) -> None:
        if not self.state.pp.workflow:
            self._error("Apply sequence failed", RuntimeError("Build or import a protocol sequence first."))
            return
        try:
            self.sync_table_to_backend()
            steps = list(self.state.pp.workflow)
            self.state.pp.run_workflow(steps, allow_column_number_fallback=True)
            self.central_table.set_dataframe(self.state.dataframe, self.state.roles)
            self.status.set_message("Sequence complete")
            self._refresh_all()
        except Exception as exc:
            self._error("Apply sequence failed", exc)

    def apply_sequence_code(self, source: str) -> None:
        steps = load_workflow_source(source, name="physplot_sequence_editor")
        self.state.pp.workflow = list(steps)
        self.state.timeline = self._sequence_rows_from_steps(steps)
        self.status.set_message("Sequence code applied")
        self._refresh_all()

    def workflow_manager(self) -> None:
        QtWidgets.QMessageBox.information(self, "Sequence Manager", "Sequence actions are available in the Advanced panel.")

    def copy_workflow_script(self) -> None:
        QtWidgets.QApplication.clipboard().setText(self.sequence_code_text())
        self.status.set_message("Sequence script copied")

    def sequence_code_text(self) -> str:
        return self.state.pp.workflow_script()

    def clear_recording(self) -> None:
        self.state.timeline.clear()
        self.state.pp.workflow.clear()
        self._refresh_all()

    def delete_timeline_step(self, index: int) -> None:
        if 0 <= index < len(self.state.timeline):
            row = self.state.timeline.pop(index)
            workflow_indices = row.get("workflow_indices")
            if workflow_indices is None:
                workflow_index = row.get("workflow_index")
                workflow_indices = [workflow_index] if isinstance(workflow_index, int) else []
            removed = sorted({i for i in workflow_indices if isinstance(i, int)}, reverse=True)
            for workflow_index in removed:
                if 0 <= workflow_index < len(self.state.pp.workflow):
                    self.state.pp.workflow.pop(workflow_index)
            if removed:
                self._reindex_sequence_rows_after_delete(set(removed))
            self._refresh_all()

    def browse_input_folder(self, field: QtWidgets.QLineEdit) -> None:
        self._browse_folder(field, "Input Folder")

    def browse_output_folder(self, field: QtWidgets.QLineEdit) -> None:
        self._browse_folder(field, "Output Folder")

    def browse_workflow_file(self, field: QtWidgets.QLineEdit) -> None:
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Workflow File", str(Path.cwd()), "Python Files (*.py)")
        if path:
            field.setText(path)

    def run_bulk_workflow(self, payload: dict) -> None:
        try:
            workflow_file = payload.get("workflow_file")
            workflow = workflow_file
            if not workflow:
                if not self.state.pp.workflow:
                    raise RuntimeError("Build or import a protocol sequence before running bulk automation.")
                workflow = [step for step in self.state.pp.workflow if not isinstance(step, LoadDataStep)]
            outputs = self.state.pp.run_bulk(
                workflow,
                payload["input_folder"],
                payload["output_folder"],
                allow_column_number_fallback=True,
            )
            self.status.set_message(f"Bulk complete: {len(outputs)} outputs")
        except Exception as exc:
            self._error("Bulk run failed", exc)

    def _browse_folder(self, field: QtWidgets.QLineEdit, title: str) -> None:
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, title, str(Path.cwd()))
        if folder:
            field.setText(folder)

    def _append_sequence(
        self,
        action: str,
        details: str,
        target: str,
        workflow_step=None,
        workflow_steps: list | None = None,
        workflow_index=None,
    ) -> None:
        workflow_indices = []
        if workflow_steps:
            for step in workflow_steps:
                self.state.pp.workflow.append(step)
                workflow_indices.append(len(self.state.pp.workflow) - 1)
        if workflow_step is not None:
            self.state.pp.workflow.append(workflow_step)
            workflow_index = len(self.state.pp.workflow) - 1
            workflow_indices.append(workflow_index)
        elif isinstance(workflow_index, int):
            workflow_indices.append(workflow_index)
        code = self._sequence_code_for_indices(workflow_indices)
        self.state.timeline.append(
            {
                "action": action,
                "details": details,
                "target": target,
                "workflow_index": workflow_index,
                "workflow_indices": workflow_indices or None,
                "code": code,
            }
        )

    def _record(self, action: str, details: str, target: str) -> None:
        self._append_sequence(action, details, target)

    def _append_role_sequence_steps(self) -> None:
        role_step = self._role_step_from_current_roles()
        if role_step is not None:
            self._append_sequence("Column Roles", "Apply selected column roles", "Role setup", workflow_step=role_step)

    def _role_step_from_current_roles(self):
        roles = {}
        for column, role in self.state.roles.items():
            if role == "Ignore":
                continue
            roles[self._role_key(role)] = column
        return SetRoleStep(roles) if roles else None

    def _reindex_sequence_rows_after_delete(self, removed: set[int]) -> None:
        def adjust(index):
            if not isinstance(index, int) or index in removed:
                return None
            return index - sum(1 for removed_index in removed if removed_index < index)

        for row in self.state.timeline:
            if isinstance(row.get("workflow_index"), int):
                row["workflow_index"] = adjust(row["workflow_index"])
            if row.get("workflow_indices"):
                row["workflow_indices"] = [
                    adjusted for adjusted in (adjust(index) for index in row["workflow_indices"]) if adjusted is not None
                ]
            row["code"] = self._sequence_code_for_indices(row.get("workflow_indices") or [row.get("workflow_index")])

    @staticmethod
    def _role_key(role: str) -> str:
        return {
            "X": "x",
            "Y": "y",
            "X Error": "xerr",
            "Y Error": "yerr",
            "Group": "group",
            "Label": "label",
            "Batch Key": "batch_key",
            "Fit Weight": "fit_weight",
        }.get(role, role)

    @staticmethod
    def _sequence_rows_from_steps(steps: list) -> list[dict]:
        rows = []
        index = 0
        while index < len(steps):
            step = steps[index]
            if isinstance(step, LoadDataStep):
                workflow_indices = [index]
                has_role_setup = index + 1 < len(steps) and isinstance(steps[index + 1], SetRoleStep)
                if has_role_setup:
                    workflow_indices.append(index + 1)
                loader_name = "Personal file loader" if step.loader_plugin else f"{step.loader} loader"
                setup_note = "column names and role setup" if has_role_setup else "column names"
                row = {
                    "action": "File Loader",
                    "details": f"{loader_name} ({setup_note})",
                    "target": str(step.path or ""),
                    "workflow_index": index,
                    "workflow_indices": workflow_indices,
                }
                row["code"] = MainWindow._sequence_code_for_steps([steps[i] for i in workflow_indices])
                rows.append(row)
                index += 2 if has_role_setup else 1
                continue
            elif isinstance(step, SetRoleStep):
                row = {"action": "Set Roles", "details": ", ".join(step.roles), "target": repr(step.roles)}
            elif isinstance(step, TransformColumnStep):
                row = {
                    "action": "Transform",
                    "details": step.function_name,
                    "target": f"{step.input_column} -> {step.output}",
                }
            elif isinstance(step, CalculateColumnStep):
                row = {"action": "Calculate", "details": step.formula_original, "target": step.output}
            elif isinstance(step, PlotModuleStep):
                row = {"action": "Generate Plot", "details": step.plotter_id, "target": step.plot_type or ""}
            elif isinstance(step, RenameColumnStep):
                row = {
                    "action": "Rename Column",
                    "details": f"{step.old_column} -> {step.new_column}",
                    "target": step.new_column,
                }
            elif isinstance(step, SetCellValueStep):
                row = {
                    "action": "Edit Cell",
                    "details": f"Row {step.row_index}, {step.column}",
                    "target": str(step.value),
                }
            elif isinstance(step, DeleteRowsStep):
                row = {"action": "Delete Rows", "details": ", ".join(map(str, step.row_indices)), "target": "Table"}
            elif isinstance(step, DeleteColumnsStep):
                row = {"action": "Delete Columns", "details": ", ".join(step.columns), "target": "Table"}
            else:
                row = {"action": step.__class__.__name__, "details": "", "target": ""}
            row["workflow_index"] = index
            row["workflow_indices"] = [index]
            row["code"] = MainWindow._sequence_code_for_steps([step])
            rows.append(row)
            index += 1
        return rows

    def _sequence_code_for_indices(self, indices) -> str:
        indices = [index for index in (indices or []) if isinstance(index, int)]
        steps = [self.state.pp.workflow[index] for index in indices if 0 <= index < len(self.state.pp.workflow)]
        return self._sequence_code_for_steps(steps)

    @staticmethod
    def _sequence_code_for_steps(steps: list) -> str:
        lines = [MainWindow._step_code_line(step) for step in steps]
        return "; ".join(line for line in lines if line)

    @staticmethod
    def _step_code_line(step) -> str:
        if isinstance(step, LoadDataStep):
            return (
                "LoadDataStep("
                f"path={step.path!r}, loader={step.loader!r}, dataset_name={step.dataset_name!r}, "
                f"loader_plugin={step.loader_plugin!r}).apply(pp)"
            )
        if isinstance(step, SetRoleStep):
            return f"pp.set_roles({MainWindow._kwargs_code(step.roles)})"
        if isinstance(step, TransformColumnStep):
            params = dict(step.params)
            params_code = MainWindow._kwargs_code(params)
            suffix = f", {params_code}" if params_code else ""
            return f"pp.transform({step.input_column!r}, {step.function_name!r}, output={step.output!r}{suffix})"
        if isinstance(step, CalculateColumnStep):
            return f"pp.calculate({step.formula_original!r}, output={step.output!r})"
        if isinstance(step, PlotModuleStep):
            config_code = MainWindow._kwargs_code(step.config)
            suffix = f", {config_code}" if config_code else ""
            return f"pp.plot_with_module({step.plotter_id!r}, {step.plot_type!r}{suffix})"
        if isinstance(step, RenameColumnStep):
            return f"pp.rename_column({step.old_column!r}, {step.new_column!r})"
        if isinstance(step, SetCellValueStep):
            return f"pp.set_cell_value({step.row_index!r}, {step.column!r}, {step.value!r})"
        if isinstance(step, DeleteRowsStep):
            return f"pp.delete_rows({step.row_indices!r})"
        if isinstance(step, DeleteColumnsStep):
            return f"pp.delete_columns({step.columns!r})"
        return f"# {step.__class__.__name__}"

    @staticmethod
    def _kwargs_code(values: dict) -> str:
        return ", ".join(f"{key}={value!r}" for key, value in values.items())

    @staticmethod
    def _column_number_from_name(name: str) -> int | None:
        text = str(name or "").strip().lower()
        if text.startswith("column "):
            try:
                return int(text.split(None, 1)[1])
            except (IndexError, ValueError):
                return None
        return None

    def _current_plot_mode(self) -> str:
        panel = self.mode_manager.panels.get(self.state.mode)
        if hasattr(panel, "current_plot_mode"):
            return panel.current_plot_mode()
        preview = getattr(panel, "plot_preview", None)
        return preview.current_plot_mode() if preview else "Single"

    @staticmethod
    def _parse_params(text: str) -> dict:
        params = {}
        if not text:
            return params
        for part in text.split(","):
            if "=" not in part:
                continue
            key, value = part.split("=", 1)
            key = key.strip()
            value = value.strip()
            try:
                params[key] = float(value)
            except ValueError:
                params[key] = value
        return params

    @staticmethod
    def _format_params(params: dict) -> str:
        if not params:
            return "-"
        return ", ".join(f"{key}={value:g}" if isinstance(value, float) else f"{key}={value}" for key, value in params.items())

    def _error(self, title: str, exc: Exception) -> None:
        self.status.set_message(title)
        QtWidgets.QMessageBox.warning(self, title, str(exc))
