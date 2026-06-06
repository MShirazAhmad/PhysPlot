"""Plot preview controls."""

from physplot.qt_compat import QtWidgets

from physplot_gui.widgets.plot_canvas import PlotCanvas


class PlotPreviewPanel(QtWidgets.QFrame):
    def __init__(self, actions, include_fit: bool = True, parent=None):
        super().__init__(parent)
        self.setObjectName("Panel")
        self.actions = actions
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)
        title = QtWidgets.QLabel("Plot Preview")
        title.setObjectName("PanelTitle")
        layout.addWidget(title)
        self.mode_tabs = QtWidgets.QTabBar()
        for label in ("Single", "Overlay", "Subplot Grid", "Grouped Subplot"):
            self.mode_tabs.addTab(label)
        self.mode_tabs.currentChanged.connect(lambda _: self.refresh())
        layout.addWidget(self.mode_tabs)
        self.canvas = PlotCanvas()
        layout.addWidget(self.canvas, 1)
        if include_fit:
            controls = QtWidgets.QHBoxLayout()
            self.fit_model = QtWidgets.QComboBox()
            self.fit_model.addItems(["linear"])
            self.fit_button = QtWidgets.QPushButton("Fit")
            self.fit_button.clicked.connect(actions.fit_model)
            self.results_button = QtWidgets.QPushButton("Fit Results")
            self.results_button.clicked.connect(actions.show_fit_results)
            self.show_fit = QtWidgets.QCheckBox("Show Fit")
            self.show_fit.setChecked(True)
            self.show_grid = QtWidgets.QCheckBox("Show Grid")
            self.show_grid.setChecked(True)
            self.show_fit.stateChanged.connect(lambda _: self.refresh())
            self.show_grid.stateChanged.connect(lambda _: self.refresh())
            controls.addWidget(QtWidgets.QLabel("Fit Model:"))
            controls.addWidget(self.fit_model)
            controls.addWidget(self.fit_button)
            controls.addWidget(self.results_button)
            controls.addWidget(self.show_fit)
            controls.addWidget(self.show_grid)
            layout.addLayout(controls)

    def current_plot_mode(self) -> str:
        return self.mode_tabs.tabText(self.mode_tabs.currentIndex())

    def refresh(self) -> None:
        show_fit = getattr(self, "show_fit", None)
        show_grid = getattr(self, "show_grid", None)
        self.canvas.draw_dataset(
            self.actions.state.pp,
            mode=self.current_plot_mode(),
            show_fit=show_fit.isChecked() if show_fit else True,
            show_grid=show_grid.isChecked() if show_grid else True,
        )
