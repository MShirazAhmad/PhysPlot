"""Figure Editor plugin: journal-style ticks on every side of the axes.

Select the Figure (all axes), an Axes, or any part of one axes, then choose
Figure Editor > Ticks > Journal Ticks. A dialog asks for the tick direction.
The command draws major and minor ticks on the bottom, top, left and right
axes, with lengths and widths that suit a single-column figure.
"""

from matplotlib.axes import Axes
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QInputDialog, QMessageBox


class JournalTicks:
    name = "Journal Ticks"
    tooltip = "Ticks on all four sides with minor ticks, pointing in, out, or both."
    submenu = "Ticks"

    def run(self, obj):
        axes_list = self._axes_for(obj)
        if not axes_list:
            self._warn("Select the Figure, an Axes, or a part of an Axes first.")
            return

        direction, ok = QInputDialog.getItem(
            None, "Journal Ticks", "Tick direction:", ["in", "out", "inout"], 0, False
        )
        if not ok:
            return  # the user pressed Cancel

        try:
            for axes in axes_list:
                axes.minorticks_on()
                axes.tick_params(axis="both", which="both", direction=direction, top=True, right=True)
                axes.tick_params(axis="both", which="major", length=4.0, width=0.8)
                axes.tick_params(axis="both", which="minor", length=2.0, width=0.6)
        except Exception as exc:
            self._warn(str(exc))

    @staticmethod
    def _axes_for(obj):
        """Return the axes to change for the selected object (empty list if none)."""
        if isinstance(obj, Figure):
            return list(obj.get_axes())
        if isinstance(obj, Axes):
            return [obj]
        axes = getattr(obj, "axes", None)  # lines, spines, texts, XAxis, YAxis, legends
        if isinstance(axes, Axes):
            return [axes]
        return []

    @staticmethod
    def _warn(message):
        box = QMessageBox()
        box.setIcon(QMessageBox.Icon.Warning)
        box.setWindowTitle("Journal Ticks")
        box.setText("Could not change the ticks.")
        box.setInformativeText(message)
        box.exec()
