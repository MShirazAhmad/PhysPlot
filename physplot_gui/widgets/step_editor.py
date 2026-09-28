"""Dialog that edits workflow steps from their ``describe()`` field specs.

The dialog knows nothing about individual step classes. Each step supplies
its editable fields through ``WorkflowStep.describe()`` and converts edited
values back with ``WorkflowStep.validate()``; see ``physplot.steps.fields``.
One table row can hold several steps (for example Load Data plus its role
setup), so the dialog shows one group per step.
"""

from __future__ import annotations

from physplot.qt_compat import QtWidgets
from physplot.steps.fields import field_label, format_field


class StepEditorDialog(QtWidgets.QDialog):
    def __init__(self, steps, columns=(), parent=None, title: str = "Edit Step"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(560)
        self.steps = list(steps)
        self.columns = [str(column) for column in columns]
        self.widgets: list[dict[str, QtWidgets.QWidget]] = []
        self._getters: list[dict[str, object]] = []
        self.result_values: list[dict] | None = None

        layout = QtWidgets.QVBoxLayout(self)
        for step in self.steps:
            layout.addWidget(self._step_group(step))

        self.error_label = QtWidgets.QLabel("")
        self.error_label.setObjectName("StepEditorError")
        self.error_label.setStyleSheet("color:#d21f2b;font-weight:600;")
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        layout.addWidget(self.error_label)

        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._try_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    # -- Public API --------------------------------------------------------

    def raw_values(self) -> list[dict]:
        """Return the current widget contents for each step, unvalidated."""
        return [{name: getter() for name, getter in getters.items()} for getters in self._getters]

    def validated_values(self) -> list[dict]:
        """Return converted values for each step or raise ``ValueError``."""
        values = []
        for step, raw in zip(self.steps, self.raw_values()):
            try:
                values.append(step.validate(**raw))
            except ValueError as exc:
                raise ValueError(f"{step.step_label()}: {exc}") from None
        return values

    # -- Construction ------------------------------------------------------

    def _step_group(self, step) -> QtWidgets.QGroupBox:
        group = QtWidgets.QGroupBox(step.step_label())
        form = QtWidgets.QFormLayout(group)
        form.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        widgets: dict[str, QtWidgets.QWidget] = {}
        getters: dict[str, object] = {}
        specs = step.describe()
        for name, spec in specs.items():
            widget, getter = self._field_widget(spec)
            if spec.get("help"):
                widget.setToolTip(spec["help"])
            label = field_label(name, spec)
            if not spec.get("optional") and spec.get("type") != "bool":
                label = f"{label} *"
            form.addRow(label, widget)
            widgets[name] = widget
            getters[name] = getter
        self._link_column_numbers(specs, widgets)
        self.widgets.append(widgets)
        self._getters.append(getters)
        return group

    def _field_widget(self, spec: dict):
        kind = spec.get("type", "str")
        value = spec.get("value")
        if kind == "bool":
            widget = QtWidgets.QCheckBox()
            widget.setChecked(bool(value))
            return widget, widget.isChecked
        if kind in {"column", "choice"}:
            widget = QtWidgets.QComboBox()
            widget.setEditable(kind == "column" or bool(spec.get("editable")))
            items = list(self.columns) if kind == "column" else [str(choice) for choice in spec.get("choices", [])]
            if spec.get("optional"):
                items.insert(0, "")
            current = "" if value is None else str(value)
            if current not in items:
                items.append(current)
            widget.addItems(items)
            widget.setCurrentText(current)
            return widget, widget.currentText
        if kind == "path":
            container = QtWidgets.QWidget()
            row = QtWidgets.QHBoxLayout(container)
            row.setContentsMargins(0, 0, 0, 0)
            edit = QtWidgets.QLineEdit(format_field(spec))
            browse = QtWidgets.QPushButton("Browse...")
            browse.clicked.connect(lambda: self._browse_path(edit))
            row.addWidget(edit, 1)
            row.addWidget(browse)
            container.line_edit = edit
            return container, edit.text
        widget = QtWidgets.QLineEdit(format_field(spec))
        if kind == "literal":
            widget.setPlaceholderText("{}" if spec.get("python_type") is dict else "[]")
        return widget, widget.text

    def _link_column_numbers(self, specs: dict, widgets: dict) -> None:
        """Keep a column's number-fallback field in step with the chosen column."""
        for name, spec in specs.items():
            number_name = spec.get("number_field")
            if spec.get("type") != "column" or number_name not in widgets:
                continue
            combo = widgets[name]
            number_edit = widgets[number_name]
            if not isinstance(number_edit, QtWidgets.QLineEdit):
                continue

            def update_number(text, edit=number_edit):
                if text in self.columns:
                    edit.setText(str(self.columns.index(text) + 1))

            combo.currentTextChanged.connect(update_number)

    def _browse_path(self, edit: QtWidgets.QLineEdit) -> None:
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Choose File", edit.text() or "")
        if path:
            edit.setText(path)

    def _try_accept(self) -> None:
        try:
            self.result_values = self.validated_values()
        except ValueError as exc:
            self.error_label.setText(str(exc))
            self.error_label.show()
            return
        self.error_label.hide()
        self.accept()


def choose_step_type(parent, step_types) -> type | None:
    """Ask which kind of step to insert; return the class or ``None``."""
    labels = [step_type.step_label() for step_type in step_types]
    label, accepted = QtWidgets.QInputDialog.getItem(parent, "Insert Step", "Step type:", labels, 0, False)
    if not accepted:
        return None
    return step_types[labels.index(label)]


__all__ = ["StepEditorDialog", "choose_step_type"]
