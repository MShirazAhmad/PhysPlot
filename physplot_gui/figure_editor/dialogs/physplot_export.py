"""PhysPlot export dialogs for the Figure Editor.

* :class:`ExportFigureDialog` saves the figure as an image or vector file in a chosen
  format, optionally with a different PhysPlot template (formatting) applied to the
  exported copy only, with a live preview.
* :func:`export_style` saves only the figure's formatting as a PhysPlot template.
"""

from __future__ import annotations

import io
import pickle
from pathlib import Path

from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtGui import QDesktopServices, QPixmap
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from physplot_gui.plot_styles import (
    apply_style_module,
    list_style_modules,
    save_style_module,
    style_path_from_name,
)

#: Export formats offered, as (menu label, file extension).
EXPORT_FORMATS = [
    ("PNG image", "png"),
    ("PDF document", "pdf"),
    ("SVG vector image", "svg"),
    ("EPS (PostScript)", "eps"),
    ("TIFF image", "tiff"),
    ("JPEG image", "jpg"),
]
AS_SHOWN = "As shown"


def figure_copy(figure):
    """Return an independent copy of ``figure`` (the on-screen figure is never changed)."""
    return pickle.loads(pickle.dumps(figure))


def render_export(figure, path, fmt: str, dpi: int, size_inches, transparent: bool, template_path=None) -> Path:
    """Save a copy of ``figure`` to ``path`` with the given options and optional template.

    :param template_path: A PhysPlot template JSON file applied to the copy, or ``None``
        to export the figure as shown.
    :returns: The written file.
    """
    copy = figure_copy(figure)
    if template_path:
        apply_style_module(copy, template_path)
    if size_inches:
        copy.set_size_inches(size_inches)
    path = Path(path)
    if path.suffix.lower().lstrip(".") != fmt:
        path = path.with_suffix(f".{fmt}")
    path.parent.mkdir(parents=True, exist_ok=True)
    copy.savefig(path, format=fmt, dpi=dpi, transparent=transparent, bbox_inches="tight")
    return path


class ExportFigureDialog(QDialog):
    """Export the figure in a chosen format, with the formatting as shown or a template."""

    def __init__(self, figure, preferences=None, parent=None, start_dir=None):
        super().__init__(parent)
        self.setWindowTitle("Export Figure")
        self.figure = figure
        self.preferences = preferences
        self.exported_path = None
        last = (preferences.get("last_export_path") if preferences else "") or ""
        default_dir = Path(last).parent if last else Path(start_dir or Path.home() / "Documents")
        self.templates = list_style_modules()

        self.format_combo = QComboBox()
        for label, ext in EXPORT_FORMATS:
            self.format_combo.addItem(f"{label} (.{ext})", ext)
        self.style_combo = QComboBox()
        self.style_combo.addItem(AS_SHOWN, None)
        for entry in self.templates:
            self.style_combo.addItem(entry["name"], entry["path"])
        self.dpi_spin = QSpinBox()
        self.dpi_spin.setRange(50, 1200)
        self.dpi_spin.setValue(300)
        width, height = figure.get_size_inches()
        self.width_spin = QDoubleSpinBox()
        self.height_spin = QDoubleSpinBox()
        for spin, value in ((self.width_spin, width), (self.height_spin, height)):
            spin.setRange(0.5, 50)
            spin.setDecimals(2)
            spin.setSingleStep(0.25)
            spin.setSuffix(" in")
            spin.setValue(float(value))
        self.transparent_check = QCheckBox("Transparent background")
        self.open_check = QCheckBox("Open the file after export")
        self.path_edit = QLineEdit(str(default_dir / "figure.png"))
        browse = QPushButton("Browse…")
        browse.clicked.connect(self.browse)

        form = QFormLayout()
        form.addRow("Format:", self.format_combo)
        form.addRow("Formatting:", self.style_combo)
        form.addRow("DPI:", self.dpi_spin)
        size_row = QHBoxLayout()
        size_row.addWidget(self.width_spin)
        size_row.addWidget(QLabel("×"))
        size_row.addWidget(self.height_spin)
        form.addRow("Size:", size_row)
        form.addRow("", self.transparent_check)
        path_row = QHBoxLayout()
        path_row.addWidget(self.path_edit)
        path_row.addWidget(browse)
        form.addRow("Save to:", path_row)
        form.addRow("", self.open_check)
        options = QWidget()
        options_layout = QVBoxLayout(options)
        options_layout.addLayout(form)
        options_layout.addStretch()
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
        export_button = buttons.addButton("Export", QDialogButtonBox.ButtonRole.AcceptRole)
        export_button.setDefault(True)
        buttons.accepted.connect(self.export)
        buttons.rejected.connect(self.reject)
        options_layout.addWidget(buttons)
        options.setFixedWidth(380)

        self.preview = QLabel()
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview.setMinimumSize(420, 360)
        self.preview.setStyleSheet("background: #ffffff; border: 1px solid #d8d8d8;")

        layout = QHBoxLayout(self)
        layout.addWidget(options)
        layout.addWidget(self.preview, 1)

        self.format_combo.currentIndexChanged.connect(self._format_changed)
        for signal in (
            self.style_combo.currentIndexChanged,
            self.width_spin.valueChanged,
            self.height_spin.valueChanged,
            self.transparent_check.toggled,
        ):
            signal.connect(self.update_preview)
        self.update_preview()

    def current_format(self) -> str:
        return self.format_combo.currentData()

    def _format_changed(self):
        path = Path(self.path_edit.text() or "figure")
        self.path_edit.setText(str(path.with_suffix(f".{self.current_format()}")))
        self.dpi_spin.setEnabled(self.current_format() not in {"svg", "pdf", "eps"} or True)

    def browse(self):
        fmt = self.current_format()
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Figure", self.path_edit.text(), f"{fmt.upper()} files (*.{fmt})"
        )
        if path:
            self.path_edit.setText(path)

    def update_preview(self):
        """Render the export copy (with the chosen formatting) into the preview."""
        try:
            copy = figure_copy(self.figure)
            if self.style_combo.currentData():
                apply_style_module(copy, self.style_combo.currentData())
            copy.set_size_inches((self.width_spin.value(), self.height_spin.value()))
            buffer = io.BytesIO()
            copy.savefig(buffer, format="png", dpi=80, transparent=self.transparent_check.isChecked(), bbox_inches="tight")
            pixmap = QPixmap()
            pixmap.loadFromData(buffer.getvalue())
            self.preview.setPixmap(
                pixmap.scaled(
                    self.preview.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        except Exception as exc:  # the preview must never block the export
            self.preview.setText(f"No preview: {exc}")

    def export(self):
        try:
            self.exported_path = render_export(
                self.figure,
                self.path_edit.text(),
                self.current_format(),
                self.dpi_spin.value(),
                (self.width_spin.value(), self.height_spin.value()),
                self.transparent_check.isChecked(),
                self.style_combo.currentData(),
            )
        except Exception as exc:
            QMessageBox.warning(self, "Export Figure", f"Could not export the figure:\n{exc}")
            return
        if self.preferences:
            self.preferences.set("last_export_path", str(self.exported_path))
        if self.open_check.isChecked():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.exported_path)))
        self.accept()


def export_style(figure, parent=None) -> Path | None:
    """Ask for a name and save only the figure's formatting as a PhysPlot template.

    The template lands in the PhysPlot templates folder (so it appears in the
    **Template** dropdown after *Reload*), unless the user picks another file.

    :returns: The written template file, or ``None`` when cancelled.
    """
    name, ok = QInputDialog.getText(parent, "Export Style", "Template name:", text="My Style")
    if not ok or not name.strip():
        return None
    suggested = style_path_from_name(name)
    path, _ = QFileDialog.getSaveFileName(parent, "Export Style", str(suggested), "PhysPlot template (*.json)")
    if not path:
        return None
    if not path.lower().endswith(".json"):
        path += ".json"
    try:
        written = save_style_module(figure, name.strip(), path)
    except Exception as exc:
        QMessageBox.warning(parent, "Export Style", f"Could not export the style:\n{exc}")
        return None
    QMessageBox.information(
        parent,
        "Export Style",
        f"Saved the formatting as “{name.strip()}”:\n{written}\n\n"
        "Choose it under Template in PhysPlot (click Reload first) to apply it to other plots.",
    )
    return written
