"""Build the **Bulk Run** panel that applies a protocol sequence to whole folders.

The panel is the left half of Advanced Mode > **Run Sequence** (see
:class:`~physplot_gui.panels.recorder_mode_panel.RecorderModePanel`). It runs a
protocol sequence, either the one currently in **Build Protocol** or a saved
``Sequence.py`` file, over every data file in a folder and exports one result
folder per input file. Run Sequence never edits the sequence: plot types and
plot settings (including an LSQ fit) come from the sequence's
``PlotModuleStep`` entries, not from the Simple Mode controls. The panel only
collects paths; the work is done by ``MainWindow.run_bulk_workflow`` and the
backend ``physplot.bulk.run_folder``.

The user documentation shows this panel in the *GUI Walkthrough*
(``docs/getting_started.rst``, *Advanced Mode > Run Sequence*, and
``wiki/GUI-Walkthrough.md``) and in the *UI Reference* wiki
(``wiki/UI-Reference.md``, page ``wiki/UI-Run-Sequence.md``).

.. rubric:: Layout

::

    +- Bulk Run -------------------------------------------------------+
    | Plot modules and formatting are read from the sequence.          |
    | Input Folder:  [______________________________________] [Browse] |
    | Sequence File: [Optional; blank uses current Build Pro] [Browse] |
    | Output Folder: [______________________________________] [Browse] |
    | +--------------------------------------------------------------+ |
    | |                      Run Bulk Workflow                       | |
    | +--------------------------------------------------------------+ |
    +------------------------------------------------------------------+

.. rubric:: Controls

**Bulk Run** (title) and the note *Plot modules and formatting are read from the sequence.*
    Static labels (object names ``PanelTitle`` and ``MutedLabel``).

**Input Folder:** (line edit ``input_folder``) and **Browse**
    The folder holding the data files. Type or paste a path, or click
    **Browse**, which calls ``MainWindow.browse_input_folder`` to open an
    *Input Folder* folder chooser and writes the chosen path into the field.

**Sequence File:** (line edit ``workflow_file``) and **Browse**
    Optional ``Sequence.py`` file to run (placeholder *Optional; blank uses
    current Build Protocol sequence*). **Browse** calls
    ``MainWindow.browse_workflow_file``, which opens a *Sequence File* dialog
    for Python files in the ``config/sequences`` folder. Leave it blank to run
    the sequence currently shown in **Build Protocol**, including its load
    step, so a loader plugin recorded there is reused for every file.

**Output Folder:** (line edit ``output_folder``) and **Browse**
    Where results are written; created if it does not exist. **Browse** calls
    ``MainWindow.browse_output_folder`` to open an *Output Folder* chooser.

**Run Bulk Workflow** (primary button ``run_button``, at least 74 px tall)
    Calls ``MainWindow.run_bulk_workflow`` with :meth:`BulkPanel.payload`.
    What happens:

    - Without a sequence file and with an empty Build Protocol sequence, the
      *Bulk run failed* warning says *Build or import a protocol sequence
      before running bulk automation.*
    - The files processed are those directly inside the input folder (not in
      subfolders), in name order, whose extension is ``.csv``, ``.txt``,
      ``.dat``, ``.tsv``, ``.msa``, ``.xls``, ``.xlsx`` or ``.xrdml``. When the
      sequence's load step used a loader plugin or another extension (for
      example ``.ras``), only files with that extension are processed.
    - Each file is loaded into a fresh backend session, the remaining steps
      are replayed (a step whose recorded column name is missing falls back
      to the recorded column number), and the result is exported to
      ``<output folder>/<file name without extension>/``: ``data.csv``,
      ``columns.csv``, ``workflow.py``, plus ``fit.json`` and ``plot.png``
      when the sequence produced a fit or a plot.
    - On success the status bar shows ``Bulk complete: N outputs``.
    - If a file fails, the run stops and the *Bulk run failed* warning names
      that file; files before it were exported and later files were not run.

    A bulk run does not change the central table or the protocol, and it is
    not recorded as a protocol step.
"""

from physplot.qt_compat import QtWidgets


class BulkPanel(QtWidgets.QFrame):
    """Collect the folders and sequence file for a bulk run and start it.

    A ``Panel``-styled frame (white card) with a grid layout: the **Bulk Run**
    title and the muted note on rows 0 and 1, the three path rows on rows 2 to
    4 (label, line edit, **Browse**), and the full-width **Run Bulk Workflow**
    button on row 5. The module docstring describes the end-to-end behaviour.

    .. rubric:: Public attributes

    ``actions``
        The object that performs the work, normally the
        :class:`~physplot_gui.app.main_window.MainWindow`.
    ``input_folder``
        :class:`QLineEdit` for **Input Folder:**.
    ``workflow_file``
        :class:`QLineEdit` for **Sequence File:** (optional, with a
        placeholder explaining that blank uses the Build Protocol sequence).
    ``output_folder``
        :class:`QLineEdit` for **Output Folder:**.
    ``run_button``
        The primary :class:`QPushButton` **Run Bulk Workflow**; clicking it
        calls ``actions.run_bulk_workflow(self.payload())``.

    The panel defines no Qt signals.

    :param actions: Object providing ``browse_input_folder``,
        ``browse_workflow_file``, ``browse_output_folder`` (each called with
        the line edit to fill) and ``run_bulk_workflow`` (called with
        :meth:`payload`).
    :param parent: Optional parent widget.
    """
    def __init__(self, actions, parent=None):
        """Build the title, note, three path rows and the run button.

        :param actions: The main window (or a compatible object) that browses
            for paths and runs the bulk workflow.
        :param parent: Optional parent widget.
        """
        super().__init__(parent)
        self.setObjectName("Panel")
        self.actions = actions
        layout = QtWidgets.QGridLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setHorizontalSpacing(8)
        layout.setVerticalSpacing(6)
        title = QtWidgets.QLabel("Bulk Run")
        title.setObjectName("PanelTitle")
        layout.addWidget(title, 0, 0, 1, 3)
        note = QtWidgets.QLabel("Plot modules and formatting are read from the sequence.")
        note.setObjectName("MutedLabel")
        layout.addWidget(note, 1, 0, 1, 3)
        self.input_folder = self._path_row(layout, 2, "Input Folder:", actions.browse_input_folder)
        self.workflow_file = self._path_row(layout, 3, "Sequence File:", actions.browse_workflow_file)
        self.workflow_file.setPlaceholderText("Optional; blank uses current Build Protocol sequence")
        self.output_folder = self._path_row(layout, 4, "Output Folder:", actions.browse_output_folder)
        self.run_button = QtWidgets.QPushButton("Run Bulk Workflow")
        self.run_button.setProperty("primary", True)
        self.run_button.setMinimumHeight(74)
        self.run_button.clicked.connect(lambda: actions.run_bulk_workflow(self.payload()))
        layout.addWidget(self.run_button, 5, 0, 1, 3)

    def _path_row(self, layout, row: int, label: str, callback):
        """Add one *label - line edit - Browse* row to the grid.

        Clicking the row's **Browse** button calls ``callback(field)``; the
        main window's browse methods open a file or folder dialog and write the
        chosen path into ``field``. The user may also type the path directly.

        :param layout: The panel's grid layout.
        :param row: Grid row to fill.
        :param label: Visible label, for example ``"Input Folder:"``.
        :param callback: Called with the line edit when **Browse** is clicked.
        :returns: The new :class:`QLineEdit`.
        """
        field = QtWidgets.QLineEdit()
        browse = QtWidgets.QPushButton("Browse")
        browse.clicked.connect(lambda: callback(field))
        layout.addWidget(QtWidgets.QLabel(label), row, 0)
        layout.addWidget(field, row, 1)
        layout.addWidget(browse, row, 2)
        return field

    def payload(self) -> dict:
        """Return the three paths entered in the panel.

        The values are the field texts with surrounding spaces removed; the
        panel does not check them. An empty ``workflow_file`` tells the main
        window to use the current Build Protocol sequence.

        :returns: ``{"input_folder": ..., "workflow_file": ...,
            "output_folder": ...}``.
        """
        return {
            "input_folder": self.input_folder.text().strip(),
            "workflow_file": self.workflow_file.text().strip(),
            "output_folder": self.output_folder.text().strip(),
        }
