"""Build the three-section Simple Mode controls shown under the central table.

Simple Mode is the default, everyday view of the PhysPlot GUI. It sits directly
below the central spreadsheet, which keeps the table-first layout, and holds
exactly three panels, left to right: **1. Data Importer**, **2. Mathematical
Transformation** and **3. Plotter Module**. The panels contain no scientific
logic. Every control forwards to a method of the ``actions`` object, which is
the :class:`~physplot_gui.app.main_window.MainWindow`. The window calls the
backend ``physplot`` API, updates the table, and records the action as a row of
the replayable protocol that Advanced Mode > **Build Protocol** lists.

The user documentation shows the same controls with screenshots: see the
*GUI Walkthrough* (``docs/getting_started.rst`` and ``wiki/GUI-Walkthrough.md``)
and the *UI Reference* wiki (``wiki/UI-Reference.md``, pages
``wiki/UI-Data-Importer.md``, ``wiki/UI-Mathematical-Transformation.md`` and
``wiki/UI-Plotter-Module.md``).

.. rubric:: Layout

The three panels share one horizontal row with stretch factors 4 : 5 : 12::

    +- 1. Data Importer -+ +- 2. Mathematical Transformation -+ +- 3. Plotter Module ---------+
    |    (stretch 4)     | |           (stretch 5)            | |        (stretch 12)         |
    +--------------------+ +----------------------------------+ +-----------------------------+

Panel **1. Data Importer**::

    +- 1. Data Importer --------------------+
    | Data Loader:   [Auto Loader        v] |
    | [Import Data]  [Import Folder       ] |
    | [Export Data]                         |
    +---------------------------------------+

Panel **2. Mathematical Transformation** (**Apply** spans both rows)::

    +- 2. Mathematical Transformation ------------------------------------------+
    | Input:  [2: Intensity v]  Function: [identity    v]  +  [0     ]  [     ] |
    | Output: [Output column                                        v]  [Apply] |
    +---------------------------------------------------------------------------+

Panel **3. Plotter Module** (left column: what to plot; right column: the
optional least-squares fit)::

    +- 3. Plotter Module --------------------------------------------------------------+
    | Plotter Module: [Basic Plotter v]    Fit Function:     [ ] LSQ fit [a*x + b    ] |
    | Plot Type:      [scatter       v]    Params / Initial: [a,b     ] [1,0         ] |
    | Template:       [None v] [Reload]    Fit Style:        [Default v] [Reload]      |
    | [Generate Plot] [Export Plot]        Fit Line:  [label   ] [-- v] [2] [x] Legend |
    +----------------------------------------------------------------------------------+

.. rubric:: 1. Data Importer

**Data Loader:** (``loader``, an :class:`AutoWidthComboBox`)
    Choose how the next file is read. The list comes from
    ``MainWindow.backend_loader_entries``: the backend loaders (for example
    *Auto Loader*, *CSV Loader*, *TXT Loader*, *Excel Loader*,
    *Nanoindentation Loader*, *XRDML Loader (Panalytical XRD)* and
    *DataFrame Loader*) followed by personal loader plugins found in
    ``config/data_importers/``. Each item stores its loader entry ``dict`` as
    item data. Entries whose ``enabled`` flag is false (the DataFrame Loader)
    are drawn grey (``#94a3b8``) and cannot be selected.

**Import Data** (push button)
    Calls ``MainWindow.import_data`` with the selected loader entry, or
    ``"auto"`` when no entry is selected. The window opens an *Import Data*
    file dialog (built-in types, loader-plugin types such as ``.ras``, or all files).
    A backend loader reads the file through ``PhysPlot.load`` and applies the
    dataset's suggested column roles. A loader plugin's ``load_data(path)`` is
    called instead; its columns are named from ``COLUMN_NAMES`` or the returned
    DataFrame's headers (missing names become ``Column N``) and its
    ``DEFAULT_COLUMN_ROLES`` are applied. The
    table is replaced by the new data and one **File Loader** protocol row is
    recorded that holds a ``LoadDataStep`` plus, when any column has a role
    other than *Ignore*, a ``SetRoleStep``. The status bar shows ``Ready``; an
    error shows the *Import failed* warning.

**Import Folder** (push button)
    Calls ``MainWindow.import_folder``, which opens a folder chooser and only
    reports ``Folder selected: <name>`` in the status bar. No data is loaded
    and nothing is recorded; folders are processed from Advanced Mode >
    **Run Sequence**.

**Export Data** (push button)
    Calls ``MainWindow.export_data``. The table is synced to the backend, a
    folder is chosen, and ``PhysPlot.export`` writes ``data.csv``,
    ``columns.csv`` and ``workflow.py`` plus ``fit.json`` and ``plot.png``
    when a fit result or figure exists. The status bar shows ``Exported``.
    Exporting is not recorded in the protocol.

.. rubric:: 2. Mathematical Transformation

**Input:** (``input_column``, :class:`AutoWidthComboBox`)
    The column to transform. Items are labelled ``Column N`` for default
    column names and ``N: name`` for real names; the item data is the real
    column name. When new data is loaded, the column with the **Y** role is
    selected automatically.

**Function:** (``function``, :class:`AutoWidthComboBox`)
    The transformation. Entries come from ``MainWindow.simple_function_entries``:
    ``identity`` and the backend built-ins (``normalize_max``, ``multiply``,
    ``add``, ``subtract``, ``divide``, ``log``, ``log10`` and
    ``baseline_subtract``, shown as ``subtract first value``), then every
    plugin in ``config/transformations/``. Hovering an item shows its
    description: built-ins use the text in ``BUILTIN_FUNCTIONS``
    (``physplot_gui/app/main_window.py``); plugins use the first line of the
    plugin module's docstring followed by the file name. The closed box's
    tooltip shows the selected entry's description.

**+** (``offset``, line edit, default ``0``)
    A number added to the result. Text that is not a number counts as ``0``.

**Output:** (``output_column``, editable :class:`AutoWidthComboBox`)
    Pick an existing column to overwrite it, or type a new column name
    (placeholder *Output column*). Typed names are not added to the list.
    When left blank the window names the output ``<input>_<function>``.

**Apply** (push button)
    Calls ``MainWindow.apply_backend_transform`` with the input column, the
    function entry, a fixed multiplier of ``1.0``, the offset and the output
    name. If the input column is empty the status bar says *Enter or import
    data before applying a transformation* and nothing happens. Otherwise
    the backend ``PhysPlot.transform`` adds or overwrites the output column
    and records a ``TransformColumnStep``, shown as a **Transform** row with
    ``input -> output`` as its target:

    - ``add`` and ``subtract`` use the offset as their value;
    - ``identity`` runs as ``multiply`` with factor ``1.0``; ``multiply`` and
      ``divide`` use ``1.0`` (the factor can be edited in the protocol Code
      view);
    - for the other built-ins a non-zero offset is applied by a second
      ``add`` step on the output column, recorded as its own row;
    - a plugin runs as ``transform(values) * multiplier + offset`` in one
      step recorded under the plugin's file name, with the plugin's display
      name in the row's details.

    The status bar shows *Transformation applied*; an error shows the
    *Transformation failed* warning.

.. rubric:: 3. Plotter Module

**Plotter Module:** (``plotter``, :class:`AutoWidthComboBox`)
    The plotter to render with. Entries come from ``MainWindow.plotter_entries``:
    the backend ``PlotterRegistry`` plotters available for the current data
    (for example *Basic Plotter*, *Histogram Plotter*, *Scatter Plotter*,
    *Error Bar Plotter*, and modules from ``config/plotter_modules/``) plus,
    when the data came from a loader plugin, the plotters that plugin declares.
    The item data is the plotter id. Changing it refills **Plot Type**.

**Plot Type:** (``plot_type``, :class:`AutoWidthComboBox`)
    The plot types of the selected plotter from ``MainWindow.plot_type_entries``
    (for the Basic Plotter: ``scatter``, ``line``, ``scatter_line`` and
    ``scatter_publication``).

**Template:** (``style_module``) and **Reload**
    ``None`` or a saved figure template (a JSON file in ``config/templates/``,
    for example one saved from the Figure Editor). The item data is the file
    path. **Reload** (tooltip *Re-scan config/templates*) re-reads the folder.
    The template is applied to the figure after it is rendered; it is not part
    of the recorded plot step's configuration.

**Fit Function:** (``fit_enabled`` check box *LSQ fit*, ``fit_expression``)
    Tick **LSQ fit** to overlay a least-squares fit of the **Y** column against
    the **X** column on the first axes. The expression defaults to
    ``a*x + b`` (placeholder ``f(x)``).

**Params / Initial:** (``fit_parameters``, ``fit_initial``)
    Comma-separated parameter names (default ``a,b``) and initial guesses
    (default ``1,0``). The two lists must have the same length.

**Fit Style:** (``fit_style_preset``) and **Reload**
    ``Default`` or a fit-style preset (a JSON file in
    ``config/figureforge_fit_styles/``). Choosing a preset copies its label,
    line style, line width and legend setting into the **Fit Line** controls.
    **Reload** (tooltip *Re-scan config/figureforge_fit_styles*) re-reads the
    folder.

**Fit Line:** (``fit_label``, ``fit_line_style``, ``fit_line_width``, ``fit_show_legend``)
    Legend label (blank builds one from the fitted parameters), line style
    (``--``, ``-``, ``-.`` or ``:``), line width (default ``2``) and the
    **Legend** check box (on by default).

    When **LSQ fit** is ticked, these settings are passed as ``lsq_fit`` in
    the plot configuration, so they are stored in the recorded
    ``PlotModuleStep`` and replayed with it.

**Generate Plot** (primary push button)
    Calls ``MainWindow.generate_module_plot`` with the plotter id, plot type,
    template path and fit configuration. The Basic Plotter's figure opens in
    the Figure Editor (FigureForge) in a separate process; other backend
    plotters open in a *PhysPlot - <plotter>: <plot type>* window with the
    Matplotlib toolbar. A plotter function declared by a loader plugin is
    shown the same way, is not replayable, and rejects an LSQ fit. A
    **Generate Plot** row (``Create <plotter id> <plot type>``, target
    *Plotter Module*) is recorded. The status bar shows *Plot generated*; an
    error shows the *Plot failed* warning.

**Export Plot** (push button)
    Calls ``MainWindow.export_module_plot``, which saves the last generated
    figure as PNG, PDF or SVG at 300 dpi (default name ``physplot_plot.png``).
    Without a figure it shows *Export plot failed: Generate a plot before
    exporting.* Exporting is not recorded in the protocol.

.. rubric:: Refresh behaviour

- :meth:`SimpleModePanel.refresh_columns` runs each time the main window
  refreshes its panels (``MainWindow._refresh_all``), for example after an
  import, a transformation, a column rename or a protocol change. It relists
  the columns, keeps the current input and output choices, and selects the
  **Y**-role column as the input whenever new data has been loaded.
- :meth:`SimpleModePanel.refresh_plotters` runs on the same refreshes, because
  the plotter list depends on the data and on the loader plugin used. It keeps
  the selected plotter, rebuilds **Plot Type**, and re-reads the templates.
- :meth:`SimpleModePanel.refresh_plugins` runs from *File > Reload Config
  Modules* (``Ctrl+Shift+R``). It re-reads the loader, function, plotter,
  template and fit-style folders and keeps the current selections where they
  still exist.

.. rubric:: Sizing

The panel row sits in a frameless horizontal :class:`QScrollArea`. When the
window is narrower than the panels' minimum width, a horizontal scroll bar
appears instead of the main window growing past the screen, and the panel
grows by the scroll bar's height. Whenever the needed height changes the panel
emits :attr:`SimpleModePanel.height_changed`; the
:class:`~physplot_gui.app.mode_manager.ModeManager` then fixes the lower
control area to exactly that height so the table gets the rest of the window.
The drop-down menus are :class:`AutoWidthComboBox` instances: the closed box
is sized from a few characters instead of its longest item, while the popup
widens to show full labels.
"""

from __future__ import annotations

from physplot.qt_compat import QtCore, QtGui, QtWidgets


class AutoWidthComboBox(QtWidgets.QComboBox):
    """Compact combo box whose popup expands to fit long scientific labels.

    The closed box is sized from a short minimum length instead of its longest
    item, so Simple Mode fits laptop-width windows; the popup and tooltip still
    show the full label.

    Every drop-down menu in Simple Mode uses this class: **Data Loader**,
    **Input**, **Function**, **Output**, **Plotter Module**, **Plot Type**,
    **Template**, **Fit Style** and the fit line-style menu.

    Behaviour seen by the user:

    - **Compact closed box.** The size-adjust policy is
      ``AdjustToMinimumContentsLengthWithIcon`` with a minimum contents length
      of ``minimum_characters`` (6 by default, 2 for the fit line-style menu),
      so a long loader or plugin name never widens the whole panel row.
    - **Wide popup.** Opening the list widens it to the longest item label, so
      full names such as *XRDML Loader (Panalytical XRD)* stay readable.
    - **Helpful tooltip.** Hovering the closed box shows the selected item's
      description (its ``ToolTipRole`` data, used by the **Function** menu) or,
      when it has none, the full selected label.
    """

    def __init__(self, parent=None, minimum_characters: int = 6):
        """Create the combo box with a compact size policy.

        The size policy is set before any size query because
        :class:`QComboBox` caches its minimum size. The tooltip is updated each
        time the selected item changes.

        :param parent: Optional parent widget.
        :param minimum_characters: Number of characters the closed box is sized
            for, independent of the longest item.
        """
        super().__init__(parent)
        # Must be set before the first size query: QComboBox caches its minimum size.
        self.setSizeAdjustPolicy(QtWidgets.QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.setMinimumContentsLength(minimum_characters)
        self.currentIndexChanged.connect(self._update_tooltip)

    def _update_tooltip(self, index: int) -> None:
        """Show the selected item's description, or its full label when it has none.

        Connected to ``currentIndexChanged``. The **Function** menu stores a
        description per item in ``ToolTipRole``; other menus fall back to the
        selected text, which may be cut off in the compact closed box.

        :param index: Index of the newly selected item, or ``-1`` when the box
            is empty.
        """
        tooltip = self.itemData(index, QtCore.Qt.ItemDataRole.ToolTipRole) if index >= 0 else None
        self.setToolTip(tooltip or self.currentText())

    def showPopup(self) -> None:
        """Open the drop-down list, first widening it to fit every item label.

        Overrides :meth:`QComboBox.showPopup`; Qt calls it whenever the user
        opens the list with the mouse or the keyboard.
        """
        self._resize_popup_to_contents()
        super().showPopup()

    def _resize_popup_to_contents(self) -> None:
        """Set the popup's minimum width so the longest label is fully visible.

        The width is the larger of the closed box's width and the widest item
        text (measured with the box's font) plus 42 px of padding, plus the
        width of a vertical scroll bar. The closed box itself keeps its compact
        size.
        """
        view = self.view()
        width = self.width()
        metrics = self.fontMetrics()
        for index in range(self.count()):
            width = max(width, metrics.horizontalAdvance(self.itemText(index)) + 42)
        scrollbar_width = self.style().pixelMetric(QtWidgets.QStyle.PixelMetric.PM_ScrollBarExtent)
        view.setMinimumWidth(width + scrollbar_width)


class SimpleModePanel(QtWidgets.QWidget):
    """Show the Simple Mode row: Data Importer, Transformation and Plotter Module.

    The :class:`~physplot_gui.app.mode_manager.ModeManager` places this panel
    in the lower control area under the central table when the header's mode
    switcher (or *View > Simple Mode*, ``Ctrl+1``) selects **Simple**. The panel
    is a thin view: each button calls a method of ``actions`` (the
    :class:`~physplot_gui.app.main_window.MainWindow`), which does the work
    through the backend and records the protocol step. The module docstring
    describes every control in detail.

    .. rubric:: Layout

    A frameless :class:`QScrollArea` (horizontal scroll bar as needed, vertical
    scroll bar always off) wraps a content widget whose horizontal layout holds
    three ``Panel`` frames with stretch factors 4, 5 and 12::

        [ 1. Data Importer ] [ 2. Mathematical Transformation ] [ 3. Plotter Module ]

    .. rubric:: Public widget attributes

    Panel **1. Data Importer**:

    - ``loader`` -- :class:`AutoWidthComboBox` **Data Loader:**; item data is
      the loader entry ``dict``.

    Panel **2. Mathematical Transformation**:

    - ``input_column`` -- :class:`AutoWidthComboBox` **Input:**; item data is
      the real column name.
    - ``function`` -- :class:`AutoWidthComboBox` **Function:**; item data is
      the function entry ``dict``, with a description in ``ToolTipRole``.
    - ``offset`` -- :class:`QLineEdit` after the **+** label (default ``0``,
      at most 72 px wide).
    - ``output_column`` -- editable :class:`AutoWidthComboBox` **Output:**
      (placeholder *Output column*, typed text is not inserted as an item).

    Panel **3. Plotter Module**:

    - ``plotter`` -- :class:`AutoWidthComboBox` **Plotter Module:**; item data
      is the plotter id.
    - ``plot_type`` -- :class:`AutoWidthComboBox` **Plot Type:**.
    - ``style_module`` -- :class:`AutoWidthComboBox` **Template:**; item data
      is the template file path, or ``None`` for *None*.
    - ``fit_enabled`` -- :class:`QCheckBox` **LSQ fit** (unchecked).
    - ``fit_expression`` -- :class:`QLineEdit` fit function (default
      ``a*x + b``, placeholder ``f(x)``).
    - ``fit_parameters`` -- :class:`QLineEdit` parameter names (default
      ``a,b``, placeholder *parameters*).
    - ``fit_initial`` -- :class:`QLineEdit` initial guesses (default ``1,0``,
      placeholder *initial guesses*).
    - ``fit_style_preset`` -- :class:`AutoWidthComboBox` **Fit Style:**; item
      data is the preset path, and ``UserRole + 1`` holds the preset payload.
    - ``fit_label`` -- :class:`QLineEdit` legend label (placeholder *label*).
    - ``fit_line_style`` -- :class:`AutoWidthComboBox` with ``--``, ``-``,
      ``-.`` and ``:`` (sized for 2 characters).
    - ``fit_line_width`` -- :class:`QLineEdit` line width (default ``2``,
      tooltip *Fit line width*, at most 52 px wide).
    - ``fit_show_legend`` -- :class:`QCheckBox` **Legend** (checked).

    The **Import Data**, **Import Folder**, **Export Data**, **Apply**, both
    **Reload**, **Generate Plot** and **Export Plot** buttons are local widgets
    connected at construction time and are not stored as attributes.

    .. rubric:: Signals

    ``height_changed``
        Emitted with no arguments when the height the panel needs changes, for
        example when the horizontal scroll bar appears or disappears, when the
        panels are first styled, or when their contents change. The
        :class:`~physplot_gui.app.mode_manager.ModeManager` responds by fixing
        the lower control area to :meth:`sizeHint` while Simple Mode is shown.

    :param actions: The object that performs the work, normally the
        :class:`~physplot_gui.app.main_window.MainWindow`. The panel calls its
        ``backend_loader_entries``, ``simple_function_entries``,
        ``plotter_entries``, ``plot_type_entries``, ``style_module_entries``,
        ``fit_style_entries``, ``import_data``, ``import_folder``,
        ``export_data``, ``apply_backend_transform``, ``generate_module_plot``
        and ``export_module_plot`` methods and reads its ``state``.
    :param parent: Optional parent widget.
    """
    height_changed = QtCore.pyqtSignal()

    def __init__(self, actions, parent=None):
        """Build the three panels, the scroll area and the initial menus.

        After the widgets are built, the plotter list (and with it the plot
        types and templates) is filled once. Layout requests from the content
        widget are watched so the panel can re-fit its height.

        :param actions: The main window (or a compatible object) that performs
            every action.
        :param parent: Optional parent widget.
        """
        super().__init__(parent)
        self.actions = actions
        self._columns: list[str] = []
        self._data_key = None
        self._plotter_entries: list[dict] = []
        self._needs_scroll = False
        self._fitted = 0

        self._content = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(self._content)
        layout.setContentsMargins(0, 6, 0, 6)
        layout.setSpacing(6)
        layout.addWidget(self._data_importer_panel(), 4)
        layout.addWidget(self._transform_panel(), 5)
        layout.addWidget(self._plotter_panel(), 12)

        # On screens narrower than the three panels, scroll sideways instead of
        # forcing the main window wider than the screen.
        self._scroll = QtWidgets.QScrollArea()
        self._scroll.setWidget(self._content)
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self._scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._scroll.viewport().setAutoFillBackground(False)
        self._content.setAutoFillBackground(False)
        outer = QtWidgets.QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self._scroll)
        self._content.installEventFilter(self)
        self.refresh_plotters()

    def sizeHint(self) -> QtCore.QSize:
        """Return the preferred size: the panels' natural width and fitted height.

        The :class:`~physplot_gui.app.mode_manager.ModeManager` uses the height
        to size the lower control area exactly, so the central table receives
        all remaining space.

        :returns: The content widget's preferred width and
            :meth:`fitted_height`.
        """
        return QtCore.QSize(self._content.sizeHint().width(), self.fitted_height())

    def minimumSizeHint(self) -> QtCore.QSize:
        """Return a minimum size with zero width and the fitted height.

        A zero minimum width lets the main window shrink below the panels'
        natural width; the horizontal scroll bar then takes over instead of
        the window growing past the screen.

        :returns: ``QSize(0, fitted_height())``.
        """
        return QtCore.QSize(0, self.fitted_height())

    def fitted_height(self) -> int:
        """Height of the three panels, plus the scrollbar while one is shown.

        :returns: The content widget's preferred height in pixels, plus the
            horizontal scroll bar's height when the window is too narrow for
            the panels.
        """
        height = self._content.sizeHint().height()
        if self._needs_scroll:
            height += self._scroll.horizontalScrollBar().sizeHint().height()
        return height

    def resizeEvent(self, event) -> None:
        """Re-fit the panel height after the user resizes the window.

        Narrowing the window may make the horizontal scroll bar necessary (and
        widening it may remove it), which changes the height the panel needs.

        :param event: The Qt resize event.
        """
        super().resizeEvent(event)
        self._refit()

    def eventFilter(self, watched, event) -> bool:
        """Schedule a re-fit when the three-panel content asks for a new layout.

        A ``LayoutRequest`` on the content widget (sent once the panels are
        styled and whenever their contents change) queues :meth:`_refit` on
        the event loop with a zero-delay timer, so the final sizes are used.

        :param watched: The object the event was sent to.
        :param event: The event being filtered.
        :returns: The base-class result; the event is never consumed here.
        """
        # Panels ask for a new layout once styled and when their contents change.
        if watched is self._content and event.type() == QtCore.QEvent.Type.LayoutRequest:
            QtCore.QTimer.singleShot(0, self._refit)
        return super().eventFilter(watched, event)

    def _refit(self) -> None:
        """Re-fit to the panels' real height and toggle room for the scrollbar.

        The horizontal scroll bar is counted when the content's minimum width
        exceeds the panel's current width. If the resulting
        :meth:`fitted_height` differs from the last one, the geometry is
        updated and :attr:`height_changed` is emitted so the
        :class:`~physplot_gui.app.mode_manager.ModeManager` can resize the
        lower control area.
        """
        self._needs_scroll = self._content.minimumSizeHint().width() > self.width()
        height = self.fitted_height()
        if height != self._fitted:
            self._fitted = height
            self.updateGeometry()
            self.height_changed.emit()

    def _data_importer_panel(self):
        """Build the **1. Data Importer** panel.

        Grid layout: the title on row 0; **Data Loader:** and :attr:`loader` on
        row 1; **Import Data** and **Import Folder** on row 2; **Export Data**
        on row 3. The loader menu is filled from
        ``actions.backend_loader_entries()``; disabled entries are greyed out
        and cannot be chosen.

        Button wiring:

        - **Import Data** calls ``actions.import_data`` with
          :meth:`_loader_entry` (the selected loader, or ``"auto"``).
        - **Import Folder** calls ``actions.import_folder``.
        - **Export Data** calls ``actions.export_data``.

        :returns: The panel frame.
        """
        frame = self._panel()
        layout = QtWidgets.QGridLayout(frame)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setHorizontalSpacing(8)
        layout.setVerticalSpacing(7)
        title = self._title("1. Data Importer")

        self.loader = AutoWidthComboBox()
        for entry in self.actions.backend_loader_entries():
            self.loader.addItem(entry["display_name"], entry)
            if not entry.get("enabled", True):
                item = self.loader.model().item(self.loader.count() - 1)
                item.setFlags(item.flags() & ~QtCore.Qt.ItemFlag.ItemIsEnabled)
                item.setForeground(QtGui.QColor("#94a3b8"))

        import_button = QtWidgets.QPushButton("Import Data")
        import_button.clicked.connect(lambda: self.actions.import_data(self._loader_entry()))
        import_folder_button = QtWidgets.QPushButton("Import Folder")
        import_folder_button.clicked.connect(self.actions.import_folder)
        export_button = QtWidgets.QPushButton("Export Data")
        export_button.clicked.connect(self.actions.export_data)

        layout.addWidget(title, 0, 0, 1, 3)
        layout.addWidget(QtWidgets.QLabel("Data Loader:"), 1, 0)
        layout.addWidget(self.loader, 1, 1, 1, 2)
        layout.addWidget(import_button, 2, 0)
        layout.addWidget(import_folder_button, 2, 1, 1, 2)
        layout.addWidget(export_button, 3, 0)
        layout.setColumnStretch(1, 1)
        layout.setRowStretch(4, 1)
        return frame

    def _transform_panel(self):
        """Build the **2. Mathematical Transformation** panel.

        Grid layout: the title on row 0; **Input:** :attr:`input_column`,
        **Function:** :attr:`function`, **+** and :attr:`offset` on row 1;
        **Output:** and :attr:`output_column` on row 2; the **Apply** button
        spans rows 1 and 2 on the right. The function menu is filled by
        :meth:`_fill_function_menu`; the column menus stay empty until
        :meth:`refresh_columns` runs. **Apply** calls :meth:`_apply`.

        :returns: The panel frame.
        """
        frame = self._panel()
        layout = QtWidgets.QGridLayout(frame)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setHorizontalSpacing(8)
        layout.setVerticalSpacing(7)
        layout.addWidget(self._title("2. Mathematical Transformation"), 0, 0, 1, 8)

        self.input_column = AutoWidthComboBox()
        self.function = AutoWidthComboBox()
        self._fill_function_menu()
        self.offset = QtWidgets.QLineEdit("0")
        self.offset.setMaximumWidth(72)
        self.output_column = AutoWidthComboBox()
        self.output_column.setEditable(True)
        self.output_column.setInsertPolicy(QtWidgets.QComboBox.InsertPolicy.NoInsert)
        self.output_column.setPlaceholderText("Output column")
        apply_button = QtWidgets.QPushButton("Apply")
        apply_button.clicked.connect(self._apply)

        layout.addWidget(QtWidgets.QLabel("Input:"), 1, 0)
        layout.addWidget(self.input_column, 1, 1)
        layout.addWidget(QtWidgets.QLabel("Function:"), 1, 2)
        layout.addWidget(self.function, 1, 3)
        layout.addWidget(QtWidgets.QLabel("+"), 1, 4)
        layout.addWidget(self.offset, 1, 5)
        layout.addWidget(QtWidgets.QLabel("Output:"), 2, 0)
        layout.addWidget(self.output_column, 2, 1, 1, 5)
        layout.addWidget(apply_button, 1, 6, 2, 1)
        layout.setColumnStretch(1, 2)
        layout.setColumnStretch(3, 2)
        layout.setColumnStretch(5, 1)
        layout.setRowStretch(3, 1)
        return frame

    def _plotter_panel(self):
        """Build the **3. Plotter Module** panel.

        Grid layout, left column (what to plot): **Plotter Module:**
        :attr:`plotter`, **Plot Type:** :attr:`plot_type`, **Template:**
        :attr:`style_module` with its **Reload** button, and on the last row the
        **Generate Plot** (primary) and **Export Plot** buttons. Right column
        (optional least-squares fit): **Fit Function:** (**LSQ fit** check box
        and expression), **Params / Initial:**, **Fit Style:** (preset menu and
        its **Reload** button) and **Fit Line:** (label, line style, line width
        and **Legend**), which shares the button row to keep the panel short.

        Wiring:

        - changing :attr:`plotter` calls :meth:`_plotter_changed`;
        - changing :attr:`fit_style_preset` calls :meth:`_fit_style_changed`;
        - the template **Reload** calls :meth:`refresh_styles`;
        - the fit-style **Reload** calls :meth:`refresh_fit_styles`;
        - **Generate Plot** calls :meth:`_generate_plot`;
        - **Export Plot** calls ``actions.export_module_plot``.

        The template and fit-style menus are filled before returning.

        :returns: The panel frame.
        """
        frame = self._panel()
        layout = QtWidgets.QGridLayout(frame)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setHorizontalSpacing(8)
        layout.setVerticalSpacing(7)
        layout.addWidget(self._title("3. Plotter Module"), 0, 0, 1, 4)

        self.plotter = AutoWidthComboBox()
        self.plotter.currentIndexChanged.connect(self._plotter_changed)
        self.plot_type = AutoWidthComboBox()
        self.style_module = AutoWidthComboBox()
        self.fit_enabled = QtWidgets.QCheckBox("LSQ fit")
        self.fit_expression = QtWidgets.QLineEdit("a*x + b")
        self.fit_expression.setPlaceholderText("f(x)")
        self.fit_parameters = QtWidgets.QLineEdit("a,b")
        self.fit_parameters.setPlaceholderText("parameters")
        self.fit_initial = QtWidgets.QLineEdit("1,0")
        self.fit_initial.setPlaceholderText("initial guesses")
        self.fit_label = QtWidgets.QLineEdit("")
        self.fit_label.setPlaceholderText("label")
        self.fit_style_preset = AutoWidthComboBox()
        self.fit_style_preset.currentIndexChanged.connect(self._fit_style_changed)
        self.fit_line_style = AutoWidthComboBox(minimum_characters=2)
        self.fit_line_style.addItems(["--", "-", "-.", ":"])
        self.fit_line_width = QtWidgets.QLineEdit("2")
        self.fit_line_width.setMaximumWidth(52)
        self.fit_line_width.setToolTip("Fit line width")
        self.fit_show_legend = QtWidgets.QCheckBox("Legend")
        self.fit_show_legend.setChecked(True)
        reload_styles_button = QtWidgets.QPushButton("Reload")
        reload_styles_button.setToolTip("Re-scan config/templates")
        reload_styles_button.clicked.connect(self.refresh_styles)
        reload_fit_styles_button = QtWidgets.QPushButton("Reload")
        reload_fit_styles_button.setToolTip("Re-scan config/figureforge_fit_styles")
        reload_fit_styles_button.clicked.connect(self.refresh_fit_styles)
        generate_button = QtWidgets.QPushButton("Generate Plot")
        generate_button.setProperty("primary", True)
        generate_button.clicked.connect(self._generate_plot)
        export_button = QtWidgets.QPushButton("Export Plot")
        export_button.clicked.connect(self.actions.export_module_plot)

        # Left column: what to plot.
        layout.addWidget(QtWidgets.QLabel("Plotter Module:"), 1, 0)
        layout.addWidget(self.plotter, 1, 1)
        layout.addWidget(QtWidgets.QLabel("Plot Type:"), 2, 0)
        layout.addWidget(self.plot_type, 2, 1)
        layout.addWidget(QtWidgets.QLabel("Template:"), 3, 0)
        style_layout = QtWidgets.QHBoxLayout()
        style_layout.setSpacing(6)
        style_layout.addWidget(self.style_module, 1)
        style_layout.addWidget(reload_styles_button)
        layout.addLayout(style_layout, 3, 1)

        # Right column: optional least-squares fit.
        fit_layout = QtWidgets.QHBoxLayout()
        fit_layout.setSpacing(6)
        fit_layout.addWidget(self.fit_enabled)
        fit_layout.addWidget(self.fit_expression, 1)
        layout.addWidget(QtWidgets.QLabel("Fit Function:"), 1, 2)
        layout.addLayout(fit_layout, 1, 3)
        fit_params_layout = QtWidgets.QHBoxLayout()
        fit_params_layout.setSpacing(6)
        fit_params_layout.addWidget(self.fit_parameters, 1)
        fit_params_layout.addWidget(self.fit_initial, 1)
        layout.addWidget(QtWidgets.QLabel("Params / Initial:"), 2, 2)
        layout.addLayout(fit_params_layout, 2, 3)
        fit_style_layout = QtWidgets.QHBoxLayout()
        fit_style_layout.setSpacing(6)
        fit_style_layout.addWidget(self.fit_style_preset, 1)
        fit_style_layout.addWidget(reload_fit_styles_button)
        layout.addWidget(QtWidgets.QLabel("Fit Style:"), 3, 2)
        layout.addLayout(fit_style_layout, 3, 3)
        # Fit line options share the button row so the panel stays narrow.
        fit_line_layout = QtWidgets.QHBoxLayout()
        fit_line_layout.setSpacing(6)
        fit_line_layout.addWidget(self.fit_label, 1)
        fit_line_layout.addWidget(self.fit_line_style)
        fit_line_layout.addWidget(self.fit_line_width)
        fit_line_layout.addWidget(self.fit_show_legend)
        layout.addWidget(QtWidgets.QLabel("Fit Line:"), 4, 2)
        layout.addLayout(fit_line_layout, 4, 3)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setSpacing(8)
        button_layout.addWidget(generate_button, 1)
        button_layout.addWidget(export_button, 1)
        layout.addLayout(button_layout, 4, 0, 1, 2)
        layout.setColumnStretch(1, 2)
        layout.setColumnStretch(3, 3)
        self.refresh_styles()
        self.refresh_fit_styles()
        return frame

    def refresh_plugins(self) -> None:
        """Re-scan editable config folders and repopulate every plugin menu.

        Called by ``MainWindow.reload_config_modules`` (*File > Reload Config
        Modules*, ``Ctrl+Shift+R``) so new or edited files in
        ``Documents/PhysPlot/config/`` appear without restarting. It rebuilds:

        - **Data Loader** from ``actions.backend_loader_entries()`` (backend
          loaders plus ``config/data_importers/`` plugins), greying out
          disabled entries;
        - **Function** from ``actions.simple_function_entries()`` (built-ins
          plus ``config/transformations/`` plugins), with their tooltips;
        - **Plotter Module**, **Plot Type** and **Template** via
          :meth:`refresh_plotters`;
        - **Fit Style** via :meth:`refresh_fit_styles`.

        The previously selected loader and function are re-selected by label
        when they still exist. Signals are blocked while the loader and
        function menus are rebuilt.
        """
        loader_current = self.loader.currentText()
        self.loader.blockSignals(True)
        self.loader.clear()
        for entry in self.actions.backend_loader_entries():
            self.loader.addItem(entry["display_name"], entry)
            if not entry.get("enabled", True):
                item = self.loader.model().item(self.loader.count() - 1)
                item.setFlags(item.flags() & ~QtCore.Qt.ItemFlag.ItemIsEnabled)
                item.setForeground(QtGui.QColor("#94a3b8"))
        index = self.loader.findText(loader_current)
        if index >= 0:
            self.loader.setCurrentIndex(index)
        self.loader.blockSignals(False)

        function_current = self.function.currentText()
        self.function.blockSignals(True)
        self.function.clear()
        self._fill_function_menu()
        index = self.function.findText(function_current)
        if index >= 0:
            self.function.setCurrentIndex(index)
        self.function.blockSignals(False)

        self.refresh_plotters()
        self.refresh_fit_styles()

    def _fill_function_menu(self) -> None:
        """Append every transformation to the **Function** menu with its tooltip.

        Entries come from ``actions.simple_function_entries()``: ``identity``
        and the backend built-ins, labelled and described by
        ``BUILTIN_FUNCTIONS`` in ``physplot_gui/app/main_window.py`` (for
        example ``baseline_subtract`` is shown as *subtract first value*),
        followed by ``config/transformations/`` plugins, whose tooltip is the
        first line of the plugin's module docstring plus its file name. Each
        item stores the entry ``dict`` as item data and its description in
        ``ToolTipRole``; the closed box's tooltip is then refreshed for the
        current item.
        """
        for entry in self.actions.simple_function_entries():
            self.function.addItem(entry["display_name"], entry)
            if entry.get("tooltip"):
                self.function.setItemData(self.function.count() - 1, entry["tooltip"], QtCore.Qt.ItemDataRole.ToolTipRole)
        self.function._update_tooltip(self.function.currentIndex())

    def refresh_columns(self, columns: list[str]) -> None:
        """Refresh input/output column menus without duplicating default names.

        New data (not just added output columns) selects the Y-role column as
        the transformation input, since that is what is usually transformed.

        Called by the :class:`~physplot_gui.app.mode_manager.ModeManager`
        whenever the main window refreshes (``MainWindow._refresh_all``), with
        the central table's current column names.

        Behaviour:

        - Both **Input** and **Output** are rebuilt with one item per column,
          labelled by :meth:`_column_label` (``Column N`` or ``N: name``) and
          carrying the real column name as item data.
        - Data counts as new when the backend dataset's name or source path
          differs from the previous call. Then the column whose role is **Y**
          becomes the input, if there is one.
        - Otherwise the previously selected input column stays selected; if it
          no longer exists, the first column is selected.
        - The previous output choice is kept: an existing column is
          re-selected, and a typed new name is put back into the edit field.

        :param columns: Column names in table order.
        """
        self._columns = list(columns)
        current = self.input_column.currentData()
        state = getattr(self.actions, "state", None)
        dataset = getattr(getattr(state, "pp", None), "dataset", None)
        data_key = (dataset.name, str(dataset.source_path)) if dataset is not None else None
        new_data = data_key != self._data_key
        self._data_key = data_key
        roles = getattr(state, "roles", {}) or {}
        y_column = next((column for column in columns if roles.get(column) == "Y"), None)
        if new_data and y_column is not None:
            current = y_column
        output_current = self.output_column.currentData() or self.output_column.currentText()
        self.input_column.clear()
        self.output_column.clear()
        for index, column in enumerate(columns, start=1):
            label = self._column_label(index, column)
            self.input_column.addItem(label, column)
            self.output_column.addItem(label, column)
        if current in columns:
            self.input_column.setCurrentText(self._column_label(columns.index(current) + 1, current))
        elif columns:
            self.input_column.setCurrentIndex(0)
        if output_current in columns:
            self.output_column.setCurrentText(self._column_label(columns.index(output_current) + 1, output_current))
        else:
            self.output_column.setEditText(str(output_current or ""))

    def refresh_pipeline(self, rows: list[dict]) -> None:
        """Ignore transformation-pipeline updates; Simple Mode has no pipeline list.

        Kept so the :class:`~physplot_gui.app.mode_manager.ModeManager` can call
        ``refresh_pipeline`` on every panel.

        :param rows: The main window's recorded transformations (unused).
        """
        return

    def refresh_plotters(self) -> None:
        """Rebuild the **Plotter Module** menu, its plot types and the templates.

        Called once at construction and on every main-window refresh (through
        ``ModeManager.refresh_plots``), because the available plotters depend
        on the current data and on the loader plugin used to import it. The
        list comes from ``actions.plotter_entries()``: the backend registry's
        plotters that can plot the current dataset, plus plotters declared by
        the active loader plugin. The previously selected plotter is kept when
        it is still listed. :meth:`_plotter_changed` then refills
        **Plot Type** (its selection returns to the first entry) and
        :meth:`refresh_styles` re-reads the templates.
        """
        current = self.plotter.currentData() if hasattr(self, "plotter") else None
        self._plotter_entries = self.actions.plotter_entries()
        self.plotter.blockSignals(True)
        self.plotter.clear()
        for entry in self._plotter_entries:
            self.plotter.addItem(entry["name"], entry["plotter_id"])
        if current:
            index = self.plotter.findData(current)
            if index >= 0:
                self.plotter.setCurrentIndex(index)
        self.plotter.blockSignals(False)
        self._plotter_changed()
        self.refresh_styles()

    def refresh_styles(self) -> None:
        """Re-read the figure templates into the **Template** menu.

        Connected to the **Reload** button next to **Template** (tooltip
        *Re-scan config/templates*) and called by :meth:`refresh_plotters`.
        Entries come from ``actions.style_module_entries()``: *None* first,
        then every JSON template in the ``config/templates/`` folders (the
        per-user folder wins on name clashes). Each item stores the template's
        file path as item data. The previous choice is re-selected by path
        when it still exists; signals are blocked while the menu is rebuilt.
        """
        current = self.style_module.currentData() if hasattr(self, "style_module") else None
        current = str(current) if current else None
        self.style_module.blockSignals(True)
        self.style_module.clear()
        for entry in self.actions.style_module_entries():
            path = str(entry["path"]) if entry["path"] else None
            self.style_module.addItem(entry["name"], path)
        if current:
            index = self.style_module.findData(current)
            if index >= 0:
                self.style_module.setCurrentIndex(index)
        self.style_module.blockSignals(False)

    def refresh_fit_styles(self) -> None:
        """Re-read the LSQ fit-style presets into the **Fit Style** menu.

        Connected to the **Reload** button next to **Fit Style** (tooltip
        *Re-scan config/figureforge_fit_styles*) and called by
        :meth:`refresh_plugins`. Entries come from
        ``actions.fit_style_entries()``: *Default* first, then every JSON
        preset in the ``config/figureforge_fit_styles/`` folders. Each item
        stores the preset path as item data and the preset payload in
        ``UserRole + 1``. The previous choice is re-selected by path when it
        still exists. Signals are blocked while the menu is rebuilt, so the
        **Fit Line** fields are not overwritten by the refresh.
        """
        current = self.fit_style_preset.currentData() if hasattr(self, "fit_style_preset") else None
        current = str(current) if current else None
        self.fit_style_preset.blockSignals(True)
        self.fit_style_preset.clear()
        for entry in self.actions.fit_style_entries():
            path = str(entry["path"]) if entry["path"] else None
            self.fit_style_preset.addItem(entry["name"], path)
            self.fit_style_preset.setItemData(self.fit_style_preset.count() - 1, entry.get("style"), QtCore.Qt.ItemDataRole.UserRole + 1)
        if current:
            index = self.fit_style_preset.findData(current)
            if index >= 0:
                self.fit_style_preset.setCurrentIndex(index)
        self.fit_style_preset.blockSignals(False)

    def current_style_module(self):
        """Return the file path of the template selected in **Template**.

        Also used by ``MainWindow.generate_plot`` (*Plot > Generate Plot*,
        ``Ctrl+G``) to style its Basic Plotter scatter plot.

        :returns: The template path as a string, or ``None`` when *None* is
            selected.
        """
        path = self.style_module.currentData()
        return str(path) if path else None

    def _plotter_changed(self) -> None:
        """Refill **Plot Type** for the plotter selected in **Plotter Module**.

        Connected to the plotter menu's ``currentIndexChanged`` and called by
        :meth:`refresh_plotters`. The menu is cleared and filled from
        ``actions.plot_type_entries(plotter_id)``; it stays empty when no
        plotter is selected. The previous plot type stays selected when the
        new list still offers it, so a refresh after a transformation or a
        generated plot does not reset the user's choice.
        """
        plotter_id = self.plotter.currentData()
        current = self.plot_type.currentText()
        self.plot_type.clear()
        if not plotter_id:
            return
        self.plot_type.addItems(self.actions.plot_type_entries(plotter_id))
        index = self.plot_type.findText(current)
        if index >= 0:
            self.plot_type.setCurrentIndex(index)

    def _fit_style_changed(self) -> None:
        """Copy the chosen **Fit Style** preset into the **Fit Line** controls.

        Connected to the preset menu's ``currentIndexChanged``. The preset's
        ``label``, ``line_style`` (default ``--``; ignored when not one of the
        four menu entries), ``line_width`` (default ``2.0``) and
        ``show_legend`` (default ``True``) fill :attr:`fit_label`,
        :attr:`fit_line_style`, :attr:`fit_line_width` and
        :attr:`fit_show_legend`. Choosing *Default*, which has no payload,
        leaves the fields unchanged. The fields stay editable afterwards.
        """
        payload = self.fit_style_preset.currentData(QtCore.Qt.ItemDataRole.UserRole + 1)
        if not payload:
            return
        self.fit_label.setText(str(payload.get("label", "")))
        style_index = self.fit_line_style.findText(str(payload.get("line_style", "--")))
        if style_index >= 0:
            self.fit_line_style.setCurrentIndex(style_index)
        self.fit_line_width.setText(str(payload.get("line_width", 2.0)))
        self.fit_show_legend.setChecked(bool(payload.get("show_legend", True)))

    def _apply(self) -> None:
        """Run the transformation configured in panel 2 (the **Apply** button).

        Calls ``actions.apply_backend_transform`` with:

        - the input column's real name (or its text when it has no item data);
        - the selected function entry (or its text);
        - a multiplier of ``1.0``, since Simple Mode has no multiplier control;
        - the **+** offset, or ``0.0`` when the text is not a number;
        - the output name from :meth:`_combo_value` (blank lets the window name
          it ``<input>_<function>``).

        The main window applies the transformation through the backend, shows
        the new column in the table, records **Transform** protocol row(s) and
        reports *Transformation applied* or *Transformation failed* in the
        status bar. See the module docstring for how each function uses the
        offset.
        """
        self.actions.apply_backend_transform(
            self.input_column.currentData() or self.input_column.currentText(),
            self.function.currentData() or self.function.currentText(),
            1.0,
            self._float_value(self.offset.text(), 0.0),
            self._combo_value(self.output_column),
        )

    def _generate_plot(self) -> None:
        """Render the configured plot (the **Generate Plot** button).

        Calls ``actions.generate_module_plot`` with the selected plotter id,
        plot type, template path (:meth:`current_style_module`) and the LSQ fit
        settings from :meth:`_fit_config`. The main window renders through the
        backend, applies the template, opens the figure (in the Figure Editor
        for the Basic Plotter, otherwise in a plot window), records a
        **Generate Plot** protocol row and reports *Plot generated* or
        *Plot failed*. Nothing happens when no plotter is selected.
        """
        self.actions.generate_module_plot(
            self.plotter.currentData(),
            self.plot_type.currentText(),
            self.current_style_module(),
            fit_config=self._fit_config(),
        )

    def _fit_config(self) -> dict | None:
        """Collect the LSQ fit settings, or ``None`` when **LSQ fit** is unticked.

        Blank fields fall back to the defaults: expression ``a*x + b``,
        parameters ``a,b``, initial guesses ``1,0``, line style ``--`` and
        line width ``2.0`` (also used when the width is not a number). The
        label may stay blank, in which case the backend builds one from the
        fitted parameters. The dict is passed on as the ``lsq_fit`` plot
        setting and is therefore stored in the recorded ``PlotModuleStep``.

        :returns: A dict with the keys ``enabled``, ``expression``,
            ``parameters``, ``initial``, ``label``, ``line_style``,
            ``line_width`` and ``show_legend``, or ``None``.
        """
        if not self.fit_enabled.isChecked():
            return None
        return {
            "enabled": True,
            "expression": self.fit_expression.text().strip() or "a*x + b",
            "parameters": self.fit_parameters.text().strip() or "a,b",
            "initial": self.fit_initial.text().strip() or "1,0",
            "label": self.fit_label.text().strip(),
            "line_style": self.fit_line_style.currentText() or "--",
            "line_width": self._float_value(self.fit_line_width.text(), 2.0),
            "show_legend": self.fit_show_legend.isChecked(),
        }

    def _loader_entry(self) -> dict | str:
        """Return the loader chosen in **Data Loader** for **Import Data**.

        :returns: The selected loader entry ``dict`` (with ``display_name`` and
            either ``loader_id`` or a plugin ``module``), or ``"auto"`` when no
            entry is selected.
        """
        return self.loader.currentData() or "auto"

    @staticmethod
    def _float_value(text: str, fallback: float) -> float:
        """Convert a number typed by the user, falling back when it is invalid.

        :param text: Text from a line edit, such as the **+** offset or the fit
            line width.
        :param fallback: Value returned when ``text`` is not a valid number.
        :returns: ``float(text)`` or ``fallback``.
        """
        try:
            return float(text)
        except ValueError:
            return fallback

    @staticmethod
    def _column_label(index: int, column: str) -> str:
        """Show ``Column N`` for defaults and ``N: name`` for real names.

        For example the second column is shown as ``Column 2`` while it still
        has its default name, and as ``2: Intensity`` once it is named
        ``Intensity``. An empty name is treated as the default name.

        :param index: One-based column position in the table.
        :param column: The column's name.
        :returns: The label shown in the **Input** and **Output** menus.
        """
        default_name = f"Column {index}"
        column = str(column or default_name)
        return default_name if column == default_name else f"{index}: {column}"

    @staticmethod
    def _combo_value(combo: QtWidgets.QComboBox) -> str:
        """Return typed output text when it differs from the selected item label.

        Used for the editable **Output** menu. When the text still matches the
        selected item's label (for example ``2: Intensity``), the item's real
        column name is returned so that column is overwritten. Any other text
        is a new column name typed by the user and is returned as typed, with
        surrounding spaces removed; it may be empty.

        :param combo: The combo box to read.
        :returns: A column name, the typed text, or an empty string.
        """
        line_edit = combo.lineEdit() if combo.isEditable() else None
        text = (line_edit.text() if line_edit is not None else combo.currentText()).strip()
        if combo.currentIndex() >= 0 and text == combo.itemText(combo.currentIndex()):
            return combo.currentData() or text
        return text

    @staticmethod
    def _panel():
        """Create an empty frame styled as a Simple Mode panel.

        :returns: A :class:`QFrame` with object name ``Panel``, which the
            application style sheet draws as a white card with a thin border
            and rounded corners.
        """
        frame = QtWidgets.QFrame()
        frame.setObjectName("Panel")
        return frame

    @staticmethod
    def _title(text: str):
        """Create a panel heading such as ``1. Data Importer``.

        :param text: The heading text.
        :returns: A :class:`QLabel` with object name ``SectionTitle``, which the
            application style sheet draws in bold blue.
        """
        label = QtWidgets.QLabel(text)
        label.setObjectName("SectionTitle")
        return label
