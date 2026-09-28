from PyQt6.QtWidgets import (
    QPushButton,
    QColorDialog,
)
from PyQt6.QtCore import pyqtSignal as Signal
from PyQt6.QtGui import QColor


class ColorButton(QPushButton):
    colorChanged = Signal(QColor)

    def __init__(self, initial_color=None, parent=None):
        super().__init__(parent)
        self.setText("Choose Color")
        self.color = initial_color if initial_color else QColor(255, 255, 255)
        self.setObjectName("color_button")
        self.update_button_color()

        self.clicked.connect(self.open_color_dialog)

    def open_color_dialog(self):
        color = QColorDialog.getColor(self.color, self, "Select Color")

        if color.isValid():
            self.color = color
            self.update_button_color()
            self.colorChanged.emit(self.color)  # Emit the signal

    def update_button_color(self):
        # PhysPlot: label text in black or white, whichever reads on the swatch, and the
        # hex code instead of "Choose Color".
        text = "#000000" if self.color.lightnessF() > 0.55 else "#ffffff"
        self.setText(self.color.name())
        self.setStyleSheet(
            f"#color_button {{ background-color: {self.color.name()}; color: {text}; }}"
        )
