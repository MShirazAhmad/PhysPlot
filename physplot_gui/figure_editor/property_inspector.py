import copy
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QScrollArea,
    QGridLayout,
    QLabel,
    QCheckBox,
    QLineEdit,
    QComboBox,
    QSpinBox,
    QPlainTextEdit,
    QSizePolicy,
)
from PyQt6.QtCore import pyqtSignal as Signal
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtCore import Qt

from physplot_gui.figure_editor.widgets.ff_widgets import (
    ColorButton,
    SpinBox,
    TupleProperty,
    DictProperty,
)
import matplotlib.colors as mcolors
import matplotlib.font_manager as mpl_fm


class PropertyInspector(QWidget):
    propertyChanged = Signal(str, object)

    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(QLabel("Property Inspector"))
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        # PhysPlot: values fit the panel width; no sideways scrolling.
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.content_widget = QWidget()
        # self.scroll_area.setStyleSheet("background-color: #ffffff")
        self.scroll_area.setWidget(self.content_widget)

        self.content_layout = QGridLayout(self.content_widget)
        self.content_layout.setContentsMargins(5, 5, 5, 5)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.content_layout.setHorizontalSpacing(10)
        self.content_layout.setVerticalSpacing(6)
        self.content_layout.setColumnStretch(1, 1)
        self.content_widget.setLayout(self.content_layout)

        layout.addWidget(self.scroll_area)

        self.setLayout(layout)

        property_label = QLabel("Property")
        font = property_label.font()
        font.setBold(True)
        property_label.setFont(font)
        value_label = QLabel("Value")
        value_label.setFont(font)

        self.content_layout.addWidget(property_label, 0, 0)
        self.content_layout.addWidget(value_label, 0, 1)

    def clear_properties(self):
        while self.content_layout.count() > 2:
            item = self.content_layout.takeAt(2)
            if item.widget():
                item.widget().deleteLater()

    def add_property(self, name, value_type, value, value_options=None, types=None):
        row = self.content_layout.rowCount()
        name_label = QLabel(name)
        name_label.setWordWrap(True)
        name_label.setToolTip(f"{name} ({value_type})")
        name_label.setMinimumWidth(80)
        name_label.setMaximumWidth(130)
        self.content_layout.addWidget(name_label, row, 0, Qt.AlignmentFlag.AlignVCenter)

        if value_type == "bool":
            value_widget = QCheckBox()
            try:
                value_widget.setChecked(value)
            except TypeError:
                value_widget.setChecked(False)
            value_widget.stateChanged.connect(
                lambda n=name, w=value_widget: self.on_value_changed(n, w)
            )
            self._add_value(value_widget, name, row)
        elif value_type == "string":
            value_widget = QLineEdit()
            value_widget.setText(value)
            value_widget.textChanged.connect(
                lambda n=name, w=value_widget: self.on_value_changed(n, w)
            )
            self._add_value(value_widget, name, row)
        elif value_type == "multiline":
            value_widget = QPlainTextEdit()
            # PhysPlot: a few lines tall, so the other properties stay in view.
            value_widget.setMaximumHeight(72)
            value_widget.setPlainText(value)
            value_widget.textChanged.connect(
                lambda n=name, w=value_widget: self.on_value_changed(n, w)
            )
            self._add_value(value_widget, name, row)
        elif value_type == "choice":
            value_widget = QComboBox()
            value_widget.addItems(value_options)
            if isinstance(value, list):
                value = value[0]
            value_widget.setCurrentText(str(value))
            value_widget.currentTextChanged.connect(
                lambda n=name, w=value_widget: self.on_value_changed(n, w)
            )
            self._add_value(value_widget, name, row)
        elif value_type == "color":
            c = mcolors.to_hex(value)
            value_widget = ColorButton(initial_color=QColor(c))
            value_widget.colorChanged.connect(
                lambda n=name, w=value_widget: self.on_value_changed(n, w)
            )
            self._add_value(value_widget, name, row)
        elif value_type == "float":
            value_widget = SpinBox()
            # PhysPlot: show the current value (upstream left every number at 0.0).
            try:
                value_widget.setValue(float(value if not isinstance(value, (list, tuple)) else value[0]))
            except (TypeError, ValueError):
                pass
            value_widget.valueChanged.connect(
                lambda n=name, w=value_widget: self.on_value_changed(n, w)
            )
            self._add_value(value_widget, name, row)
        elif value_type == "int":
            value_widget = QSpinBox()
            value_widget.setMinimum(-999999999)
            value_widget.setMaximum(999999999)
            try:
                value_widget.setValue(value)
            except TypeError:
                value_widget.setValue(0)
            value_widget.valueChanged.connect(
                lambda n=name, w=value_widget: self.on_value_changed(n, w)
            )
            self._add_value(value_widget, name, row)
        elif value_type == "tuple":
            value_widget = TupleProperty(types=types, values=value)
            value_widget.valueChanged.connect(
                lambda n=name, w=value_widget: self.on_value_changed(n, w)
            )
            self._add_value(value_widget, name, row)
        elif value_type == "dict":
            value_widget = DictProperty(types=types, values=value)
            value_widget.valueChanged.connect(
                lambda n=name, w=value_widget: self.on_value_changed(n, w)
            )
            self._add_value(value_widget, name, row)
        elif value_type == "font":
            value_widget = QComboBox()
            font_names = sorted(set(f.name for f in mpl_fm.fontManager.ttflist))
            for font_name in font_names:
                value_widget.addItem(font_name)
                font = QFont(font_name)
                value_widget.setItemData(value_widget.count() - 1, font, Qt.ItemDataRole.FontRole)
            value_widget.setCurrentText(value)
            value_widget.currentTextChanged.connect(
                lambda n=name, w=value_widget: self.on_value_changed(n, w)
            )
            self._add_value(value_widget, name, row)

    def _add_value(self, widget, name, row):
        """PhysPlot: place a value widget, stretched to the panel width, and tag its name."""
        widget._property_name = name
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, widget.sizePolicy().verticalPolicy())
        widget.setMinimumWidth(0)
        self.content_layout.addWidget(widget, row, 1)

    def on_value_changed(self, name, widget):
        if widget.__class__.__name__ == "QCheckBox":
            value = widget.isChecked()
        elif widget.__class__.__name__ == "QComboBox":
            value = widget.currentText()
        elif widget.__class__.__name__ == "QLineEdit":
            value = widget.text()
        elif widget.__class__.__name__ == "QPlainTextEdit":
            value = widget.toPlainText()
        elif widget.__class__.__name__ == "SpinBox":
            value = widget.value()
        elif widget.__class__.__name__ == "ColorButton":
            value = widget.color.getRgbF()
        elif widget.__class__.__name__ == "QSpinBox":
            value = widget.value()
        elif widget.__class__.__name__ == "TupleProperty":
            value = widget.get_values()
        elif widget.__class__.__name__ == "DictProperty":
            value = widget.get_values()
        else:
            value = None

        self.propertyChanged.emit(widget._property_name, value)
