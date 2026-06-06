"""Mode switching for the lower control area."""

from physplot.qt_compat import QtCore, QtWidgets

from physplot_gui.panels.advanced_mode_panel import AdvancedModePanel
from physplot_gui.panels.simple_mode_panel import SimpleModePanel


class ModeManager(QtCore.QObject):
    mode_changed = QtCore.pyqtSignal(str)

    def __init__(self, actions, parent=None):
        super().__init__(parent)
        self.stack = QtWidgets.QStackedWidget()
        self.stack.setMinimumHeight(138)
        self.stack.setMaximumHeight(152)
        self.panels = {
            "Simple": SimpleModePanel(actions),
            "Advanced": AdvancedModePanel(actions),
        }
        for panel in self.panels.values():
            self.stack.addWidget(panel)

    def set_mode(self, mode: str) -> None:
        panel = self.panels[mode]
        if mode == "Simple":
            self.stack.setMinimumHeight(138)
            self.stack.setMaximumHeight(152)
        else:
            self.stack.setMinimumHeight(300)
            self.stack.setMaximumHeight(430)
        self.stack.setCurrentWidget(panel)
        self.mode_changed.emit(mode)

    def refresh_columns(self, columns: list[str]) -> None:
        for panel in self.panels.values():
            if hasattr(panel, "refresh_columns"):
                panel.refresh_columns(columns)

    def refresh_pipeline(self, rows: list[dict]) -> None:
        for panel in self.panels.values():
            if hasattr(panel, "refresh_pipeline"):
                panel.refresh_pipeline(rows)

    def refresh_timeline(self, rows: list[dict]) -> None:
        panel = self.panels["Advanced"]
        panel.refresh_timeline(rows)

    def set_recording(self, active: bool) -> None:
        panel = self.panels["Advanced"]
        panel.set_recording(active)

    def refresh_plots(self) -> None:
        if hasattr(self.panels["Simple"], "refresh_plotters"):
            self.panels["Simple"].refresh_plotters()
        self.panels["Advanced"].refresh_plot()
