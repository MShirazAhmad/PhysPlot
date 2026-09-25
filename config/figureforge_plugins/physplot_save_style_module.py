"""Figure Editor plugin for saving reusable PhysPlot templates."""

from __future__ import annotations

from matplotlib.figure import Figure
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QFormLayout, QLineEdit, QMessageBox, QVBoxLayout

from physplot_gui.plot_styles import save_style_module, style_path_from_name


class SavePhysPlotStyleModule:
    name = "Save as Template"
    tooltip = "Save the current figure styling as a reusable PhysPlot template."
    submenu = "PhysPlot"

    def run(self, obj):
        figure = obj if isinstance(obj, Figure) else getattr(obj, "figure", None)
        if figure is None:
            self._warn("Select the Figure, an Axes, or an artist from the figure before saving a template.")
            return

        dialog = SaveStyleDialog()
        if dialog.exec() != QDialog.Accepted:
            return

        try:
            name = dialog.name.text().strip()
            path = save_style_module(figure, name)
            QMessageBox.information(None, "PhysPlot Template", f"Saved template:\n{path}")
        except Exception as exc:
            self._warn(str(exc))

    @staticmethod
    def _warn(message):
        box = QMessageBox()
        box.setIcon(QMessageBox.Warning)
        box.setWindowTitle("PhysPlot Template")
        box.setText("Could not save template.")
        box.setInformativeText(message)
        box.exec()


class SaveStyleDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Save as Template")
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.name = QLineEdit("Publication Style")
        self.name.textChanged.connect(self._update_path)
        self.path = QLineEdit()
        self.path.setReadOnly(True)
        form.addRow("Name:", self.name)
        form.addRow("Saved as:", self.path)
        layout.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self._update_path()

    def _update_path(self):
        self.path.setText(str(style_path_from_name(self.name.text())))


SaveStyleDialog.__module__ = __name__ + "._internal"
