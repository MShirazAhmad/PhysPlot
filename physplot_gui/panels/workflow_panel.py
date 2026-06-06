"""Workflow controls shared by modes."""

from physplot.qt_compat import QtWidgets


class WorkflowPanel(QtWidgets.QFrame):
    def __init__(self, actions, recorder: bool = False, parent=None):
        super().__init__(parent)
        self.setObjectName("Panel")
        self.actions = actions
        self.recorder = recorder
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)
        title = QtWidgets.QLabel("Sequence Controls" if recorder else "Sequence")
        title.setObjectName("PanelTitle")
        layout.addWidget(title)
        self.recording_label = QtWidgets.QLabel("Recording: OFF")
        if recorder:
            self.recording_label.setText("Tracking: ON")
            self.recording_label.setStyleSheet("color:#12823b;font-weight:700;")
            layout.addWidget(self.recording_label)
            save_text = "Save Sequence.py"
        else:
            self.recording_label.setText("Recording: OFF")
            save_text = "Save Sequence.py"
            if hasattr(actions, "toggle_recording"):
                layout.addWidget(self.recording_label)
        self.save_button = QtWidgets.QPushButton(save_text)
        self.save_button.clicked.connect(actions.save_workflow)
        layout.addWidget(self.save_button)
        self.open_button = QtWidgets.QPushButton("Load Sequence.py")
        self.open_button.clicked.connect(actions.open_workflow)
        layout.addWidget(self.open_button)
        self.run_button = QtWidgets.QPushButton("Run Sequence.py")
        self.run_button.clicked.connect(actions.run_workflow)
        layout.addWidget(self.run_button)
        self.manager_button = QtWidgets.QPushButton("Workflow Manager")
        self.manager_button.clicked.connect(actions.workflow_manager)
        layout.addWidget(self.manager_button)
        layout.addStretch(1)

    def set_recording(self, active: bool) -> None:
        color = "#12823b"
        text = "Tracking: ON"
        self.recording_label.setText(text)
        self.recording_label.setStyleSheet(f"color:{color};font-weight:700;")
