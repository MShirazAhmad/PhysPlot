"""Top-right mode switcher.

:class:`ModeSwitcher` is the small ``Mode: [Simple] [Advanced]`` control on the right of the
PhysPlot header, opposite the LSF and PhysLab logos and beside the centred PhysPlot logo.
It only reports clicks; the main window decides what a mode change does.

How a mode change flows through the GUI:

1. The user clicks **Simple** or **Advanced** (or uses *View > Simple Mode* ``Ctrl+1`` /
   *View > Advanced Mode* ``Ctrl+2``, which bypass this widget).
2. :attr:`ModeSwitcher.mode_changed` carries the mode name to
   :meth:`physplot_gui.app.mode_manager.ModeManager.set_mode`, which shows the matching
   panel below the table.
3. The mode manager's own ``mode_changed`` reaches ``MainWindow._mode_changed``, which
   stores the mode in :class:`~physplot_gui.app.gui_state.GuiState`, calls
   :meth:`ModeSwitcher.set_mode` so the highlighted button follows, resets the status
   message to ``Ready`` and refreshes all panels and the status bar.

The active button is highlighted through the ``activeMode`` dynamic property, which the
application stylesheet (:mod:`physplot_gui.style.theme`) paints with the blue primary
button style.
"""

from physplot.qt_compat import QtCore, QtWidgets


class ModeSwitcher(QtWidgets.QWidget):
    """Show a ``Mode:`` label followed by one checkable button per GUI mode.

    Signals:

    * ``mode_changed(str mode)``: emitted with ``"Simple"`` or ``"Advanced"`` whenever the
      matching button is clicked, even if that mode is already active.

    ``MODES`` lists the available modes in button order: ``("Simple", "Advanced")``.

    :ivar buttons: Mapping of mode name to its ``QPushButton``.
    """
    mode_changed = QtCore.pyqtSignal(str)

    MODES = ("Simple", "Advanced")

    def __init__(self, parent=None):
        """Build the label and buttons, laid out in a row with 6 px spacing.

        The widget starts with **Simple** highlighted.

        :param parent: Optional Qt parent widget.
        """
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
        """Highlight the button for ``mode`` and un-highlight the others.

        Only the buttons' look changes; :attr:`mode_changed` is not emitted. Each button is
        checked or unchecked and its ``activeMode`` property set to match, then its style
        is re-polished so the stylesheet rule for ``activeMode="true"`` takes effect at
        once. A name not in :attr:`MODES` leaves every button un-highlighted.

        :param mode: ``"Simple"`` or ``"Advanced"``.
        """
        for name, button in self.buttons.items():
            active = name == mode
            button.setChecked(active)
            button.setProperty("activeMode", active)
            button.style().unpolish(button)
            button.style().polish(button)
