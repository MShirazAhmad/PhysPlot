"""Mode switching for the lower control area.

The PhysPlot window stacks, from top to bottom: the branded header, the central table, the
*lower control area* and the status bar. :class:`ModeManager` owns that lower area, a
``QStackedWidget`` holding one panel per GUI mode:

* ``"Simple"``: :class:`~physplot_gui.panels.simple_mode_panel.SimpleModePanel`, the three
  side-by-side panels **Data Importer**, **Transformation** and **Plotter Module**.
* ``"Advanced"``: :class:`~physplot_gui.panels.advanced_mode_panel.AdvancedModePanel`, the
  **Build Protocol** and **Run Sequence** tabs.

Only one panel is visible at a time; the central table above stays in place, so switching
modes never hides the data. Both panels are created once, at start-up, and keep their state
while hidden.

Heights: in Simple mode the stack is fixed to exactly the height the three panels need, so
the table gets all remaining space and the controls never overlap. Whenever that height
changes (the panels are restyled or their contents change, or a horizontal scroll bar
appears on a narrow window) the Simple panel emits ``height_changed`` and the stack is
re-fitted, as long as Simple mode is showing. In Advanced mode the stack may be between
300 and 430 px tall, leaving room for the sequence table.

The main window forwards data refreshes through the ``refresh_*`` methods, which hand them
to whichever panels support them, so the hidden panel is up to date when the user switches.
"""

from physplot.qt_compat import QtCore, QtWidgets

from physplot_gui.panels.advanced_mode_panel import AdvancedModePanel
from physplot_gui.panels.simple_mode_panel import SimpleModePanel


class ModeManager(QtCore.QObject):
    """Own the Simple and Advanced panels and switch between them.

    ``ModeManager`` is a ``QObject``, not a widget; the main window adds :attr:`stack` to
    its layout below the central table.

    Signals:

    * ``mode_changed(str mode)``: emitted by :meth:`set_mode` after the requested panel is
      shown. ``MainWindow._mode_changed`` stores the mode in the GUI state, updates the
      header's mode switcher, resets the status message and refreshes the panels.

    :ivar stack: The ``QStackedWidget`` placed in the window below the central table.
    :ivar panels: Mapping of mode name (``"Simple"``, ``"Advanced"``) to its panel.
    """
    mode_changed = QtCore.pyqtSignal(str)

    def __init__(self, actions, parent=None):
        """Create both mode panels, stack them, and fit the stack to Simple mode.

        Simple mode's panel is the first page of the stack, so it is shown at start-up.

        :param actions: The object the panels call back into for every user action; the
            main window passes itself.
        :param parent: Optional Qt parent object.
        """
        super().__init__(parent)
        self.stack = QtWidgets.QStackedWidget()
        self.panels = {
            "Simple": SimpleModePanel(actions),
            "Advanced": AdvancedModePanel(actions),
        }
        for panel in self.panels.values():
            self.stack.addWidget(panel)
        self.panels["Simple"].height_changed.connect(self._refit_simple)
        self._fit_stack_to("Simple")

    def _refit_simple(self) -> None:
        """Re-fit the stack when the Simple panel's height changes, if Simple is showing.

        Connected to ``SimpleModePanel.height_changed``. While Advanced mode is shown the
        change is ignored; the height is fitted again when Simple mode is selected.
        """
        if self.stack.currentWidget() is self.panels["Simple"]:
            self._fit_stack_to("Simple")

    def set_mode(self, mode: str) -> None:
        """Show the panel for ``mode`` and emit :attr:`mode_changed`.

        The stack is resized for the new mode before the panel is shown. Called by the
        header's mode switcher buttons and by *View > Simple Mode* (``Ctrl+1``) and
        *View > Advanced Mode* (``Ctrl+2``).

        :param mode: ``"Simple"`` or ``"Advanced"``.
        :raises KeyError: If ``mode`` is not one of those names.
        """
        panel = self.panels[mode]
        self._fit_stack_to(mode)
        self.stack.setCurrentWidget(panel)
        self.mode_changed.emit(mode)

    def _fit_stack_to(self, mode: str) -> None:
        """Size the lower area to the active panel so controls never overlap.

        Simple Mode is compact and takes exactly the height its three panels
        need; Advanced Mode keeps a taller, bounded area for the sequence table.

        For ``"Simple"`` the stack's minimum and maximum heights are both set to the
        Simple panel's size-hint height (its fitted height). For any other mode the
        stack's height is bounded to 300 to 430 px.

        :param mode: The mode being shown.
        """
        if mode == "Simple":
            height = self.panels["Simple"].sizeHint().height()
            self.stack.setMinimumHeight(height)
            self.stack.setMaximumHeight(height)
        else:
            self.stack.setMinimumHeight(300)
            self.stack.setMaximumHeight(430)

    def refresh_columns(self, columns: list[str]) -> None:
        """Pass the table's column names to every panel that lists columns.

        :param columns: Column names in table order (from ``CentralTable.column_names``).
        """
        for panel in self.panels.values():
            if hasattr(panel, "refresh_columns"):
                panel.refresh_columns(columns)

    def refresh_pipeline(self, rows: list[dict]) -> None:
        """Pass the transformation pipeline rows to every panel that shows them.

        :param rows: The ``GuiState.transformations`` display rows.
        """
        for panel in self.panels.values():
            if hasattr(panel, "refresh_pipeline"):
                panel.refresh_pipeline(rows)

    def refresh_timeline(self, rows: list[dict]) -> None:
        """Show the protocol sequence rows in the Advanced panel.

        :param rows: The ``GuiState.timeline`` rows, one per recorded action.
        """
        panel = self.panels["Advanced"]
        panel.refresh_timeline(rows)

    def set_recording(self, active: bool) -> None:
        """Pass the backend's recording flag to the Advanced panel.

        :param active: Whether the backend is currently recording.
        """
        panel = self.panels["Advanced"]
        panel.set_recording(active)

    def refresh_plots(self) -> None:
        """Refresh the plot-related controls of both panels.

        The Simple panel re-lists its plotters (if it supports that) and the Advanced
        panel's ``refresh_plot`` is called.
        """
        if hasattr(self.panels["Simple"], "refresh_plotters"):
            self.panels["Simple"].refresh_plotters()
        self.panels["Advanced"].refresh_plot()
