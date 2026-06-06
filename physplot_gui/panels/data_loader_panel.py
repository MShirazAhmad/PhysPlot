"""Reusable data loader controls."""

from physplot.qt_compat import QtWidgets


class DataLoaderPanel(QtWidgets.QFrame):
    def __init__(self, actions, show_folder: bool = False, parent=None):
        super().__init__(parent)
        self.setObjectName("Panel")
        self.actions = actions
        layout = QtWidgets.QGridLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setHorizontalSpacing(8)
        layout.setVerticalSpacing(7)
        title = QtWidgets.QLabel("Data Loader")
        title.setObjectName("PanelTitle")
        self.loader = QtWidgets.QComboBox()
        if hasattr(actions, "backend_loader_entries"):
            for entry in actions.backend_loader_entries():
                self.loader.addItem(entry["display_name"], entry)
        elif hasattr(actions, "discover_loader_entries"):
            for entry in actions.discover_loader_entries():
                self.loader.addItem(entry["display_name"], entry)
        else:
            self.loader.addItems(["Auto Loader", "CSV Loader", "Excel Loader", "TXT Loader", "Pandas Data Loader"])
        layout.addWidget(title, 0, 0, 1, 2)
        layout.addWidget(self.loader, 1, 0, 1, 2)
        self.import_button = QtWidgets.QPushButton("Import Data")
        self.import_button.clicked.connect(lambda: actions.import_data(self.loader_id()))
        layout.addWidget(self.import_button, 2, 0)
        if show_folder:
            self.folder_button = QtWidgets.QPushButton("Import Folder")
            self.folder_button.clicked.connect(actions.import_folder)
            layout.addWidget(self.folder_button, 2, 1)
        self.export_button = QtWidgets.QPushButton("Export Data")
        self.export_button.clicked.connect(actions.export_data)
        layout.addWidget(self.export_button, 3, 0)
        self.plot_button = QtWidgets.QPushButton("Update Preview")
        self.plot_button.setProperty("primary", True)
        plot_callback = getattr(actions, "generate_integrated_plot", actions.generate_plot)
        self.plot_button.clicked.connect(plot_callback)
        layout.addWidget(self.plot_button, 3, 1 if show_folder else 0)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)

    def loader_id(self) -> str:
        data = self.loader.currentData()
        if data:
            return data
        text = self.loader.currentText().lower()
        if "csv" in text:
            return "csv"
        if "excel" in text:
            return "excel"
        if "txt" in text:
            return "txt"
        if "pandas" in text:
            return "auto"
        return "auto"
