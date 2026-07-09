"""PhysPlot main application module.

This module implements the complete PhysPlot desktop GUI application:
table-based data entry/import, column transformations, plotting with
matplotlib, and optional curve fitting.

Input data structure:
    The main table stores numeric data in a QTableWidget. Row 0 contains
    column-role combo boxes; rows 1..N contain numeric data. Plot generation
    reads that table into ``OutPut_Table`` as a two-dimensional NumPy array.
    File loaders return the same rectangular 2D array structure.

Return type:
    GUI classes do not return data directly. Plot windows render matplotlib
    figures, transformation functions write values back into table columns,
    and loaders/configuration helpers update global GUI state used by the
    active plot.

Optional main/runtime behavior:
    This legacy module is imported by the modern GUI when Basic Plotter needs
    the historical plot-formatting and curve-fitting windows.

Original metadata:
- Original file name: PhysPlot.py
- Authors: Muhammad Shiraz Ahmad and Sabieh Anwar
- Date created: 8/20/2019
- Date last modified: 5/15/2026
- Script Version: 2.0.0
- Python Version: 3.7.3
"""
import webbrowser
import ast
import importlib.util
from pathlib import Path

MODULE_ID = "physplot.app"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-05-30-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"

import numpy as np
from physplot.user_paths import plugin_search_dirs
from physplot.qt_compat import Qt, QtCore, QtGui, QtWidgets
QDialog = QtWidgets.QDialog
QVBoxLayout = QtWidgets.QVBoxLayout
QWidget = QtWidgets.QWidget
QMessageBox = QtWidgets.QMessageBox
QFileDialog = QtWidgets.QFileDialog
QTableWidgetItem = QtWidgets.QTableWidgetItem
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from scipy.optimize import curve_fit

plt_LableData = np.zeros((0, 4))
CURVE_FIT_ROWS = []
ACTIVE_CURVE_FIT_DEFINITIONS = []
APP_LOGO_PATH = Path(__file__).resolve().parent / "inc" / "PhysPlotWide1.png"
APP_ICON_PATH = Path(__file__).resolve().parent / "inc" / "PhysPlot.png"

try:
    from .constants import (
        AXIS_ROLE_OPTIONS,
        COLORS,
        GRID_COLOR_OPTIONS,
        GRID_STYLE_OPTIONS,
        LINESTYLES,
        LINE_COLOR_OPTIONS,
        LINE_STYLE_OPTIONS,
        MARKERS,
        MARKER_COLOR_OPTIONS,
        MARKER_STYLE_OPTIONS,
        PLOT_LABEL_DEFAULTS,
        SCALE_X_OPTIONS,
        CURVE_FIT_LABEL_MODES,
    )
    from .utils import fit_label, table_item_float
except ImportError:
    from constants import (
        AXIS_ROLE_OPTIONS,
        COLORS,
        GRID_COLOR_OPTIONS,
        GRID_STYLE_OPTIONS,
        LINESTYLES,
        LINE_COLOR_OPTIONS,
        LINE_STYLE_OPTIONS,
        MARKERS,
        MARKER_COLOR_OPTIONS,
        MARKER_STYLE_OPTIONS,
        PLOT_LABEL_DEFAULTS,
        SCALE_X_OPTIONS,
        CURVE_FIT_LABEL_MODES,
    )
    from utils import fit_label, table_item_float


def _set_combo_items(combo, values):
    """_set_combo_items(combo, values) -> object

    Set combo items.

    Parameters:
        See function signature.

    Returns:
        object: Result described by the method name and GUI side effects.
    """
    combo.clear()
    combo.addItems(list(values))


def _role_index(role_name):
    """_role_index(role_name) -> object

    Role index.

    Parameters:
        See function signature.

    Returns:
        object: Result described by the method name and GUI side effects.
    """
    try:
        return AXIS_ROLE_OPTIONS.index(role_name)
    except ValueError:
        return 0


def _loader_display_name(loader_path):
    """_loader_display_name(loader_path) -> object

    Loader display name.

    Parameters:
        See function signature.

    Returns:
        object: Result described by the method name and GUI side effects.
    """
    try:
        module_ast = ast.parse(loader_path.read_text(encoding="utf-8", errors="ignore"))
        for node in module_ast.body:
            if (
                isinstance(node, ast.Assign)
                and any(isinstance(target, ast.Name) and target.id == "title" for target in node.targets)
                and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str)
            ):
                return node.value.value
    except Exception:
        pass
    return loader_path.stem.replace("_", " ").title()


def _discover_loader_files():
    """_discover_loader_files() -> object

    Discover loader files.

    Parameters:
        None

    Returns:
        object: Result described by the method name and GUI side effects.
    """
    return _discover_plugin_files(plugin_search_dirs("fileloader"), default_first=True)


def _load_loader_module(loader_path):
    """_load_loader_module(loader_path) -> object

    Load loader module.

    Parameters:
        See function signature.

    Returns:
        object: Result described by the method name and GUI side effects.
    """
    module_name = f"fileloader.{loader_path.stem}"
    spec = importlib.util.spec_from_file_location(module_name, loader_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load file loader from {loader_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not isinstance(getattr(module, "title", None), str) or not module.title.strip():
        raise AttributeError(f"{loader_path.name} must define a non-empty title string")
    if not hasattr(module, "load_data"):
        raise AttributeError(f"{loader_path.name} must define load_data(file_path)")
    return module


def _discover_function_files():
    """_discover_function_files() -> object

    Discover function files.

    Parameters:
        None

    Returns:
        object: Result described by the method name and GUI side effects.
    """
    return _discover_plugin_files(plugin_search_dirs("functions"))


def _load_function_module(function_path):
    """_load_function_module(function_path) -> object

    Load function module.

    Parameters:
        See function signature.

    Returns:
        object: Result described by the method name and GUI side effects.
    """
    module_name = f"functions.{function_path.stem}"
    spec = importlib.util.spec_from_file_location(module_name, function_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load function from {function_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "transform"):
        raise AttributeError(f"{function_path.name} must define transform(values)")
    return module


def _discover_curve_fit_files():
    """_discover_curve_fit_files() -> object

    Discover curve fit files.

    Parameters:
        None

    Returns:
        object: Result described by the method name and GUI side effects.
    """
    return _discover_plugin_files(plugin_search_dirs("curvefitting"))


def _discover_plugin_files(folders, default_first=False):
    paths_by_name = {}
    for folder in folders:
        if not folder.exists():
            continue
        for path in sorted(folder.glob("*.py")):
            if path.name.startswith(".") or path.name == "__init__.py":
                continue
            paths_by_name.setdefault(path.name, path)
    if default_first:
        return sorted(paths_by_name.values(), key=lambda path: (path.stem != "default_loader", path.stem))
    return sorted(paths_by_name.values(), key=lambda path: path.stem)


def _load_curve_fit_module(curve_fit_path):
    """_load_curve_fit_module(curve_fit_path) -> object

    Load curve fit module.

    Parameters:
        See function signature.

    Returns:
        object: Result described by the method name and GUI side effects.
    """
    module_name = f"curvefitting.{curve_fit_path.stem}"
    spec = importlib.util.spec_from_file_location(module_name, curve_fit_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load curve fitting function from {curve_fit_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for attribute in ("DISPLAY_NAME", "DEFAULT_LABEL", "KIND"):
        if not hasattr(module, attribute):
            raise AttributeError(f"{curve_fit_path.name} must define {attribute}")
    if module.KIND == "poly" and not hasattr(module, "DEGREE"):
        raise AttributeError(f"{curve_fit_path.name} must define DEGREE")
    if module.KIND == "callable" and not hasattr(module, "function"):
        raise AttributeError(f"{curve_fit_path.name} must define function(x, ...)")
    if module.KIND not in {"poly", "callable"}:
        raise ValueError(f"{curve_fit_path.name} KIND must be 'poly' or 'callable'")
    return module


def _curve_fit_definition(curve_fit_path, index):
    """_curve_fit_definition(curve_fit_path, index) -> object

    Curve fit definition.

    Parameters:
        See function signature.

    Returns:
        object: Result described by the method name and GUI side effects.
    """
    module = _load_curve_fit_module(curve_fit_path)
    definition = {
        "display_name": module.DISPLAY_NAME,
        "default_label": module.DEFAULT_LABEL,
        "kind": module.KIND,
        "label_modes": getattr(module, "LABEL_MODES", ["Off", "Equation", "Custom"]),
        "check_box_name": f"checkBox__crvft_{index}",
        "off_radio_name": "radioButton_off_crvft_1" if index == 1 else f"radioButton__off_crvft_{index}",
        "equation_radio_name": f"radioButton_Equation_crvft_{index}",
        "path": curve_fit_path,
    }
    if module.KIND == "poly":
        definition["degree"] = module.DEGREE
    else:
        definition["function"] = module.function
        definition["initial_guess"] = getattr(module, "INITIAL_GUESS", None)
    return definition


def _load_curve_fit_definitions():
    """_load_curve_fit_definitions() -> object

    Load curve fit definitions.

    Parameters:
        None

    Returns:
        object: Result described by the method name and GUI side effects.
    """
    return [
        _curve_fit_definition(path, index)
        for index, path in enumerate(_discover_curve_fit_files(), start=1)
    ]


CURVE_FIT_DEFINITIONS = _load_curve_fit_definitions()


class Ui_ConfigWindow(object):
    """Plot configuration window for styling and curve-fit display options."""

    def setupUiConfigWindow(self, ConfigWindow):
        """setupUiConfigWindow(self, ConfigWindow) -> None

        Configure generated Qt user-interface widgets and signals.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        ConfigWindow.setObjectName("ConfigWindow")
        ConfigWindow.resize(440, 555)
        ConfigWindow.setMinimumSize(QtCore.QSize(413, 550))
        self.centralwidget = QtWidgets.QWidget(ConfigWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout_12 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_12.addItem(spacerItem)
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout_12.addWidget(self.pushButton)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_12.addItem(spacerItem1)
        self.gridLayout.addLayout(self.horizontalLayout_12, 1, 0, 1, 1)
        self.tabWidget1 = QtWidgets.QTabWidget(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.tabWidget1.setFont(font)
        self.tabWidget1.setObjectName("tabWidget1")
        self.tab_1 = QtWidgets.QWidget()
        self.tab_1.setObjectName("tab_1")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.tab_1)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.scrollArea = QtWidgets.QScrollArea(self.tab_1)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 377, 562))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.groupBox = QtWidgets.QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_Grid_Style = QtWidgets.QLabel(self.groupBox)
        self.label_Grid_Style.setObjectName("label_Grid_Style")
        self.verticalLayout_2.addWidget(self.label_Grid_Style)
        self.label_Grid_Width = QtWidgets.QLabel(self.groupBox)
        self.label_Grid_Width.setObjectName("label_Grid_Width")
        self.verticalLayout_2.addWidget(self.label_Grid_Width)
        self.label_Grid_Color = QtWidgets.QLabel(self.groupBox)
        self.label_Grid_Color.setObjectName("label_Grid_Color")
        self.verticalLayout_2.addWidget(self.label_Grid_Color)
        self.gridLayout_6.addLayout(self.verticalLayout_2, 0, 0, 1, 1)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.comboBox_Grid_Style = QtWidgets.QComboBox(self.groupBox)
        self.comboBox_Grid_Style.setObjectName("comboBox_Grid_Style")
        self.comboBox_Grid_Style.addItem("")
        self.comboBox_Grid_Style.addItem("")
        self.comboBox_Grid_Style.addItem("")
        self.comboBox_Grid_Style.addItem("")
        self.comboBox_Grid_Style.addItem("")
        validator = QtGui.QDoubleValidator()
        self.verticalLayout.addWidget(self.comboBox_Grid_Style)
        self.lineEdit_Grid_Width = QtWidgets.QLineEdit(self.groupBox)
        self.lineEdit_Grid_Width.setValidator(validator)
        self.lineEdit_Grid_Width.setInputMethodHints(QtCore.Qt.ImhDigitsOnly | QtCore.Qt.ImhFormattedNumbersOnly)
        self.lineEdit_Grid_Width.setObjectName("lineEdit_Grid_Width")
        self.verticalLayout.addWidget(self.lineEdit_Grid_Width)
        self.comboBox_Grid_Color = QtWidgets.QComboBox(self.groupBox)
        self.comboBox_Grid_Color.setObjectName("comboBox_Grid_Color")
        self.comboBox_Grid_Color.addItem("")
        self.comboBox_Grid_Color.addItem("")
        self.comboBox_Grid_Color.addItem("")
        self.comboBox_Grid_Color.addItem("")
        self.comboBox_Grid_Color.addItem("")
        self.comboBox_Grid_Color.addItem("")
        self.comboBox_Grid_Color.addItem("")
        self.verticalLayout.addWidget(self.comboBox_Grid_Color)
        self.gridLayout_6.addLayout(self.verticalLayout, 0, 1, 1, 1)
        self.gridLayout_4.addWidget(self.groupBox, 0, 0, 1, 1)
        self.groupBox_2 = QtWidgets.QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_7 = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.label_Marker_Style = QtWidgets.QLabel(self.groupBox_2)
        self.label_Marker_Style.setObjectName("label_Marker_Style")
        self.verticalLayout_4.addWidget(self.label_Marker_Style)
        self.label_Marker_Size = QtWidgets.QLabel(self.groupBox_2)
        self.label_Marker_Size.setObjectName("label_Marker_Size")
        self.verticalLayout_4.addWidget(self.label_Marker_Size)
        self.label_Marker_Color = QtWidgets.QLabel(self.groupBox_2)
        self.label_Marker_Color.setObjectName("label_Marker_Color")
        self.verticalLayout_4.addWidget(self.label_Marker_Color)
        self.gridLayout_7.addLayout(self.verticalLayout_4, 0, 0, 1, 1)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.comboBox_Marker_Style = QtWidgets.QComboBox(self.groupBox_2)
        self.comboBox_Marker_Style.setObjectName("comboBox_Marker_Style")
        self.comboBox_Marker_Style.addItem("")
        self.comboBox_Marker_Style.addItem("")
        self.comboBox_Marker_Style.addItem("")
        self.comboBox_Marker_Style.addItem("")
        self.comboBox_Marker_Style.addItem("")
        self.comboBox_Marker_Style.addItem("")
        self.comboBox_Marker_Style.addItem("")
        self.comboBox_Marker_Style.addItem("")
        self.comboBox_Marker_Style.addItem("")
        self.comboBox_Marker_Style.addItem("")
        self.comboBox_Marker_Style.addItem("")
        self.comboBox_Marker_Style.addItem("")
        self.comboBox_Marker_Style.addItem("")
        self.comboBox_Marker_Style.addItem("")
        self.comboBox_Marker_Style.addItem("")
        self.comboBox_Marker_Style.addItem("")
        self.comboBox_Marker_Style.addItem("")
        self.comboBox_Marker_Style.addItem("")
        self.comboBox_Marker_Style.addItem("")
        self.comboBox_Marker_Style.addItem("")
        self.comboBox_Marker_Style.addItem("")
        self.comboBox_Marker_Style.addItem("")
        self.comboBox_Marker_Style.addItem("")
        self.comboBox_Marker_Style.addItem("")
        self.verticalLayout_3.addWidget(self.comboBox_Marker_Style)
        self.lineEdit_Marker_Size = QtWidgets.QLineEdit(self.groupBox_2)
        self.lineEdit_Marker_Size.setValidator(validator)
        self.lineEdit_Marker_Size.setInputMethodHints(QtCore.Qt.ImhDigitsOnly | QtCore.Qt.ImhFormattedNumbersOnly)
        self.lineEdit_Marker_Size.setObjectName("lineEdit_Marker_Size")
        self.verticalLayout_3.addWidget(self.lineEdit_Marker_Size)
        self.comboBox_Marker_Color = QtWidgets.QComboBox(self.groupBox_2)
        self.comboBox_Marker_Color.setObjectName("comboBox_Marker_Color")
        self.comboBox_Marker_Color.addItem("")
        self.comboBox_Marker_Color.addItem("")
        self.comboBox_Marker_Color.addItem("")
        self.comboBox_Marker_Color.addItem("")
        self.comboBox_Marker_Color.addItem("")
        self.comboBox_Marker_Color.addItem("")
        self.comboBox_Marker_Color.addItem("")
        self.comboBox_Marker_Color.addItem("")
        self.verticalLayout_3.addWidget(self.comboBox_Marker_Color)
        self.gridLayout_7.addLayout(self.verticalLayout_3, 0, 1, 1, 1)
        self.gridLayout_4.addWidget(self.groupBox_2, 1, 0, 1, 1)
        self.groupBox_3 = QtWidgets.QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_3.setObjectName("groupBox_3")
        self.gridLayout_8 = QtWidgets.QGridLayout(self.groupBox_3)
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.label_Line_Style = QtWidgets.QLabel(self.groupBox_3)
        self.label_Line_Style.setObjectName("label_Line_Style")
        self.verticalLayout_5.addWidget(self.label_Line_Style)
        self.label_Line_Width = QtWidgets.QLabel(self.groupBox_3)
        self.label_Line_Width.setObjectName("label_Line_Width")
        self.verticalLayout_5.addWidget(self.label_Line_Width)
        self.label_Line_Color = QtWidgets.QLabel(self.groupBox_3)
        self.label_Line_Color.setObjectName("label_Line_Color")
        self.verticalLayout_5.addWidget(self.label_Line_Color)
        self.gridLayout_8.addLayout(self.verticalLayout_5, 0, 0, 1, 1)
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.comboBox_Line_Style = QtWidgets.QComboBox(self.groupBox_3)
        self.comboBox_Line_Style.setObjectName("comboBox_Line_Style")
        self.comboBox_Line_Style.addItem("")
        self.comboBox_Line_Style.addItem("")
        self.comboBox_Line_Style.addItem("")
        self.comboBox_Line_Style.addItem("")
        self.comboBox_Line_Style.addItem("")
        self.verticalLayout_6.addWidget(self.comboBox_Line_Style)
        self.lineEdit_Line_Width = QtWidgets.QLineEdit(self.groupBox_3)
        self.lineEdit_Line_Width.setValidator(validator)
        self.lineEdit_Line_Width.setInputMethodHints(QtCore.Qt.ImhDigitsOnly | QtCore.Qt.ImhFormattedNumbersOnly)
        self.lineEdit_Line_Width.setObjectName("lineEdit_Line_Width")
        self.verticalLayout_6.addWidget(self.lineEdit_Line_Width)
        self.comboBox_Line_Color = QtWidgets.QComboBox(self.groupBox_3)
        self.comboBox_Line_Color.setObjectName("comboBox_Line_Color")
        self.comboBox_Line_Color.addItem("")
        self.comboBox_Line_Color.addItem("")
        self.comboBox_Line_Color.addItem("")
        self.comboBox_Line_Color.addItem("")
        self.comboBox_Line_Color.addItem("")
        self.comboBox_Line_Color.addItem("")
        self.comboBox_Line_Color.addItem("")
        self.comboBox_Line_Color.addItem("")
        self.verticalLayout_6.addWidget(self.comboBox_Line_Color)
        self.gridLayout_8.addLayout(self.verticalLayout_6, 0, 1, 1, 1)
        self.gridLayout_4.addWidget(self.groupBox_3, 2, 0, 1, 1)
        self.groupBox_6 = QtWidgets.QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_6.setObjectName("groupBox_6")
        self.gridLayout_9 = QtWidgets.QGridLayout(self.groupBox_6)
        self.gridLayout_9.setObjectName("gridLayout_9")
        self.verticalLayout_9 = QtWidgets.QVBoxLayout()
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.label_title = QtWidgets.QLabel(self.groupBox_6)
        self.label_title.setObjectName("label_title")
        self.verticalLayout_9.addWidget(self.label_title)
        self.label_xLable = QtWidgets.QLabel(self.groupBox_6)
        self.label_xLable.setObjectName("label_xLable")
        self.verticalLayout_9.addWidget(self.label_xLable)
        self.label_yLable = QtWidgets.QLabel(self.groupBox_6)
        self.label_yLable.setObjectName("label_yLable")
        self.verticalLayout_9.addWidget(self.label_yLable)
        self.label_Legend = QtWidgets.QLabel(self.groupBox_6)
        self.label_Legend.setObjectName("label_Legend")
        self.verticalLayout_9.addWidget(self.label_Legend)
        self.gridLayout_9.addLayout(self.verticalLayout_9, 0, 0, 1, 1)
        self.verticalLayout_10 = QtWidgets.QVBoxLayout()
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.lineEdit_PlotLabel = QtWidgets.QLineEdit(self.groupBox_6)
        self.lineEdit_PlotLabel.setObjectName("lineEdit_PlotLabel")
        self.verticalLayout_10.addWidget(self.lineEdit_PlotLabel)
        self.lineEdit_PlotxLabel = QtWidgets.QLineEdit(self.groupBox_6)
        self.lineEdit_PlotxLabel.setObjectName("lineEdit_PlotxLabel")
        self.verticalLayout_10.addWidget(self.lineEdit_PlotxLabel)
        self.lineEdit_PlotyLabel = QtWidgets.QLineEdit(self.groupBox_6)
        self.lineEdit_PlotyLabel.setObjectName("lineEdit_PlotyLabel")
        self.verticalLayout_10.addWidget(self.lineEdit_PlotyLabel)
        self.lineEdit_PlotLegend = QtWidgets.QLineEdit(self.groupBox_6)
        self.lineEdit_PlotLegend.setObjectName("lineEdit_PlotLegend")
        self.verticalLayout_10.addWidget(self.lineEdit_PlotLegend)
        self.gridLayout_9.addLayout(self.verticalLayout_10, 0, 1, 1, 1)
        self.gridLayout_4.addWidget(self.groupBox_6, 3, 0, 1, 1)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout_3.addWidget(self.scrollArea, 0, 0, 1, 1)
        self.tabWidget1.addTab(self.tab_1, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.tab_2)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.gridLayout_5.setContentsMargins(36, 32, 36, 32)
        self.gridLayout_5.setVerticalSpacing(14)
        self.label_curve_fit_label_mode = QtWidgets.QLabel(self.tab_2)
        self.label_curve_fit_label_mode.setObjectName("label_curve_fit_label_mode")
        self.gridLayout_5.addWidget(self.label_curve_fit_label_mode, 0, 0, 1, 1)
        self.comboBox_curve_fit_label_mode = QtWidgets.QComboBox(self.tab_2)
        self.comboBox_curve_fit_label_mode.setMinimumWidth(220)
        self.comboBox_curve_fit_label_mode.setObjectName("comboBox_curve_fit_label_mode")
        self.gridLayout_5.addWidget(self.comboBox_curve_fit_label_mode, 1, 0, 1, 1)
        self.label_curve_fit_custom_label = QtWidgets.QLabel(self.tab_2)
        self.label_curve_fit_custom_label.setObjectName("label_curve_fit_custom_label")
        self.gridLayout_5.addWidget(self.label_curve_fit_custom_label, 2, 0, 1, 1)
        self.lineEdit_curve_fit_label = QtWidgets.QLineEdit(self.tab_2)
        self.lineEdit_curve_fit_label.setMinimumWidth(240)
        self.lineEdit_curve_fit_label.setObjectName("lineEdit_curve_fit_label")
        self.gridLayout_5.addWidget(self.lineEdit_curve_fit_label, 3, 0, 1, 1)
        self.label_curve_fit_type = QtWidgets.QLabel(self.tab_2)
        self.label_curve_fit_type.setObjectName("label_curve_fit_type")
        self.gridLayout_5.addWidget(self.label_curve_fit_type, 4, 0, 1, 1)
        self.listWidget_curve_fit_type = QtWidgets.QListWidget(self.tab_2)
        self.listWidget_curve_fit_type.setMinimumWidth(220)
        self.listWidget_curve_fit_type.setObjectName("listWidget_curve_fit_type")
        self.gridLayout_5.addWidget(self.listWidget_curve_fit_type, 5, 0, 1, 1)
        self.gridLayout_5.setColumnStretch(0, 1)
        self.gridLayout_5.setRowStretch(0, 0)
        self.gridLayout_5.setRowStretch(1, 0)
        self.gridLayout_5.setRowStretch(2, 0)
        self.gridLayout_5.setRowStretch(3, 0)
        self.gridLayout_5.setRowStretch(4, 0)
        self.gridLayout_5.setRowStretch(5, 1)
        self.tabWidget1.addTab(self.tab_2, "")
        self.gridLayout.addWidget(self.tabWidget1, 0, 0, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        ConfigWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(ConfigWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 440, 21))
        self.menubar.setObjectName("menubar")
        ConfigWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(ConfigWindow)
        self.statusbar.setObjectName("statusbar")
        ConfigWindow.setStatusBar(self.statusbar)

        self.retranslateUi(ConfigWindow)
        self.tabWidget1.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(ConfigWindow)

    def retranslateUi(self, ConfigWindow):
        """retranslateUi(self, ConfigWindow) -> None

        Configure generated Qt user-interface widgets and signals.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        _translate = QtCore.QCoreApplication.translate
        ConfigWindow.setWindowTitle(_translate("ConfigWindow", "Configuration"))
        ConfigWindow.setWindowIcon(QtGui.QIcon(str(APP_ICON_PATH)))
        self._apply_configured_texts()
        self.sourceScript()

    def _curve_fit_radio_name(self, index, mode):
        """_curve_fit_radio_name(self, index, mode) -> None

        Curve fit radio name.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        if mode == "off" and index == 1:
            return f"radioButton_off_crvft_{index}"
        if mode == "off":
            return f"radioButton__off_crvft_{index}"
        return f"radioButton_{mode}_crvft_{index}"

    def _apply_configured_texts(self):
        """_apply_configured_texts(self) -> None

        Apply configured texts.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        _set_combo_items(self.comboBox_Grid_Style, GRID_STYLE_OPTIONS)
        _set_combo_items(self.comboBox_Grid_Color, GRID_COLOR_OPTIONS)
        _set_combo_items(self.comboBox_Marker_Style, MARKER_STYLE_OPTIONS)
        _set_combo_items(self.comboBox_Marker_Color, MARKER_COLOR_OPTIONS)
        _set_combo_items(self.comboBox_Line_Style, LINE_STYLE_OPTIONS)
        _set_combo_items(self.comboBox_Line_Color, LINE_COLOR_OPTIONS)

        self.pushButton.setText("Apply")
        self.groupBox.setTitle("Grid Line")
        self.label_Grid_Style.setText("Style:")
        self.label_Grid_Width.setText("Width:")
        self.label_Grid_Color.setText("Color:")
        self.lineEdit_Grid_Width.setText("0.3")
        self.groupBox_2.setTitle("Marker")
        self.label_Marker_Style.setText("Style:")
        self.label_Marker_Size.setText("Size:")
        self.label_Marker_Color.setText("Color:")
        self.lineEdit_Marker_Size.setText("1")
        self.groupBox_3.setTitle("Plot Line")
        self.label_Line_Style.setText("Style")
        self.label_Line_Width.setText("Width")
        self.label_Line_Color.setText("Color")
        self.lineEdit_Line_Width.setText("1")
        self.groupBox_6.setTitle("Labels")
        self.label_title.setText("Title:")
        self.label_xLable.setText("xLabel:")
        self.label_yLable.setText("yLabel:")
        self.label_Legend.setText("Legend:")
        self.lineEdit_PlotLabel.setText(PLOT_LABEL_DEFAULTS["title"])
        self.lineEdit_PlotxLabel.setText(PLOT_LABEL_DEFAULTS["x_label"])
        self.lineEdit_PlotyLabel.setText(PLOT_LABEL_DEFAULTS["y_label"])
        self.lineEdit_PlotLegend.setText(PLOT_LABEL_DEFAULTS["legend"])
        self.tabWidget1.setTabText(self.tabWidget1.indexOf(self.tab_1), "Plot Formating")
        self.label_curve_fit_type.setText("Curve Fit Type")
        self.label_curve_fit_label_mode.setText("Label Mode")
        self.label_curve_fit_custom_label.setText("Custom Label")
        _set_combo_items(
            self.listWidget_curve_fit_type,
            [fit_definition["display_name"] for fit_definition in CURVE_FIT_DEFINITIONS],
        )
        if CURVE_FIT_DEFINITIONS:
            self.lineEdit_curve_fit_label.setText(CURVE_FIT_DEFINITIONS[0]["default_label"])
            self._set_curve_fit_label_modes(0)
            self.listWidget_curve_fit_type.clearSelection()
            self.listWidget_curve_fit_type.setCurrentRow(-1)

        self.tabWidget1.setTabText(self.tabWidget1.indexOf(self.tab_2), "Curve Fitting")

    def _set_curve_fit_label_modes(self, index):
        """_set_curve_fit_label_modes(self, index) -> None

        Set curve fit label modes.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        if not CURVE_FIT_DEFINITIONS:
            return
        current = self.comboBox_curve_fit_label_mode.currentText()
        modes = CURVE_FIT_DEFINITIONS[index]["label_modes"]
        self.comboBox_curve_fit_label_mode.blockSignals(True)
        _set_combo_items(self.comboBox_curve_fit_label_mode, modes)
        selected_index = self.comboBox_curve_fit_label_mode.findText(current)
        self.comboBox_curve_fit_label_mode.setCurrentIndex(max(selected_index, 0))
        self.comboBox_curve_fit_label_mode.blockSignals(False)

    def _curve_fit_type_changed(self, index):
        """_curve_fit_type_changed(self, index) -> None

        Curve fit type changed.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        if index < 0 or index >= len(CURVE_FIT_DEFINITIONS):
            return
        self.lineEdit_curve_fit_label.setText(CURVE_FIT_DEFINITIONS[index]["default_label"])
        self._set_curve_fit_label_modes(index)
        self._sync_curve_fit_selection()

    def _sync_curve_fit_selection(self):
        """_sync_curve_fit_selection(self) -> None

        Sync curve fit selection.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        global plt_LableData
        global CURVE_FIT_ROWS
        global ACTIVE_CURVE_FIT_DEFINITIONS
        index = self.listWidget_curve_fit_type.currentRow()
        if not CURVE_FIT_DEFINITIONS or index < 0:
            CURVE_FIT_ROWS = []
            ACTIVE_CURVE_FIT_DEFINITIONS = []
            plt_LableData = np.zeros((0, 4))
            mode = self.comboBox_curve_fit_label_mode.currentText().lower()
            is_custom_label = mode in {"custom", "label"}
            self.label_curve_fit_custom_label.setVisible(is_custom_label)
            self.lineEdit_curve_fit_label.setVisible(is_custom_label)
            self.lineEdit_curve_fit_label.setEnabled(is_custom_label)
            return
        ACTIVE_CURVE_FIT_DEFINITIONS = [CURVE_FIT_DEFINITIONS[index]]
        CURVE_FIT_ROWS = [{"line_edit": self.lineEdit_curve_fit_label}]
        plt_LableData = np.zeros((1, 4))
        plt_LableData[0, 0] = True
        mode = self.comboBox_curve_fit_label_mode.currentText().lower()
        is_custom_label = mode in {"custom", "label"}
        self.label_curve_fit_custom_label.setVisible(is_custom_label)
        self.lineEdit_curve_fit_label.setVisible(is_custom_label)
        self.lineEdit_curve_fit_label.setEnabled(is_custom_label)
        if mode == "equation":
            plt_LableData[0, 2] = True
        elif mode in {"custom", "label"}:
            plt_LableData[0, 3] = True
        else:
            plt_LableData[0, 1] = True

    def _setup_file_loader_menu(self):
        """_setup_file_loader_menu(self) -> None

        Setup file loader menu.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        self.file_loader_actions = []
        self.active_loader_path = None
        self.active_loader_module = None
        self._loader_module_cache = {}
        self.menuFileLoader.clear()
        loader_group = QtWidgets.QActionGroup(self.menuFileLoader)
        loader_group.setExclusive(True)
        loader_files = _discover_loader_files()
        if not loader_files:
            empty_action = QtWidgets.QAction("No loaders found", self.menuFileLoader)
            empty_action.setEnabled(False)
            self.menuFileLoader.addAction(empty_action)
            return

        for loader_path in loader_files:
            action = QtWidgets.QAction(_loader_display_name(loader_path), self.menuFileLoader)
            action.setCheckable(True)
            action.setData(str(loader_path))
            action.triggered.connect(lambda _checked=False, path=loader_path: self._set_active_loader(path))
            loader_group.addAction(action)
            self.menuFileLoader.addAction(action)
            self.file_loader_actions.append(action)

        default_loader = next((path for path in loader_files if path.stem == "default_loader"), loader_files[0])
        self._set_active_loader(default_loader)

    def _set_active_loader(self, loader_path):
        """_set_active_loader(self, loader_path) -> None

        Set active loader.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        loader_path = Path(loader_path)
        loader_key = str(loader_path)
        cached_module = self._loader_module_cache.get(loader_key)
        if cached_module is None:
            cached_module = _load_loader_module(loader_path)
            self._loader_module_cache[loader_key] = cached_module
        self.active_loader_path = loader_path
        self.active_loader_module = cached_module
        for action in getattr(self, "file_loader_actions", []):
            action.setChecked(action.data() == loader_key)

    def _load_table_data(self, file_path):
        """_load_table_data(self, file_path) -> None

        Load table data.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        if self.active_loader_module is None:
            raise RuntimeError("No file loader is selected.")
        table_data = self.active_loader_module.load_data(file_path)
        table_data = np.asarray(table_data)
        if table_data.ndim == 1:
            table_data = np.atleast_2d(table_data).T
        if table_data.ndim != 2:
            raise ValueError("Loader must return a 2D table-like array.")
        return table_data

    def sourceScript(self):
        """sourceScript(self) -> None

        Configure generated Qt user-interface widgets and signals.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """

        # delayCmd.delay(self)

        # Tab 1
        #  self.comboBox_Grid_Style.activated[str].connect(self.onActivated_Grid_Style)
        self.lineEdit_Grid_Width.setText("0.3")
        #  self.comboBox_Grid_Color.activated[str].connect(self.onActivated_Grid_Color)

        #   self.comboBox_Marker_Style.activated[str].connect(self.onActivated_Marker_Style)
        self.lineEdit_Marker_Size.setText("2")
        #  self.comboBox_Marker_Color.activated[str].connect(self.onActivated_Marker_Color)

        #  self.comboBox_Line_Style.activated[str].connect(self.onActivated_Line_Style)
        self.lineEdit_Line_Width.setText("1")
        #  self.comboBox_Line_Color.activated[str].connect(self.onActivated_Line_Style)
        self.pushButton.clicked.connect(self.definePlotParameters)
        import numpy as np
        self.listWidget_curve_fit_type.currentRowChanged.connect(self._curve_fit_type_changed)
        self.comboBox_curve_fit_label_mode.currentIndexChanged.connect(lambda _index: self._sync_curve_fit_selection())
        self.lineEdit_curve_fit_label.textChanged.connect(lambda _text: self._sync_curve_fit_selection())
        self._sync_curve_fit_selection()
        global Grid_Style
        global Grid_Width
        global Grid_Color
        global Marker_Style
        global Marker_Size
        global Marker_Color
        global Line_Style
        global Line_Width
        global Line_Color
        global Label_PlotLabel
        global Label_PlotxLabel
        global Label_PlotyLabel
        global Label_PlotLegend

        Label_PlotLabel = PLOT_LABEL_DEFAULTS["title"]
        Label_PlotxLabel = PLOT_LABEL_DEFAULTS["x_label"]
        Label_PlotyLabel = PLOT_LABEL_DEFAULTS["y_label"]
        Label_PlotLegend = PLOT_LABEL_DEFAULTS["legend"]
        Grid_Style = GRID_STYLE_OPTIONS[0]
        Grid_Width = "0.3"
        Grid_Color = GRID_COLOR_OPTIONS[0]
        Marker_Style = MARKER_STYLE_OPTIONS[1]
        Marker_Size = "1"
        Marker_Color = MARKER_COLOR_OPTIONS[2]
        Line_Style = LINE_STYLE_OPTIONS[0]
        Line_Width = "1"
        Line_Color = LINE_COLOR_OPTIONS[0]

        """
        Label_lineEdit_crvft_1= str(self.lineEdit_crvft_1.text())
        Label_lineEdit_crvft_2= str(self.lineEdit_crvft_2.text())
        Label_lineEdit_crvft_3= str(self.lineEdit_crvft_3.text())
        Label_lineEdit_crvft_4= str(self.lineEdit_crvft_4.text())
        Label_lineEdit_crvft_5 = str(self.lineEdit_crvft_5.text())
        Label_lineEdit_crvft_6 = str(self.lineEdit_crvft_6.text())
        Label_lineEdit_crvft_7 = str(self.lineEdit_crvft_7.text())
        Label_lineEdit_crvft_8 = str(self.lineEdit_crvft_8.text())
        Label_lineEdit_crvft_9 = str(self.lineEdit_crvft_9.text())
        Label_lineEdit_crvft_10 = str(self.lineEdit_crvft_10.text())
        Label_lineEdit_crvft_11 = str(self.lineEdit_crvft_11.text())
        """

    def readFitType(self):
        """readFitType(self) -> None

        Update curve-fit enable flags from the configuration checkboxes.

        Parameters:
            self (Ui_ConfigWindow): Active configuration window instance.

        Returns:
            None
        """
        if self.checkBox__crvft_1.isChecked() == True:
            plt_LableData[0, 0] = True
        else:
            plt_LableData[0, 0] = False
        if self.checkBox__crvft_2.isChecked() == True:
            plt_LableData[1, 0] = True
        else:
            plt_LableData[1, 0] = False
        if self.checkBox__crvft_3.isChecked() == True:
            plt_LableData[2, 0] = True
        else:
            plt_LableData[2, 0] = False
        if self.checkBox__crvft_4.isChecked() == True:
            plt_LableData[3, 0] = True
        else:
            plt_LableData[3, 0] = False
        if self.checkBox__crvft_5.isChecked() == True:
            plt_LableData[4, 0] = True
        else:
            plt_LableData[4, 0] = False
        if self.checkBox__crvft_6.isChecked() == True:
            plt_LableData[5, 0] = True
        else:
            plt_LableData[5, 0] = False
        if self.checkBox__crvft_7.isChecked() == True:
            plt_LableData[6, 0] = True
        else:
            plt_LableData[6, 0] = False
        if self.checkBox__crvft_8.isChecked() == True:
            plt_LableData[7, 0] = True
        else:
            plt_LableData[7, 0] = False
        if self.checkBox__crvft_9.isChecked() == True:
            plt_LableData[8, 0] = True
        else:
            plt_LableData[8, 0] = False
        if self.checkBox__crvft_10.isChecked() == True:
            plt_LableData[9, 0] = True
        else:
            plt_LableData[9, 0] = False
        if self.checkBox__crvft_11.isChecked() == True:
            plt_LableData[10, 0] = True
        else:
            plt_LableData[10, 0] = False

    def onClicked_radioButton_off_crvft_1(self):
        """onClicked_radioButton_off_crvft_1(self) -> None

        Handle a legacy curve-fit radio-button click.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        self.radioButton_off_crvft_1.setChecked(True)
        self.radioButton_Equation_crvft_1.setChecked(False)
        self.radioButton_Label_crvft_1.setChecked(False)
        plt_LableData[0, 1] = True
        plt_LableData[0, 2] = False
        plt_LableData[0, 3] = False

    def onClicked_radioButton_Equation_crvft_1(self):
        """onClicked_radioButton_Equation_crvft_1(self) -> None

        Handle a legacy curve-fit radio-button click.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        self.radioButton_Equation_crvft_1.setChecked(True)
        self.radioButton_off_crvft_1.setChecked(False)
        self.radioButton_Label_crvft_1.setChecked(False)
        plt_LableData[0, 1] = False
        plt_LableData[0, 2] = True
        plt_LableData[0, 3] = False

    def onClicked_radioButton_Label_crvft_1(self):
        """onClicked_radioButton_Label_crvft_1(self) -> None

        Handle a legacy curve-fit radio-button click.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        self.radioButton_Label_crvft_1.setChecked(True)
        self.radioButton_off_crvft_1.setChecked(False)
        self.radioButton_Equation_crvft_1.setChecked(False)
        plt_LableData[0, 1] = False
        plt_LableData[0, 2] = False
        plt_LableData[0, 3] = True

    def onClicked_radioButton_off_crvft_2(self):
        """onClicked_radioButton_off_crvft_2(self) -> None

        Handle a legacy curve-fit radio-button click.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        self.radioButton__off_crvft_2.setChecked(True)
        self.radioButton_Equation_crvft_2.setChecked(False)
        self.radioButton_Label_crvft_2.setChecked(False)
        plt_LableData[1, 1] = True
        plt_LableData[1, 2] = False
        plt_LableData[1, 3] = False

    def onClicked_radioButton_Equation_crvft_2(self):
        """onClicked_radioButton_Equation_crvft_2(self) -> None

        Handle a legacy curve-fit radio-button click.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        self.radioButton_Equation_crvft_2.setChecked(True)
        self.radioButton__off_crvft_2.setChecked(False)
        self.radioButton_Label_crvft_2.setChecked(False)
        plt_LableData[1, 1] = False
        plt_LableData[1, 2] = True
        plt_LableData[1, 3] = False

    def onClicked_radioButton_Label_crvft_2(self):
        """onClicked_radioButton_Label_crvft_2(self) -> None

        Handle a legacy curve-fit radio-button click.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        self.radioButton_Label_crvft_2.setChecked(True)
        self.radioButton__off_crvft_2.setChecked(False)
        self.radioButton_Equation_crvft_2.setChecked(False)
        plt_LableData[1, 1] = False
        plt_LableData[1, 2] = False
        plt_LableData[1, 3] = True

    def onClicked_radioButton_off_crvft_3(self):
        """onClicked_radioButton_off_crvft_3(self) -> None

        Handle a legacy curve-fit radio-button click.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        self.radioButton__off_crvft_3.setChecked(True)
        self.radioButton_Equation_crvft_3.setChecked(False)
        self.radioButton_Label_crvft_3.setChecked(False)
        plt_LableData[2, 1] = True
        plt_LableData[2, 2] = False
        plt_LableData[2, 3] = False

    def onClicked_radioButton_Equation_crvft_3(self):
        """onClicked_radioButton_Equation_crvft_3(self) -> None

        Handle a legacy curve-fit radio-button click.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        self.radioButton_Equation_crvft_3.setChecked(True)
        self.radioButton__off_crvft_3.setChecked(False)
        self.radioButton_Label_crvft_3.setChecked(False)
        plt_LableData[2, 1] = False
        plt_LableData[2, 2] = True
        plt_LableData[2, 3] = False

    def onClicked_radioButton_Label_crvft_3(self):
        """onClicked_radioButton_Label_crvft_3(self) -> None

        Handle a legacy curve-fit radio-button click.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        self.radioButton_Label_crvft_3.setChecked(True)
        self.radioButton__off_crvft_3.setChecked(False)
        self.radioButton_Equation_crvft_3.setChecked(False)
        plt_LableData[2, 1] = False
        plt_LableData[2, 2] = False
        plt_LableData[2, 3] = True

    def onClicked_radioButton_off_crvft_4(self):
        """onClicked_radioButton_off_crvft_4(self) -> None

        Handle a legacy curve-fit radio-button click.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        self.radioButton__off_crvft_4.setChecked(True)
        self.radioButton_Equation_crvft_4.setChecked(False)
        self.radioButton_Label_crvft_4.setChecked(False)
        plt_LableData[3, 1] = True
        plt_LableData[3, 2] = False
        plt_LableData[3, 3] = False

    def onClicked_radioButton_Equation_crvft_4(self):
        """onClicked_radioButton_Equation_crvft_4(self) -> None

        Handle a legacy curve-fit radio-button click.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        self.radioButton_Equation_crvft_4.setChecked(True)
        self.radioButton__off_crvft_4.setChecked(False)
        self.radioButton_Label_crvft_4.setChecked(False)
        plt_LableData[3, 1] = False
        plt_LableData[3, 2] = True
        plt_LableData[3, 3] = False

    def onClicked_radioButton_Label_crvft_4(self):
        """onClicked_radioButton_Label_crvft_4(self) -> None

        Handle a legacy curve-fit radio-button click.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        self.radioButton_Label_crvft_4.setChecked(True)
        self.radioButton__off_crvft_4.setChecked(False)
        self.radioButton_Equation_crvft_4.setChecked(False)
        plt_LableData[3, 1] = False
        plt_LableData[3, 2] = False
        plt_LableData[3, 3] = True

    def onClicked_radioButton_off_crvft_5(self):
        """onClicked_radioButton_off_crvft_5(self) -> None

        Handle a legacy curve-fit radio-button click.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        self.radioButton__off_crvft_5.setChecked(True)
        self.radioButton_Equation_crvft_5.setChecked(False)
        self.radioButton_Label_crvft_5.setChecked(False)
        plt_LableData[4, 1] = True
        plt_LableData[4, 2] = False
        plt_LableData[4, 3] = False

    def onClicked_radioButton_Equation_crvft_5(self):
        """onClicked_radioButton_Equation_crvft_5(self) -> None

        Handle a legacy curve-fit radio-button click.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        self.radioButton_Equation_crvft_5.setChecked(True)
        self.radioButton__off_crvft_5.setChecked(False)
        self.radioButton_Label_crvft_5.setChecked(False)
        plt_LableData[4, 1] = False
        plt_LableData[4, 2] = True
        plt_LableData[4, 3] = False

    def onClicked_radioButton_Label_crvft_5(self):
        """onClicked_radioButton_Label_crvft_5(self) -> None

        Handle a legacy curve-fit radio-button click.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        self.radioButton_Label_crvft_5.setChecked(True)
        self.radioButton__off_crvft_5.setChecked(False)
        self.radioButton_Equation_crvft_5.setChecked(False)
        plt_LableData[4, 1] = False
        plt_LableData[4, 2] = False
        plt_LableData[4, 3] = True

    def onClicked_radioButton_off_crvft_6(self):
        """onClicked_radioButton_off_crvft_6(self) -> None

        Handle a legacy curve-fit radio-button click.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        self.radioButton__off_crvft_6.setChecked(True)
        self.radioButton_Equation_crvft_6.setChecked(False)
        self.radioButton_Label_crvft_6.setChecked(False)
        plt_LableData[5, 1] = True
        plt_LableData[5, 2] = False
        plt_LableData[5, 3] = False

    def onClicked_radioButton_Equation_crvft_6(self):
        """onClicked_radioButton_Equation_crvft_6(self) -> None

        Handle a legacy curve-fit radio-button click.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        self.radioButton_Equation_crvft_6.setChecked(True)
        self.radioButton__off_crvft_6.setChecked(False)
        self.radioButton_Label_crvft_6.setChecked(False)
        plt_LableData[5, 1] = False
        plt_LableData[5, 2] = True
        plt_LableData[5, 3] = False

    def onClicked_radioButton_Label_crvft_6(self):
        """onClicked_radioButton_Label_crvft_6(self) -> None

        Handle a legacy curve-fit radio-button click.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        self.radioButton_Label_crvft_6.setChecked(True)
        self.radioButton__off_crvft_6.setChecked(False)
        self.radioButton_Equation_crvft_6.setChecked(False)
        plt_LableData[5, 1] = False
        plt_LableData[5, 2] = False
        plt_LableData[5, 3] = True

    def onClicked_radioButton_off_crvft_7(self):
        """onClicked_radioButton_off_crvft_7(self) -> None

        Handle a legacy curve-fit radio-button click.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        self.radioButton__off_crvft_7.setChecked(True)
        self.radioButton_Equation_crvft_7.setChecked(False)
        self.radioButton_Label_crvft_7.setChecked(False)
        plt_LableData[6, 1] = True
        plt_LableData[6, 2] = False
        plt_LableData[6, 3] = False

    def onClicked_radioButton_Equation_crvft_7(self):
        """onClicked_radioButton_Equation_crvft_7(self) -> None

        Handle a legacy curve-fit radio-button click.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        self.radioButton_Equation_crvft_7.setChecked(True)
        self.radioButton__off_crvft_7.setChecked(False)
        self.radioButton_Label_crvft_7.setChecked(False)
        plt_LableData[6, 1] = False
        plt_LableData[6, 2] = True
        plt_LableData[6, 3] = False

    def onClicked_radioButton_Label_crvft_7(self):
        """onClicked_radioButton_Label_crvft_7(self) -> None

        Handle a legacy curve-fit radio-button click.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        self.radioButton_Label_crvft_7.setChecked(True)
        self.radioButton__off_crvft_7.setChecked(False)
        self.radioButton_Equation_crvft_7.setChecked(False)
        plt_LableData[6, 1] = False
        plt_LableData[6, 2] = False
        plt_LableData[6, 3] = True

    def onClicked_radioButton_off_crvft_8(self):
        """onClicked_radioButton_off_crvft_8(self) -> None

        Handle a legacy curve-fit radio-button click.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        self.radioButton__off_crvft_8.setChecked(True)
        self.radioButton_Equation_crvft_8.setChecked(False)
        self.radioButton_Label_crvft_8.setChecked(False)
        plt_LableData[7, 1] = True
        plt_LableData[7, 2] = False
        plt_LableData[7, 3] = False

    def onClicked_radioButton_Equation_crvft_8(self):
        """onClicked_radioButton_Equation_crvft_8(self) -> None

        Handle a legacy curve-fit radio-button click.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        self.radioButton_Equation_crvft_8.setChecked(True)
        self.radioButton__off_crvft_8.setChecked(False)
        self.radioButton_Label_crvft_8.setChecked(False)
        plt_LableData[7, 1] = False
        plt_LableData[7, 2] = True
        plt_LableData[7, 3] = False

    def onClicked_radioButton_Label_crvft_8(self):
        """onClicked_radioButton_Label_crvft_8(self) -> None

        Handle a legacy curve-fit radio-button click.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        self.radioButton_Label_crvft_8.setChecked(True)
        self.radioButton__off_crvft_8.setChecked(False)
        self.radioButton_Equation_crvft_8.setChecked(False)
        plt_LableData[7, 1] = False
        plt_LableData[7, 2] = False
        plt_LableData[7, 3] = True

    def onClicked_radioButton_off_crvft_9(self):
        """onClicked_radioButton_off_crvft_9(self) -> None

        Handle a legacy curve-fit radio-button click.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        self.radioButton__off_crvft_9.setChecked(True)
        self.radioButton_Equation_crvft_9.setChecked(False)
        self.radioButton_Label_crvft_9.setChecked(False)
        plt_LableData[8, 1] = True
        plt_LableData[8, 2] = False
        plt_LableData[8, 3] = False

    def onClicked_radioButton_Equation_crvft_9(self):
        """onClicked_radioButton_Equation_crvft_9(self) -> None

        Handle a legacy curve-fit radio-button click.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        self.radioButton_Equation_crvft_9.setChecked(True)
        self.radioButton__off_crvft_9.setChecked(False)
        self.radioButton_Label_crvft_9.setChecked(False)
        plt_LableData[8, 1] = False
        plt_LableData[8, 2] = True
        plt_LableData[8, 3] = False

    def onClicked_radioButton_Label_crvft_9(self):
        """onClicked_radioButton_Label_crvft_9(self) -> None

        Handle a legacy curve-fit radio-button click.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        self.radioButton_Label_crvft_9.setChecked(True)
        self.radioButton__off_crvft_9.setChecked(False)
        self.radioButton_Equation_crvft_9.setChecked(False)
        plt_LableData[8, 1] = False
        plt_LableData[8, 2] = False
        plt_LableData[8, 3] = True

    def onClicked_radioButton_off_crvft_10(self):
        """onClicked_radioButton_off_crvft_10(self) -> None

        Handle a legacy curve-fit radio-button click.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        self.radioButton__off_crvft_10.setChecked(True)
        self.radioButton_Equation_crvft_10.setChecked(False)
        self.radioButton_Label_crvft_10.setChecked(False)
        plt_LableData[9, 1] = True
        plt_LableData[9, 2] = False
        plt_LableData[9, 3] = False

    def onClicked_radioButton_Equation_crvft_10(self):
        """onClicked_radioButton_Equation_crvft_10(self) -> None

        Handle a legacy curve-fit radio-button click.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        self.radioButton_Equation_crvft_10.setChecked(True)
        self.radioButton__off_crvft_10.setChecked(False)
        self.radioButton_Label_crvft_10.setChecked(False)
        plt_LableData[9, 1] = False
        plt_LableData[9, 2] = True
        plt_LableData[9, 3] = False

    def onClicked_radioButton_Label_crvft_10(self):
        """onClicked_radioButton_Label_crvft_10(self) -> None

        Handle a legacy curve-fit radio-button click.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        self.radioButton_Label_crvft_10.setChecked(True)
        self.radioButton__off_crvft_10.setChecked(False)
        self.radioButton_Equation_crvft_10.setChecked(False)
        plt_LableData[9, 1] = False
        plt_LableData[9, 2] = False
        plt_LableData[9, 3] = True

    def onClicked_radioButton_off_crvft_11(self):
        """onClicked_radioButton_off_crvft_11(self) -> None

        Handle a legacy curve-fit radio-button click.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        self.radioButton__off_crvft_11.setChecked(True)
        self.radioButton_Equation_crvft_11.setChecked(False)
        self.radioButton_Label_crvft_11.setChecked(False)
        plt_LableData[10, 1] = True
        plt_LableData[10, 2] = False
        plt_LableData[10, 3] = False

    def onClicked_radioButton_Equation_crvft_11(self):
        """onClicked_radioButton_Equation_crvft_11(self) -> None

        Handle a legacy curve-fit radio-button click.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        self.radioButton_Equation_crvft_11.setChecked(True)
        self.radioButton__off_crvft_11.setChecked(False)
        self.radioButton_Label_crvft_11.setChecked(False)
        plt_LableData[10, 1] = False
        plt_LableData[10, 2] = True
        plt_LableData[10, 3] = False

    def onClicked_radioButton_Label_crvft_11(self):
        """onClicked_radioButton_Label_crvft_11(self) -> None

        Handle a legacy curve-fit radio-button click.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        self.radioButton_Label_crvft_11.setChecked(True)
        self.radioButton__off_crvft_11.setChecked(False)
        self.radioButton_Equation_crvft_11.setChecked(False)
        plt_LableData[10, 1] = False
        plt_LableData[10, 2] = False
        plt_LableData[10, 3] = True

    def definePlotParameters(self):
        """definePlotParameters(self) -> None

        Persist current legacy plot settings and refresh or open the legacy plot window.

        Parameters:
            self (Ui_ConfigWindow): Active configuration window instance.

        Returns:
            None
        """
        global Grid_Style
        global Grid_Width
        global Grid_Color
        global Marker_Style
        global Marker_Size
        global Marker_Color
        global Line_Style
        global Line_Width
        global Line_Color
        global Label_PlotLabel
        global Label_PlotxLabel
        global Label_PlotyLabel
        global Label_PlotLegend
        Label_PlotLabel = str(self.lineEdit_PlotLabel.text())
        Label_PlotxLabel = str(self.lineEdit_PlotxLabel.text())
        Label_PlotyLabel = str(self.lineEdit_PlotyLabel.text())
        Label_PlotLegend = str(self.lineEdit_PlotLegend.text())
        Grid_Style = self.comboBox_Grid_Style.currentText()
        Grid_Width = self.lineEdit_Grid_Width.text()
        Grid_Color = self.comboBox_Grid_Color.currentText()
        Marker_Style = self.comboBox_Marker_Style.currentText()
        Marker_Size = self.lineEdit_Marker_Size.text()
        Marker_Color = self.comboBox_Marker_Color.currentText()
        Line_Style = self.comboBox_Line_Style.currentText()
        Line_Width = self.lineEdit_Line_Width.text()
        Line_Color = self.comboBox_Line_Color.currentText()
        try:
            if list(tableLabels == 1).count(True) == 1 and list(tableLabels == 3).count(True) == 1:
                owner = getattr(self, "owner", None)
                if owner is not None and hasattr(owner, "plot_window"):
                    if owner.plot_window.isVisible():
                        owner.plot_window.refresh_plot()
                        owner.plot_window.raise_()
                        owner.plot_window.activateWindow()
                    else:
                        owner.plot_window = Plot_Window(getattr(owner, "_main_window", None))
                        owner.plot_window.show()
                else:
                    Plot_Window(getattr(owner, "_main_window", None) if owner is not None else None).show()
        except Exception as e:
            pass


class about_gui(QWidget):
    """Modal about dialog showing app version, authors, links, and license."""

    def __init__(self):
        """__init__(self) -> None

        Initialize the object.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        super().__init__()
        self.initUI()

    def initUI(self):
        """initUI(self) -> None

        Initui.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        message = "<p><strong>PhysPlot: Advanced Plotting Made Simple<br /></strong>Version: 2.0.0 (5/15/2026)</p><p>PhysPlot was developed by M. Shiraz Ahmad based on an idea conceptualized by Dr. Sabieh Anwar.</p><p><strong>Details: </strong><a href='https://physplot.readthedocs.io/'>PhysPlot Documentation</a></p><p>For feature enhancement requests or bug reports, visit <a href='https://github.com/MShirazAhmad/PhysPlot/issues'>MShirazAhmad/PhysPlot</a>.</p><p><strong>Licenses:</strong> Code uses PolyForm Noncommercial 1.0.0. Documentation and educational media use CC BY-NC 4.0.</p><p>Commercial use requires written permission from the project originator.</p><p>Copyright &copy; 2019-2026 PhysPlot project originator.</p>"
        msg_box = QMessageBox()
        msg_box.setWindowIcon(QtGui.QIcon(str(APP_ICON_PATH)))
        msg_box.setWindowTitle("About PhysPlot")
        msg_box.setIconPixmap(QtGui.QPixmap(str(APP_ICON_PATH)).scaled(
            64,
            64,
            QtCore.Qt.KeepAspectRatio,
            QtCore.Qt.SmoothTransformation,
        ))
        msg_box.setTextFormat(QtCore.Qt.RichText)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()


class pick_file_to_append(QWidget):
    """File picker dialog used to select an input dataset for import."""

    def __init__(self):
        """__init__(self) -> None

        Initialize the object.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        super().__init__()
        self.title = "Please Pick multiple Physlogger' exported files"
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.initUI()

    def initUI(self):
        """initUI(self) -> None

        Initui.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        self.setWindowTitle(self.title)
        self.setWindowIcon(QtGui.QIcon(str(APP_ICON_PATH)))
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.openFileNamesDialog()

    def openFileNamesDialog(self):
        """openFileNamesDialog(self) -> None

        Openfilenamesdialog.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        global files
        options = QFileDialog.Options()
        options |= QFileDialog.DontConfirmOverwrite
        files, _ = QFileDialog.getOpenFileName(None, "Pick Variables File", "",
                                               "All Files (*);;OES HRF (*.HRF *.hrf);;Excel Files (*.xlsx);; CSV (*.csv);;TSV (*.txt)",
                                               options=options)


class SaveFile(QWidget):
    """Save dialog wrapper that exports the current output table to text."""

    def __init__(self):
        """__init__(self) -> None

        Initialize the object.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        super().__init__()
        self.title = 'Qt file dialogs'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.initUI()

    def initUI(self):
        """initUI(self) -> None

        Initui.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        self.setWindowTitle(self.title)
        self.setWindowIcon(QtGui.QIcon(str(APP_ICON_PATH)))
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.saveFileDialog()

    def saveFileDialog(self):
        """saveFileDialog(self) -> None

        Savefiledialog.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(None, "Save File", "",
                                                  "Text Files (*.txt);;All Files (*)")
        if fileName:
            global exportFilePath
            exportFilePath = fileName
            np.savetxt(exportFilePath, np.around(np.single(OutPut_Table), decimals=6), delimiter='\t', fmt='%.3f')


class Plot_Window(QDialog):
    """Plot dialog that renders data, errors, legend, and optional fits."""

    def __init__(self, parent=None):
        """__init__(self, parent) -> None

        Initialize the object.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        super(Plot_Window, self).__init__(parent)
        self.setWindowIcon(QtGui.QIcon(str(APP_ICON_PATH)))
        self.setWindowTitle("PhysPlot - Plot Window")
        # a figure instance to plot on
        self.figure = Figure()
        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        # set the layout
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        self.refresh_plot()

    def refresh_plot(self):
        """refresh_plot(self) -> None

        Redraw the existing plot canvas using current table and config state.

        Parameters:
            self (Plot_Window): Active plot dialog instance.

        Returns:
            None
        """
        self.figure.clear()
        label_counts = {role: int(np.count_nonzero(tableLabels == role)) for role in range(1, 5)}
        has_x = label_counts[1] == 1
        has_xerr = label_counts[2] == 1
        has_y = label_counts[3] == 1
        has_yerr = label_counts[4] == 1
        if has_x:
            xIndex = int(np.where(tableLabels == 1)[0][0])
            x = OutPut_Table[:, xIndex]
        if has_xerr:
            uxIndex = int(np.where(tableLabels == 2)[0][0])
            xerr = OutPut_Table[:, uxIndex]
        if has_y:
            yIndex = int(np.where(tableLabels == 3)[0][0])
            y = OutPut_Table[:, yIndex]
        if has_yerr:
            uyIndex = int(np.where(tableLabels == 4)[0][0])
            yerr = OutPut_Table[:, uyIndex]
        ax = self.figure.add_subplot(111)
        ax.set_xlabel(Label_PlotxLabel)
        ax.set_ylabel(Label_PlotyLabel)
        ax.set_title(Label_PlotLabel)
        ax.grid(color=COLORS[Grid_Color], linestyle=LINESTYLES[Grid_Style], linewidth=float(Grid_Width))
        try:
            #        slope, intercept, r_value, p_value, stderr = linregress(x, y)
            #        Equation = 'y = ' + str(np.round(slope, 7)) + 'x + ' + str(np.round(intercept, 7))
            if has_x and has_y:
                errorbar_options = {}
                if has_xerr:
                    errorbar_options["xerr"] = xerr
                if has_yerr:
                    errorbar_options["yerr"] = yerr
                ax.errorbar(
                    x, y,
                    marker=MARKERS[Marker_Style],
                    markerfacecolor=COLORS[Marker_Color],
                    markeredgecolor=COLORS[Marker_Color],
                    markersize=float(Marker_Size),
                    linestyle=LINESTYLES[Line_Style],
                    linewidth=float(Line_Width),
                    color=COLORS[Line_Color],
                    elinewidth=1,
                    capsize=5,
                    capthick=1,
                    label=Label_PlotLegend,
                    **errorbar_options,
                )
        except Exception as e:
            self.errMessage("Generating Plot:", str(e))

        try:
            fit_rows = globals().get("CURVE_FIT_ROWS", [])
            custom_labels = [row["line_edit"].text() for row in fit_rows]
            fit_definitions = globals().get("ACTIVE_CURVE_FIT_DEFINITIONS", [])
            for index, fit_definition in enumerate(fit_definitions[:len(plt_LableData)]):
                try:
                    if plt_LableData[index, 0]:
                        custom_label = custom_labels[index] if index < len(custom_labels) else fit_definition["default_label"]
                        if not custom_label:
                            custom_label = fit_definition["default_label"]
                        if fit_definition["kind"] == "poly":
                            coefficients = np.polyfit(x, y, fit_definition["degree"])
                            polynomial = np.poly1d(coefficients)
                            ax.plot(
                                x,
                                polynomial(x),
                                '-',
                                label=fit_label(plt_LableData, index, coefficients, custom_label),
                            )
                        elif fit_definition["kind"] == "callable":
                            fit_function = fit_definition["function"]
                            initial_guess = fit_definition.get("initial_guess")
                            popt, pcov = curve_fit(fit_function, x, y, p0=initial_guess)
                            ax.plot(
                                x,
                                fit_function(x, *popt),
                                label=fit_label(plt_LableData, index, popt, custom_label),
                            )
                except Exception as e:
                    self.errMessage(fit_definition["display_name"] + ":", str(e))
        except Exception as e:
            self.errMessage("Curve Fitting:", str(e))

        #       ax.text(0.05, 0.95, Equation, transform=ax.transAxes, fontsize=11,
        #              verticalalignment='top')
        if ax.get_legend_handles_labels()[0]:
            ax.legend(loc='upper left', fontsize='small')
        self.figure.tight_layout()
        self.canvas.draw()

    def errMessage(self, Text, InformativeText):
        """Show an error dialog from the standalone legacy plot window."""
        msgBox = QMessageBox(self)
        msgBox.setWindowIcon(QtGui.QIcon(str(APP_ICON_PATH)))
        msgBox.setIcon(QMessageBox.Critical)
        msgBox.setText(Text)
        msgBox.setInformativeText(InformativeText)
        msgBox.setWindowTitle("Warning")
        msgBox.exec_()


class Ui_MainWindow(object):
    """Primary PhysPlot window for table editing, transforms, and plot launch."""

    def setupUi(self, MainWindow):
        """setupUi(self, MainWindow) -> None

        Configure generated Qt user-interface widgets and signals.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(601, 643)
        self._main_window = MainWindow
        MainWindow.setMaximumSize(QtCore.QSize(16777215, 16777215))
        MainWindow.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        MainWindow.setFocusPolicy(QtCore.Qt.ClickFocus)
        MainWindow.setLayoutDirection(QtCore.Qt.LeftToRight)
        MainWindow.setAutoFillBackground(False)
        MainWindow.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.Pakistan))
        MainWindow.setInputMethodHints(QtCore.Qt.ImhNone)
        MainWindow.setDockOptions(
            QtWidgets.QMainWindow.AllowTabbedDocks | QtWidgets.QMainWindow.AnimatedDocks | QtWidgets.QMainWindow.VerticalTabs)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setTabletTracking(True)
        self.centralwidget.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.centralwidget.setAcceptDrops(True)
        self.centralwidget.setAutoFillBackground(True)
        self.centralwidget.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setMaximumSize(QtCore.QSize(220, 91))
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap(str(APP_LOGO_PATH)))
        self.label.setScaledContents(True)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.horizontalLayout_3.addWidget(self.label)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.gridLayout_2.addLayout(self.horizontalLayout_3, 0, 0, 1, 2)
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.tableWidget.setAutoFillBackground(True)
        self.tableWidget.setInputMethodHints(QtCore.Qt.ImhNone)
        self.tableWidget.setEditTriggers(
            QtWidgets.QAbstractItemView.AnyKeyPressed | QtWidgets.QAbstractItemView.DoubleClicked | QtWidgets.QAbstractItemView.EditKeyPressed)
        self.tableWidget.setDragEnabled(True)
        self.tableWidget.setAlternatingRowColors(True)
        self.tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.tableWidget.setRowCount(10)
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setObjectName("tableWidget")
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        self.tableWidget.horizontalHeader().font()

        self.tableWidget.horizontalHeader().setVisible(True)
        self.tableWidget.horizontalHeader().setCascadingSectionResizes(True)
        self.tableWidget.horizontalHeader().setHighlightSections(True)
        self.tableWidget.horizontalHeader().setSortIndicatorShown(False)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.verticalHeader().setCascadingSectionResizes(False)
        self.tableWidget.verticalHeader().setSortIndicatorShown(False)
        self.tableWidget.verticalHeader().setStretchLastSection(False)
        self.gridLayout_2.addWidget(self.tableWidget, 1, 0, 1, 2)
        self.groupBox_3 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_3.setTitle("")
        self.groupBox_3.setObjectName("groupBox_3")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox_3)
        self.gridLayout.setObjectName("gridLayout")
        self.pushButton_5 = QtWidgets.QPushButton(self.groupBox_3)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.pushButton_5.setFont(font)
        self.pushButton_5.setObjectName("pushButton_5")
        self.gridLayout.addWidget(self.pushButton_5, 0, 0, 1, 1)
        self.checkBox_2 = QtWidgets.QCheckBox(self.groupBox_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.checkBox_2.sizePolicy().hasHeightForWidth())
        self.checkBox_2.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.checkBox_2.setFont(font)
        self.checkBox_2.setObjectName("checkBox_2")
        self.gridLayout.addWidget(self.checkBox_2, 1, 0, 1, 1)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.Rows_label = QtWidgets.QLabel(self.groupBox_3)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.Rows_label.setFont(font)
        self.Rows_label.setObjectName("Rows_label")
        self.verticalLayout_2.addWidget(self.Rows_label)
        self.Columns_label = QtWidgets.QLabel(self.groupBox_3)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.Columns_label.setFont(font)
        self.Columns_label.setObjectName("Columns_label")
        self.verticalLayout_2.addWidget(self.Columns_label)
        self.horizontalLayout_4.addLayout(self.verticalLayout_2)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.Rows_lineEdit = QtWidgets.QLineEdit(self.groupBox_3)
        self.Rows_lineEdit.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.Rows_lineEdit.setObjectName("Rows_lineEdit")
        self.verticalLayout.addWidget(self.Rows_lineEdit)
        self.Columns_lineEdit = QtWidgets.QLineEdit(self.groupBox_3)
        self.Columns_lineEdit.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.Columns_lineEdit.setObjectName("Columns_lineEdit")

        validator = QtGui.QDoubleValidator()

        int_validator = QtGui.QIntValidator(1, 1000000)

        self.Rows_lineEdit.setText("10")
        self.Columns_lineEdit.setText("4")
        self.Rows_lineEdit.setValidator(int_validator)
        self.Columns_lineEdit.setValidator(int_validator)
        self.verticalLayout.addWidget(self.Columns_lineEdit)
        self.horizontalLayout_4.addLayout(self.verticalLayout)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.pushButton_RP = QtWidgets.QPushButton(self.groupBox_3)
        self.pushButton_RP.setMaximumSize(QtCore.QSize(40, 29))
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_RP.setFont(font)
        self.pushButton_RP.setObjectName("pushButton_RP")
        self.verticalLayout_3.addWidget(self.pushButton_RP)
        self.pushButton_CP = QtWidgets.QPushButton(self.groupBox_3)
        self.pushButton_CP.setMaximumSize(QtCore.QSize(40, 29))
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_CP.setFont(font)
        self.pushButton_CP.setObjectName("pushButton_CP")
        self.verticalLayout_3.addWidget(self.pushButton_CP)
        self.horizontalLayout_4.addLayout(self.verticalLayout_3)
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.pushButton_RM = QtWidgets.QPushButton(self.groupBox_3)
        self.pushButton_RM.setMaximumSize(QtCore.QSize(39, 29))
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_RM.setFont(font)
        self.pushButton_RM.setObjectName("pushButton_RM")
        self.verticalLayout_6.addWidget(self.pushButton_RM)
        self.pushButton_CM = QtWidgets.QPushButton(self.groupBox_3)
        self.pushButton_CM.setMaximumSize(QtCore.QSize(39, 29))
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_CM.setFont(font)
        self.pushButton_CM.setObjectName("pushButton_CM")
        self.verticalLayout_6.addWidget(self.pushButton_CM)
        self.horizontalLayout_4.addLayout(self.verticalLayout_6)
        self.gridLayout.addLayout(self.horizontalLayout_4, 2, 0, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox_3, 2, 0, 1, 1)
        self.groupBox_4 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_4.setTitle("")
        self.groupBox_4.setObjectName("groupBox_4")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.groupBox_4)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_data_loader = QtWidgets.QLabel(self.groupBox_4)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_data_loader.setFont(font)
        self.label_data_loader.setObjectName("label_data_loader")
        self.gridLayout_3.addWidget(self.label_data_loader, 0, 0, 1, 1)
        self.comboBox_data_loader = QtWidgets.QComboBox(self.groupBox_4)
        self.comboBox_data_loader.setObjectName("comboBox_data_loader")
        self.gridLayout_3.addWidget(self.comboBox_data_loader, 1, 0, 1, 1)
        self.pushButton = QtWidgets.QPushButton(self.groupBox_4)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout_3.addWidget(self.pushButton, 2, 0, 1, 1)
        self.pushButton_3 = QtWidgets.QPushButton(self.groupBox_4)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.pushButton_3.setFont(font)
        self.pushButton_3.setObjectName("pushButton_3")
        self.gridLayout_3.addWidget(self.pushButton_3, 3, 0, 1, 1)
        self.pushButton_4 = QtWidgets.QPushButton(self.groupBox_4)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.pushButton_4.setFont(font)
        self.pushButton_4.setObjectName("pushButton_4")
        self.gridLayout_3.addWidget(self.pushButton_4, 4, 0, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox_4, 2, 1, 1, 1)
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.groupBox.setFont(font)
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout(self.groupBox)
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.groupBox_5 = QtWidgets.QGroupBox(self.groupBox)
        self.groupBox_5.setTitle("")
        self.groupBox_5.setObjectName("groupBox_5")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.groupBox_5)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.Rows_label_2 = QtWidgets.QLabel(self.groupBox_5)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.Rows_label_2.setFont(font)
        self.Rows_label_2.setObjectName("Rows_label_2")
        self.verticalLayout_4.addWidget(self.Rows_label_2)
        self.Columns_label_2 = QtWidgets.QLabel(self.groupBox_5)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.Columns_label_2.setFont(font)
        self.Columns_label_2.setObjectName("Columns_label_2")
        self.verticalLayout_4.addWidget(self.Columns_label_2)
        self.gridLayout_4.addLayout(self.verticalLayout_4, 0, 0, 1, 1)
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.Rows_lineEdit_2 = QtWidgets.QLineEdit(self.groupBox_5)
        self.Rows_lineEdit_2.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.Rows_lineEdit_2.setObjectName("Rows_lineEdit_2")
        self.verticalLayout_5.addWidget(self.Rows_lineEdit_2)
        self.Columns_lineEdit_2 = QtWidgets.QLineEdit(self.groupBox_5)
        self.Columns_lineEdit_2.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.Columns_lineEdit_2.setObjectName("Columns_lineEdit_2")
        self.verticalLayout_5.addWidget(self.Columns_lineEdit_2)
        self.gridLayout_4.addLayout(self.verticalLayout_5, 0, 1, 1, 1)
        self.horizontalLayout_9.addWidget(self.groupBox_5)
        self.groupBox_2 = QtWidgets.QGroupBox(self.groupBox)
        self.groupBox_2.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.groupBox_2.setFont(font)
        self.groupBox_2.setObjectName("groupBox_2")
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout(self.groupBox_2)
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.comboBox_scale_x = QtWidgets.QComboBox(self.groupBox_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox_scale_x.sizePolicy().hasHeightForWidth())
        self.comboBox_scale_x.setSizePolicy(sizePolicy)
        self.comboBox_scale_x.setMinimumSize(QtCore.QSize(0, 0))
        self.comboBox_scale_x.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(11)
        self.comboBox_scale_x.setFont(font)
        self.comboBox_scale_x.setObjectName("comboBox_scale_x")
        self.comboBox_scale_x.addItem("")
        self.comboBox_scale_x.addItem("")
        self.comboBox_scale_x.addItem("")
        self.comboBox_scale_x.addItem("")
        self.comboBox_scale_x.addItem("")
        self.comboBox_scale_x.addItem("")
        self.comboBox_scale_x.addItem("")
        self.comboBox_scale_x.addItem("")
        self.comboBox_scale_x.addItem("")
        self.comboBox_scale_x.addItem("")
        self.comboBox_scale_x.addItem("")
        self.comboBox_scale_x.addItem("")
        self.comboBox_scale_x.addItem("")
        self.horizontalLayout_8.addWidget(self.comboBox_scale_x)
        spacerItem2 = QtWidgets.QSpacerItem(0, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem2)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_3 = QtWidgets.QLabel(self.groupBox_2)
        font = QtGui.QFont()
        font.setFamily("Kozuka Gothic Pr6N B")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setTextFormat(QtCore.Qt.RichText)
        self.label_3.setScaledContents(True)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_2.addWidget(self.label_3)
        self.lineEdit_scale_x_x = QtWidgets.QLineEdit(self.groupBox_2)
        self.lineEdit_scale_x_x.setMinimumSize(QtCore.QSize(0, 0))
        self.lineEdit_scale_x_x.setMaximumSize(QtCore.QSize(120, 16777215))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.lineEdit_scale_x_x.setFont(font)
        self.lineEdit_scale_x_x.setObjectName("lineEdit_scale_x_x")
        self.horizontalLayout_2.addWidget(self.lineEdit_scale_x_x)
        self.horizontalLayout_8.addLayout(self.horizontalLayout_2)
        spacerItem3 = QtWidgets.QSpacerItem(0, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem3)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_4 = QtWidgets.QLabel(self.groupBox_2)
        font = QtGui.QFont()
        font.setFamily("Kozuka Gothic Pr6N B")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.label_4.setTextFormat(QtCore.Qt.RichText)
        self.label_4.setScaledContents(True)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout.addWidget(self.label_4)
        self.lineEdit_scale_x_plus = QtWidgets.QLineEdit(self.groupBox_2)
        self.lineEdit_scale_x_plus.setMaximumSize(QtCore.QSize(107, 16777215))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.lineEdit_scale_x_plus.setFont(font)
        self.lineEdit_scale_x_plus.setObjectName("lineEdit_scale_x_plus")
        self.horizontalLayout.addWidget(self.lineEdit_scale_x_plus)
        self.horizontalLayout_8.addLayout(self.horizontalLayout)
        self.pushButton_2 = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButton_2.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout_8.addWidget(self.pushButton_2)
        self.horizontalLayout_9.addWidget(self.groupBox_2)
        self.gridLayout_2.addWidget(self.groupBox, 3, 0, 1, 2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 601, 21))
        self.menubar.setObjectName("menubar")
        self.menuSettings = QtWidgets.QMenu(self.menubar)
        self.menuSettings.setObjectName("menuSettings")
        self.menuFileLoader = QtWidgets.QMenu(self.menuSettings)
        self.menuFileLoader.setObjectName("menuFileLoader")
        self.menuFunctions = QtWidgets.QMenu(self.menubar)
        self.menuFunctions.setObjectName("menuFunctions")
        self.menuABC = QtWidgets.QMenu(self.menubar)
        self.menuABC.setObjectName("menuABC")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionHome_Page = QtWidgets.QAction(MainWindow)
        self.actionHome_Page.setObjectName("actionHome_Page")
        self.actionHome_Page.setMenuRole(QtWidgets.QAction.NoRole)
        self.actionHome_Page_2 = QtWidgets.QAction(MainWindow)
        self.actionHome_Page_2.setObjectName("actionHome_Page_2")
        self.actionHome_Page_2.setMenuRole(QtWidgets.QAction.NoRole)
        self.actionHome_Page_2.triggered.connect(self.open_home_page)
        self.menuSettings.addMenu(self.menuFileLoader)
        self.menubar.addAction(self.menuSettings.menuAction())
        self.menubar.addAction(self.menuFunctions.menuAction())
        self.menuABC.addAction(self.actionHome_Page)
        self.actionHome_Page.triggered.connect(self.about_gui_command)
        self.menuABC.addAction(self.actionHome_Page_2)
        self.menubar.addAction(self.menuABC.menuAction())

        self.retranslateUi(MainWindow)
        self._setup_function_menu()
        self._setup_file_loader_menu()
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        validator1 = QtGui.QIntValidator(0, 100)
        self.Rows_lineEdit_2.setValidator(validator1)
        self.Columns_lineEdit_2.setValidator(validator1)
        self.Rows_lineEdit_2.setText("0")
        self.Columns_lineEdit_2.setText("0")

    def retranslateUi(self, MainWindow):
        """retranslateUi(self, MainWindow) -> None

        Configure generated Qt user-interface widgets and signals.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "PhysPlot"))
        self.tableWidget.setSortingEnabled(False)
        self.pushButton_5.setText(_translate("MainWindow", "New Table"))
        self.checkBox_2.setText(_translate("MainWindow", "Delete Old Entries"))
        self.Rows_label.setText(_translate("MainWindow", "#Rows:"))
        self.Columns_label.setText(_translate("MainWindow", "#Columns:"))
        self.pushButton_RP.setText(_translate("MainWindow", "+"))
        self.pushButton_CP.setText(_translate("MainWindow", "+"))
        self.pushButton_RM.setText(_translate("MainWindow", "-"))
        self.pushButton_CM.setText(_translate("MainWindow", "-"))
        self.pushButton.setText(_translate("MainWindow", "Import Data"))
        self.pushButton_3.setText(_translate("MainWindow", "Export Data"))
        self.pushButton_4.setText(_translate("MainWindow", "Generate Plot"))
        self.label_data_loader.setText(_translate("MainWindow", "Data Loader:"))
        self.groupBox.setTitle(_translate("MainWindow", "Apply Mathematical Transformation to Column"))
        self.Rows_label_2.setText(_translate("MainWindow", "Input Col.:"))
        self.Columns_label_2.setText(_translate("MainWindow", "Output Col.:"))
        self.groupBox_2.setTitle(_translate("MainWindow", "Functions"))
        _set_combo_items(self.comboBox_scale_x, SCALE_X_OPTIONS)
        self.label_3.setText(_translate("MainWindow", "x"))
        self.lineEdit_scale_x_x.setText(_translate("MainWindow", "1"))
        self.label_4.setText(_translate("MainWindow", "+"))
        self.lineEdit_scale_x_plus.setText(_translate("MainWindow", "0"))
        self.pushButton_2.setText(_translate("MainWindow", "Apply"))
        self.menuSettings.setTitle(_translate("MainWindow", "Settings"))
        self.menuFunctions.setTitle(_translate("MainWindow", "Functions"))
        self.menuFileLoader.setTitle(_translate("MainWindow", "File Loader"))
        self.menuABC.setTitle(_translate("MainWindow", "Help"))
        self.actionHome_Page.setText(_translate("MainWindow", "About"))
        self.actionHome_Page_2.setText(_translate("MainWindow", "Documentation"))
        self.pushButton.clicked.connect(self.btn_LoadData)

        self.pushButton_4.clicked.connect(self.btn_GeneratePlot)
        self.pushButton_5.clicked.connect(self.btn_ClearTable)
        self.pushButton_3.clicked.connect(self.btn_SaveTable)
        self.pushButton_2.clicked.connect(self.readRow)
        self.tableWidget.keyPressEvent = self.keyPressEvent
        self.pushButton_RP.clicked.connect(self.btn_RP)
        self.pushButton_RM.clicked.connect(self.btn_RM)
        self.pushButton_CP.clicked.connect(self.btn_CP)
        self.pushButton_CM.clicked.connect(self.btn_CM)
        validator = QtGui.QDoubleValidator()
        self.lineEdit_scale_x_x.setValidator(validator)
        self.lineEdit_scale_x_plus.setValidator(validator)
        global tableLabels
        tableLabels = np.zeros(100)
        global xIndex
        global uxIndex
        global yIndex
        global uyIndex
        self.btn_ClearTable()

    def _setup_file_loader_menu(self):
        """_setup_file_loader_menu(self) -> None

        Setup file loader menu.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        self.file_loader_actions = []
        self.active_loader_path = None
        self.active_loader_module = None
        self._loader_module_cache = {}
        self.loader_entries = []
        self.menuFileLoader.clear()
        self.comboBox_data_loader.blockSignals(True)
        self.comboBox_data_loader.clear()
        loader_group = QtWidgets.QActionGroup(self.menuFileLoader)
        loader_group.setExclusive(True)
        loader_files = _discover_loader_files()
        if not loader_files:
            empty_action = QtWidgets.QAction("No loaders found", self.menuFileLoader)
            empty_action.setEnabled(False)
            self.menuFileLoader.addAction(empty_action)
            self.comboBox_data_loader.addItem("No loaders found")
            self.comboBox_data_loader.blockSignals(False)
            return

        for loader_path in loader_files:
            display_name = _loader_display_name(loader_path)
            action = QtWidgets.QAction(display_name, self.menuFileLoader)
            action.setCheckable(True)
            action.setData(str(loader_path))
            action.triggered.connect(lambda _checked=False, path=loader_path: self._set_active_loader(path))
            loader_group.addAction(action)
            self.menuFileLoader.addAction(action)
            self.file_loader_actions.append(action)
            self.loader_entries.append({"display_name": display_name, "path": loader_path})
            self.comboBox_data_loader.addItem(display_name, str(loader_path))

        self.comboBox_data_loader.currentIndexChanged.connect(self._on_data_loader_index_changed)
        self.comboBox_data_loader.blockSignals(False)

        default_loader = next((path for path in loader_files if path.stem == "default_loader"), loader_files[0])
        self._set_active_loader(default_loader)

    def _on_data_loader_index_changed(self, index):
        """_on_data_loader_index_changed(self, index) -> None

        On data loader index changed.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        if index < 0 or index >= len(getattr(self, "loader_entries", [])):
            return
        loader_path = self.comboBox_data_loader.itemData(index)
        if loader_path:
            self._set_active_loader(loader_path)

    def _setup_function_menu(self):
        """_setup_function_menu(self) -> None

        Setup function menu.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        self.function_actions = []
        self.active_function_path = None
        self.active_function_module = None
        self._function_module_cache = {}
        self.function_entries = []
        self.function_lookup = {}
        self.menuFunctions.clear()
        self.comboBox_scale_x.blockSignals(True)
        self.comboBox_scale_x.clear()

        function_files = _discover_function_files()
        if not function_files:
            fallback_items = list(SCALE_X_OPTIONS)
            self.comboBox_scale_x.addItems(fallback_items)
            self.function_entries = [{"display_name": item, "default_label": item, "path": None, "module": None} for item in fallback_items]
            self.function_lookup = {item: None for item in fallback_items}
            self.comboBox_scale_x.blockSignals(False)
            return

        function_group = QtWidgets.QActionGroup(self.menuFunctions)
        function_group.setExclusive(True)

        for index, function_path in enumerate(function_files):
            module = _load_function_module(function_path)
            display_name = getattr(module, "DISPLAY_NAME", function_path.stem.replace("_", " ").title())
            default_label = getattr(module, "DEFAULT_LABEL", display_name)
            self._function_module_cache[str(function_path)] = module
            self.function_entries.append(
                {
                    "display_name": display_name,
                    "default_label": default_label,
                    "path": function_path,
                    "module": module,
                }
            )
            self.function_lookup[display_name] = module

            action = QtWidgets.QAction(display_name, self.menuFunctions)
            action.setCheckable(True)
            action.setData(index)
            action.triggered.connect(lambda _checked=False, idx=index: self.comboBox_scale_x.setCurrentIndex(idx))
            function_group.addAction(action)
            self.menuFunctions.addAction(action)
            self.function_actions.append(action)

        self.comboBox_scale_x.addItems([entry["display_name"] for entry in self.function_entries])
        self.comboBox_scale_x.currentIndexChanged.connect(self._sync_function_menu)
        self.comboBox_scale_x.blockSignals(False)
        if self.function_actions:
            self.comboBox_scale_x.setCurrentIndex(0)
            self._sync_function_menu(0)

    def _sync_function_menu(self, index):
        """_sync_function_menu(self, index) -> None

        Sync function menu.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        for action_index, action in enumerate(getattr(self, "function_actions", [])):
            action.setChecked(action_index == index)

    def _resolve_function_transform(self, function_name):
        """_resolve_function_transform(self, function_name) -> None

        Resolve function transform.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        function_module = getattr(self, "function_lookup", {}).get(function_name)
        if function_module is not None:
            return function_module.transform, getattr(function_module, "DEFAULT_LABEL", function_name)
        legacy_transforms = {
            "x": (lambda values: values, "x"),
            "x^2": (lambda values: np.power(values, 2), "x^2"),
            "x^3": (lambda values: np.power(values, 3), "x^3"),
            "1/x": (lambda values: 1 / values, "1/x"),
            "log10(x)": (np.log10, "log10(x)"),
            "log(x)": (np.log, "log(x)"),
            "e^x": (np.exp, "e^x"),
            "cos(x)": (np.cos, "cos(x)"),
            "sin(x)": (np.sin, "sin(x)"),
            "tan(x)": (np.tan, "tan(x)"),
            "arccos(x)": (np.arccos, "arccos(x)"),
            "arcsin(x)": (np.arcsin, "arcsin(x)"),
            "arctan(x)": (np.arctan, "arctan(x)"),
        }
        transform, default_label = legacy_transforms.get(function_name, legacy_transforms["x"])
        return transform, default_label

    def _set_active_loader(self, loader_path):
        """_set_active_loader(self, loader_path) -> None

        Set active loader.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        loader_path = Path(loader_path)
        loader_key = str(loader_path)
        cached_module = self._loader_module_cache.get(loader_key)
        if cached_module is None:
            cached_module = _load_loader_module(loader_path)
            self._loader_module_cache[loader_key] = cached_module
        self.active_loader_path = loader_path
        self.active_loader_module = cached_module
        for action in getattr(self, "file_loader_actions", []):
            action.setChecked(action.data() == loader_key)
        combo_index = self.comboBox_data_loader.findData(loader_key)
        if combo_index != -1 and self.comboBox_data_loader.currentIndex() != combo_index:
            self.comboBox_data_loader.blockSignals(True)
            self.comboBox_data_loader.setCurrentIndex(combo_index)
            self.comboBox_data_loader.blockSignals(False)

    def _load_table_data(self, file_path):
        """_load_table_data(self, file_path) -> None

        Load table data.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        if self.active_loader_module is None:
            raise RuntimeError("No file loader is selected.")
        table_data = self.active_loader_module.load_data(file_path)
        table_data = np.asarray(table_data)
        if table_data.ndim == 1:
            table_data = np.atleast_2d(table_data).T
        if table_data.ndim != 2:
            raise ValueError("Loader must return a 2D table-like array.")
        return table_data

    def _apply_loader_column_roles(self, column_count):
        """_apply_loader_column_roles(self, column_count) -> None

        Apply loader column roles.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        global tableLabels
        tableLabels = np.zeros(100)
        roles = getattr(self.active_loader_module, "DEFAULT_COLUMN_ROLES", [])
        for column, role_name in enumerate(roles[:column_count]):
            role_value = _role_index(role_name)
            combo = self.tableWidget.cellWidget(0, column)
            if combo is not None:
                combo.setCurrentIndex(role_value)
            else:
                self.btn_combobox_changed(role_value, column)

    def keyPressEvent(self, e):
        """keyPressEvent(self, e) -> None

        Keypressevent.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        if e.key() == Qt.Key_Delete:
            self.delRows()
            self.Rows_lineEdit.setText(str(self.tableWidget.rowCount()))
            self.Columns_lineEdit.setText(str(self.tableWidget.columnCount()))
        else:
            e.ignore()

    def delRows(self):
        """delRows(self) -> None

        Delrows.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        indices = self.tableWidget.selectionModel().selectedRows()
        for index in sorted(indices, reverse=True):
            if index != 0:
                self.tableWidget.removeRow(index.row())

    def shiftVal(self):
        """shiftVal(self) -> None

        Shiftval.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        if int(self.Rows_lineEdit_2.text()) > int(self.tableWidget.rowCount()):
            self.Rows_lineEdit_2.setText("0")
        if int(self.Columns_lineEdit_2.text()) > int(self.tableWidget.columnCount()):
            self.Columns_lineEdit_2.setText("0")

    def btn_RP(self):
        """btn_RP(self) -> None

        Handle the matching GUI button action.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
        self.Rows_lineEdit.setText(str(self.tableWidget.rowCount()))

    def btn_RM(self):
        """btn_RM(self) -> None

        Handle the matching GUI button action.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        if int(self.tableWidget.rowCount()) > 4:
            self.tableWidget.setRowCount(self.tableWidget.rowCount() - 1)
            self.Rows_lineEdit.setText(str(self.tableWidget.rowCount()))

    def btn_CP(self):
        """btn_CP(self) -> None

        Handle the matching GUI button action.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        self.tableWidget.setColumnCount(self.tableWidget.columnCount() + 1)
        self.Columns_lineEdit.setText(str(self.tableWidget.columnCount()))
        combo = QtWidgets.QComboBox()
        _set_combo_items(combo, AXIS_ROLE_OPTIONS)
        self.tableWidget.setCellWidget(0, self.tableWidget.columnCount() - 1, combo)
        column = self.tableWidget.columnCount() - 1
        self.tableWidget.cellWidget(0, column).currentIndexChanged.connect(
            lambda value, col=column: self.btn_combobox_changed(value, col))
        self.shiftVal()

    def btn_CM(self):
        """btn_CM(self) -> None

        Handle the matching GUI button action.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        if int(self.tableWidget.columnCount()) > 2:
            # print("CM", self.tableWidget.columnCount())
            tableLabels[self.tableWidget.columnCount():99] = 0
            self.tableWidget.setColumnCount(self.tableWidget.columnCount() - 1)
            self.Columns_lineEdit.setText(str(self.tableWidget.columnCount()))
            self.shiftVal()

    def readRow(self):
        """readRow(self) -> None

        Read transform input/output column choices and apply the transform.

        Parameters:
            self (Ui_MainWindow): Active main window UI instance.

        Returns:
            None
        """
        if (int(self.Rows_lineEdit_2.text()) <= int(self.tableWidget.rowCount())) and (
                int(self.Columns_lineEdit_2.text()) <= int(self.tableWidget.columnCount())) and (
                int(self.Rows_lineEdit_2.text()) > 0) and (int(self.Columns_lineEdit_2.text()) > 0):
            # print("Condition True")
            global inputRow
            global outputRow
            inputRow = int(self.Rows_lineEdit_2.text()) - 1
            outputRow = int(self.Columns_lineEdit_2.text()) - 1
            self.readTableRow()
            self.writeTableRow()

    def readTableRow(self):
        """readTableRow(self) -> None

        Readtablerow.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        global xFormula
        global yFormula
        global xTimes
        global yTimes
        global xPlus
        global yPlus
        xFormula = self.comboBox_scale_x.currentText()
        transform, _default_label = self._resolve_function_transform(xFormula)
        xTimes = np.double(self.lineEdit_scale_x_x.text())
        xPlus = np.double(self.lineEdit_scale_x_plus.text())
        try:
            global rowData
            data_rows = self.tableWidget.rowCount() - 1
            rowData = np.array([
                table_item_float(self.tableWidget, row + 1, inputRow)
                for row in range(data_rows)
            ], dtype=float)
            rowData = transform(rowData) * xTimes + xPlus

        except Exception as e:
            self.errMessage("readTableRow:", str(e))

    def writeTableRow(self):
        """writeTableRow(self) -> None

        Writetablerow.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        try:
            for row, value in enumerate(rowData, start=1):
                self.tableWidget.setItem(row, outputRow, QTableWidgetItem(str(np.round(value, 6))))
            input_role = int(tableLabels[inputRow]) if inputRow < len(tableLabels) else 0
            if input_role in {1, 2, 3, 4}:
                input_combo = self.tableWidget.cellWidget(0, inputRow)
                output_combo = self.tableWidget.cellWidget(0, outputRow)
                if input_combo is not None:
                    input_combo.setCurrentIndex(0)
                if output_combo is not None:
                    output_combo.setCurrentIndex(input_role)
                else:
                    self.btn_combobox_changed(input_role, outputRow)
        except Exception as e:
            self.errMessage("writeTableRow:", str(e))

    def btn_LoadData(self):
        """btn_LoadData(self) -> None

        Load a selected dataset file and print values to the table.

        Parameters:
            self (Ui_MainWindow): Active main window UI instance.

        Returns:
            None
        """
        self.file_picker = pick_file_to_append()
        if files:
            try:
                table_data = self._load_table_data(files)
                self.printTOTable(table_data)
            except Exception as e:
                self.errMessage("Loading Data:", str(e))

    def printTOTable(self, table_data):  # Prints data file to table
        """printTOTable(self, table_data) -> None

        Printtotable.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        try:
            global tableDimensions
            global data
            data = np.asarray(table_data)
            tableDimensions = [int(data.shape[0]) + 1, int(data.shape[1])]
            self.tableWidget.setRowCount(data.shape[0] + 1)
            self.tableWidget.setColumnCount(data.shape[1])

            for row in range(data.shape[1]):
                combo = QtWidgets.QComboBox()
                _set_combo_items(combo, AXIS_ROLE_OPTIONS)
                self.tableWidget.setCellWidget(0, row, combo)
            self._wire_role_combos(data.shape[1])
            self._apply_loader_column_roles(data.shape[1])
            for column in range(data.shape[1]):
                for row in range(data.shape[0]):
                    self.tableWidget.setItem(row + 1, column, QTableWidgetItem(str(data[row, column])))
            self.Columns_lineEdit.setText(str(self.tableWidget.columnCount()))
            self.Rows_lineEdit.setText(str(self.tableWidget.rowCount()))

        except Exception as e:
            self.errMessage("Printing to Table:", str(e))

    def btn_combobox_index(self, value):
        """btn_combobox_index(self, value) -> None

        Handle the matching GUI button action.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        global plot_AxisIndex
        plot_AxisIndex = value
        # print("btn_combobox_index:", plot_AxisIndex)

    def btn_combobox_changed(self, value, column=None):
        """btn_combobox_changed(self, value, column) -> None

        Handle the matching GUI button action.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        global combobox_Val
        btn_combobox_Val = value
        if column is None:
            column = plot_AxisIndex
        if value == 1:
            global xIndex
            xIndex = column
        if value == 2:
            global uxIndex
            uxIndex = column
        if value == 3:
            global yIndex
            yIndex = column
        if value == 4:
            global uyIndex
            uyIndex = column
        tableLabels[int(column)] = int(value)

    def _wire_role_combos(self, column_count):
        """_wire_role_combos(self, column_count) -> None

        Wire role combos.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        limit = column_count
        if 'tableLabels' in globals():
            limit = min(column_count, len(tableLabels))
        for column in range(limit):
            combo = self.tableWidget.cellWidget(0, column)
            if combo is not None:
                combo.currentIndexChanged.connect(lambda value, col=column: self.btn_combobox_changed(value, col))

    def btn_ClearTable(self):
        """btn_ClearTable(self) -> None

        Reset table dimensions/content and recreate axis-role combobox headers.

        Parameters:
            self (Ui_MainWindow): Active main window UI instance.

        Returns:
            None
        """

        ##print("Clear Table")
        #    self.Rows_lineEdit.text()
        #    self.Columns_lineEdit.text()
        self.tableWidget.setRowCount(int(self.Rows_lineEdit.text()))
        self.tableWidget.setColumnCount(int(self.Columns_lineEdit.text()))
        global tableLabels
        global tableDimensions
        tableLabels = np.zeros(100)
        tableDimensions = [int(self.Rows_lineEdit.text()), int(self.Columns_lineEdit.text())]

        ##print("tableDimensions set to:", tableDimensions[0],"R, ", tableDimensions[1],"C")
        if self.checkBox_2.isChecked() == True:
            for column in range(int(self.Columns_lineEdit.text())):
                for row in range(1, int(self.Rows_lineEdit.text()) + 1):
                    self.tableWidget.setItem(row, column, QtWidgets.QTableWidgetItem(""))
        for col in range(tableDimensions[1]):
            combo = QtWidgets.QComboBox()
            _set_combo_items(combo, AXIS_ROLE_OPTIONS)
            # self.tableWidget.setItem(data.shape[1], data.shape[0], cellinfo)
            self.tableWidget.setCellWidget(0, col, combo)
        self._wire_role_combos(tableDimensions[1])

    def btn_SaveTable(self):
        """btn_SaveTable(self) -> None

        Read the current table and open the export save-file dialog.

        Parameters:
            self (Ui_MainWindow): Active main window UI instance.

        Returns:
            None
        """
        ##print("Save Table")

        self.readTable()
        self.save_dialog = SaveFile()

    def readTable(self):
        """readTable(self) -> None

        Readtable.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        try:
            global OutPut_Table
            tableDimensions = [int(self.tableWidget.rowCount()), int(self.tableWidget.columnCount())]
            OutPut_Table = np.array([
                [
                    table_item_float(self.tableWidget, row + 1, column)
                    for column in range(tableDimensions[1])
                ]
                for row in range(tableDimensions[0] - 1)
            ], dtype=float)
            # print(OutPut_Table)
        except Exception as e:
            self.errMessage("Reading Table:", str(e))

    def pltConfigWindow(self):
        """pltConfigWindow(self) -> None

        Pltconfigwindow.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        self.Ui_ConfigWindow = QtWidgets.QMainWindow()
        self.ui = Ui_ConfigWindow()
        self.ui.setupUiConfigWindow(self.Ui_ConfigWindow)
        self.ui.owner = self
        self.Ui_ConfigWindow.show()

    def btn_GeneratePlot(self):
        """btn_GeneratePlot(self) -> None

        Validate axis selections and open legacy configuration and plot windows.

        Parameters:
            self (Ui_MainWindow): Active main window UI instance.

        Returns:
            None
        """
        self.readTable()
        try:
            if np.count_nonzero(tableLabels == 1) == 1 and np.count_nonzero(tableLabels == 3) == 1:
                self.pltConfigWindow()
                self.plot_window = Plot_Window(getattr(self, "_main_window", None))
                self.plot_window.show()
            else:
                self.errMessage("The inappropriate combination is selected from the dropdown buttons on the table.",
                                "Possible Solution: Click on 'New Table' button with 'Delete Old Entries' button unchecked and select the proper labels combination.")

        except Exception as e:
            self.errMessage("Generating Plot:", str(e))

    def about_gui_command(self):
        """about_gui_command(self) -> None

        About gui command.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        self.about_window = about_gui()

    def open_home_page(self):
        """open_home_page(self) -> None

        Open home page.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        webbrowser.open('https://physplot.readthedocs.io/', new=2)

    def errMessage(self, Text, InformativeText):
        """errMessage(self, Text, InformativeText) -> None

        Errmessage.

        Parameters:
            See function signature.

        Returns:
            None: Result described by the method name and GUI side effects.
        """
        msgBox = QMessageBox()
        msgBox.setWindowIcon(QtGui.QIcon(str(APP_ICON_PATH)))
        msgBox.setWindowTitle("PhysPlot - Plot Window")
        msgBox.setIcon(QMessageBox.Critical)
        msgBox.setText(Text)
        msgBox.setInformativeText(InformativeText)
        msgBox.setWindowTitle("Warning")
        msgBox.exec_()
