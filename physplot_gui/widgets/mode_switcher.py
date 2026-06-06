"""Top-right mode switcher."""

from physplot.qt_compat import QtCore, QtWidgets


class ModeSwitcher(QtWidgets.QWidget):
    mode_changed = QtCore.pyqtSignal(str)

    MODES = ("Simple", "Advanced")

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        label = QtWidgets.QLabel("Mode:")
        layout.addWidget(label)
        self.buttons: dict[str, QtWidgets.QPushButton] = {}
        for mode in self.MODES:
            button = QtWidgets.QPushButton(mode)
            button.setCheckable(True)
            button.clicked.connect(lambda checked=False, value=mode: self.mode_changed.emit(value))
            self.buttons[mode] = button
            layout.addWidget(button)
        self.set_mode("Simple")

    def set_mode(self, mode: str) -> None:
        for name, button in self.buttons.items():
            active = name == mode
            button.setChecked(active)
            button.setProperty("activeMode", active)
            button.style().unpolish(button)
            button.style().polish(button)
