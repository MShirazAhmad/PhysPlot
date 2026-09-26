"""Bottom status bar.

:class:`PhysPlotStatusBar` is the strip along the bottom of the PhysPlot window, below the
mode panels. It is an ordinary ``QFrame`` in the main window layout (object name
``StatusBar``), not Qt's ``QStatusBar``. From left to right it shows:

* a small green "ready" dot (hidden in Simple mode);
* the status message, ``Status: <message>``, which takes all spare width. It shows the last
  action or error (for example ``Status: Plot generated``). A long message is cut with an
  ellipsis instead of widening the window; hover it to read the full text in the tooltip;
* ``Rows: <n>`` and ``Columns: <n>``, the size of the backend dataset (the trimmed table,
  not the padded grid);
* ``File: <name>``, the file name of the last imported file, or ``-``;
* ``Workflow: <name>``, the file name of the saved or loaded sequence, or ``Untitled``
  (hidden in Simple mode);
* ``Mode: <mode>``, the current GUI mode (hidden in Simple mode).

The main window calls :meth:`PhysPlotStatusBar.set_message` after actions and errors, and
:meth:`PhysPlotStatusBar.update_state` whenever the dataset, file or mode changes.
"""

from pathlib import Path

from physplot.qt_compat import QtCore, QtWidgets


class ElidedLabel(QtWidgets.QLabel):
    """Single-line label that never widens its window.

    Long text is cut with an ellipsis to the space available; ``text()`` and the
    tooltip keep the full message.

    The label's horizontal size policy is ``Ignored``, so its text never asks the layout
    for more width: the label simply gets whatever width the layout gives it, and the
    window cannot be pushed wider by a long status message. All runs of whitespace,
    including newlines, are collapsed to single spaces, so a multi-line error message is
    shown on one line. The visible text is re-elided at the right-hand end every time the
    label is resized, and the tooltip always holds the full, collapsed message.
    """

    def __init__(self, text: str = "", parent=None):
        """Create the label and show ``text``.

        :param text: Initial message.
        :param parent: Optional Qt parent widget.
        """
        super().__init__(parent)
        self._full_text = ""
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Ignored, QtWidgets.QSizePolicy.Policy.Preferred)
        self.setText(text)

    def setText(self, text: str) -> None:
        """Store the full message, put it in the tooltip, and show it elided.

        Whitespace runs are collapsed to single spaces before storing.

        :param text: New message; any object is converted with ``str``.
        """
        self._full_text = " ".join(str(text).split())
        self.setToolTip(self._full_text)
        self._show_elided()

    def text(self) -> str:
        """Return the full, un-elided message (whitespace collapsed).

        :returns: The message last passed to :meth:`setText`, not the visible text.
        """
        return self._full_text

    def resizeEvent(self, event) -> None:
        """Re-elide the message to fit the new width.

        :param event: The Qt resize event.
        """
        super().resizeEvent(event)
        self._show_elided()

    def _show_elided(self) -> None:
        """Display the full message cut with a trailing ellipsis to the current width."""
        elided = self.fontMetrics().elidedText(self._full_text, QtCore.Qt.TextElideMode.ElideRight, self.width())
        super().setText(elided)


class PhysPlotStatusBar(QtWidgets.QFrame):
    """Show the status message and dataset summary along the bottom of the window.

    The labels sit in one row with 12 px side margins, 6 px top and bottom margins and
    22 px between items; the status message stretches, the others keep their natural width.

    :ivar ready_dot: 10 px green circle, hidden in Simple mode.
    :ivar status: :class:`ElidedLabel` with the ``Status: <message>`` text.
    :ivar rows: ``Rows: <n>`` label.
    :ivar columns: ``Columns: <n>`` label.
    :ivar file: ``File: <name>`` label.
    :ivar workflow: ``Workflow: <name>`` label, hidden in Simple mode.
    :ivar mode: ``Mode: <mode>`` label, hidden in Simple mode.
    """
    def __init__(self, parent=None):
        """Build the status bar with its initial texts.

        It starts as ``Status: Ready``, ``Rows: 0``, ``Columns: 0``, ``File: -``,
        ``Workflow: Untitled`` and ``Mode: Simple``, with every item visible until the
        first :meth:`update_state` call.

        :param parent: Optional Qt parent widget.
        """
        super().__init__(parent)
        self.setObjectName("StatusBar")
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(22)
        self.ready_dot = QtWidgets.QLabel()
        self.ready_dot.setFixedSize(10, 10)
        self.ready_dot.setStyleSheet("background:#1fb34f;border-radius:5px;")
        self.status = ElidedLabel("Status: Ready")
        self.rows = QtWidgets.QLabel("Rows: 0")
        self.columns = QtWidgets.QLabel("Columns: 0")
        self.file = QtWidgets.QLabel("File: -")
        self.workflow = QtWidgets.QLabel("Workflow: Untitled")
        self.mode = QtWidgets.QLabel("Mode: Simple")
        layout.addWidget(self.ready_dot)
        layout.addWidget(self.status, 1)
        for widget in (self.rows, self.columns, self.file, self.workflow, self.mode):
            layout.addWidget(widget)

    def update_state(self, state) -> None:
        """Refresh the counters, file names and mode from the shared GUI state.

        In Simple mode the ready dot and the ``Workflow`` and ``Mode`` labels are hidden,
        leaving only the message, row and column counts and file name; in Advanced mode
        they are all shown. The texts are then set from ``state``: ``Rows`` and
        ``Columns`` from its dataset size, ``File`` and ``Workflow`` from the file name
        (without folder) of ``current_file`` and ``workflow_file``, or ``-`` and
        ``Untitled`` when unset, and ``Mode`` from ``mode``. The status message is left
        unchanged.

        :param state: The window's :class:`~physplot_gui.app.gui_state.GuiState` (any
            object with ``mode``, ``row_count``, ``column_count``, ``current_file`` and
            ``workflow_file`` attributes works).
        """
        simple = state.mode == "Simple"
        self.ready_dot.setVisible(not simple)
        self.workflow.setVisible(not simple)
        self.mode.setVisible(not simple)
        self.rows.setText(f"Rows: {state.row_count}")
        self.columns.setText(f"Columns: {state.column_count}")
        self.file.setText(f"File: {Path(state.current_file).name if state.current_file else '-'}")
        self.workflow.setText(f"Workflow: {Path(state.workflow_file).name if state.workflow_file else 'Untitled'}")
        self.mode.setText(f"Mode: {state.mode}")

    def set_message(self, message: str) -> None:
        """Show ``Status: <message>`` in the elided status label.

        The main window uses this for results such as ``Plot generated`` or
        ``Sequence saved`` and for error summaries. A long message is elided on screen
        and shown in full in the tooltip.

        :param message: Text to show after ``Status:``.
        """
        self.status.setText(f"Status: {message}")
