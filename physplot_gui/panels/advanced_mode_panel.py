"""Advanced mode controls."""

from physplot.qt_compat import QtWidgets

from .recorder_mode_panel import RecorderModePanel, SequenceTablePanel


class AdvancedModePanel(QtWidgets.QWidget):
    def __init__(self, actions, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 8)
        layout.setSpacing(6)
        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.addTab(self._protocol_tab(actions), "Build Protocol")
        self.recorder = RecorderModePanel(actions)
        self.tabs.addTab(self.recorder, "Run Sequence")
        layout.addWidget(self.tabs)

    def _protocol_tab(self, actions):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.sequence_builder = SequenceTablePanel(
            actions,
            title="Protocol Sequence from Simple Mode",
            show_buttons=False,
        )
        layout.addWidget(self.sequence_builder, 1)
        return widget

    def refresh_columns(self, columns: list[str]) -> None:
        return None

    def refresh_pipeline(self, rows: list[dict]) -> None:
        return None

    def refresh_timeline(self, rows: list[dict]) -> None:
        self.sequence_builder.refresh_timeline(rows)
        self.recorder.refresh_timeline(rows)

    def set_recording(self, active: bool) -> None:
        self.sequence_builder.set_tracking(True)
        self.recorder.set_recording(active)

    def refresh_plot(self) -> None:
        return None

    def current_plot_mode(self) -> str:
        return "Sequence"
