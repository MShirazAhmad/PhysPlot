import os

from PyQt6.QtWidgets import (
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QLabel,
    QWidget,
    QPushButton,
    QHBoxLayout,
)
from PyQt6.QtCore import pyqtSignal as Signal
from PyQt6.QtGui import QIcon

from physplot_gui.figure_editor import CURRENT_DIR


#: PhysPlot: readable names for the figure parts shown in the tree and status bar.
FRIENDLY_CLASS_NAMES = {
    "PathCollection": "Scatter",
    "Line2D": "Line",
    "XAxis": "X axis",
    "YAxis": "Y axis",
    "XTick": "X tick",
    "YTick": "Y tick",
    "Rectangle": "Background",
    "Legend": "Legend",
    "Annotation": "Annotation",
    "Text": "Text",
    "Axes": "Axes",
    "Figure": "Figure",
    "PolyCollection": "Filled area",
    "LineCollection": "Lines",
    "BarContainer": "Bars",
}


def _short(text, limit=28):
    text = " ".join(str(text).split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def friendly_name(artist) -> str:
    """PhysPlot: a readable name for a figure part, e.g. ``Title "Intensity vs Angle"``."""
    cls = artist.__class__.__name__
    name = FRIENDLY_CLASS_NAMES.get(cls, cls)
    if cls == "Spine":
        name = f"{getattr(artist, 'spine_type', '')} spine".strip().capitalize()
    axes = getattr(artist, "axes", None)
    figure = getattr(artist, "figure", None)
    if cls == "Text" and figure is not None:
        if artist is getattr(figure, "_suptitle", None):
            name = "Figure title"
        for ax in getattr(figure, "axes", []):
            if artist is ax.xaxis.label:
                name = "X label"
            elif artist is ax.yaxis.label:
                name = "Y label"
            elif artist in (ax.title, getattr(ax, "_left_title", None), getattr(ax, "_right_title", None)):
                name = "Title"
    if cls == "Rectangle":
        if any(artist is ax.patch for ax in getattr(figure, "axes", [])):
            name = "Plot background"
        elif figure is not None and artist is figure.patch:
            name = "Figure background"
    parent_tick = getattr(artist, "_physplot_parent_tick", None)
    if parent_tick is not None:
        if artist in (parent_tick.tick1line, parent_tick.tick2line):
            name = "Tick mark"
        elif artist is parent_tick.gridline:
            name = "Grid line"
        elif artist in (parent_tick.label1, parent_tick.label2):
            name = "Tick label"
    if cls in ("XTick", "YTick"):
        return f'{name} "{_short(artist.label1.get_text())}"' if artist.label1.get_text() else name
    if cls == "FancyBboxPatch" and getattr(artist, "_physplot_in_legend", False):
        return "Legend frame"
    text = artist.get_text() if cls in ("Text", "Annotation") else ""
    if text:
        return f'{name} "{_short(text)}"'
    label = artist.get_label() if hasattr(artist, "get_label") else ""
    if isinstance(label, str) and label and not label.startswith("_"):
        return f"{name} – {_short(label)}"
    return name


#: Layout helpers inside a legend; not useful to edit.
LAYOUT_CLASSES = {"VPacker", "HPacker", "TextArea", "DrawingArea", "OffsetBox", "PaddedBox"}


def is_hidden_part(artist) -> bool:
    """PhysPlot: parts left out of the tree.

    PhysPlot's hidden helper artists, empty text slots, legend layout boxes, and the
    parts of a tick that are switched off (for example the second label of each tick).
    """
    if artist.__class__.__name__ in LAYOUT_CLASSES:
        return True
    if getattr(artist, "_physplot_parent_tick", None) is not None and not artist.get_visible():
        return True
    label = artist.get_label() if hasattr(artist, "get_label") else ""
    if isinstance(label, str) and label.startswith("_physplot_template"):
        return True
    if artist.__class__.__name__ == "Text" and not artist.get_text():
        return True
    return False


class FigureExplorer(QWidget):
    itemSelected = Signal(object)
    refreshTree = Signal()

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Figure Explorer"))
        header_layout.addStretch()
        reload_button = QPushButton("Reload")
        reload_button.setToolTip("Reload from file")
        reload_button.setIcon(
            QIcon(os.path.join(CURRENT_DIR, "resources/icons/refresh_icon.png"))
        )
        reload_button.clicked.connect(self.refreshTree.emit)
        header_layout.addWidget(reload_button)
        layout.addLayout(header_layout)
        self.tree = QTreeWidget()
        self.tree.header().hide()
        self.tree.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.tree)
        self.setLayout(layout)

    def build_tree(self, figure, last_obj=None):
        self.tree.clear()
        self.tree.addTopLevelItem(QTreeWidgetItem(["Figure"]))
        root = self.tree.topLevelItem(0)
        root.reference = figure
        for i, item in enumerate(root.reference.get_children()):
            self.add_item(root, item, last_obj)
        self.tree.expandItem(root)

    def add_item(self, parent, child, last_obj):
        if is_hidden_part(child):
            return
        label = friendly_name(child)
        parent.addChild(QTreeWidgetItem([label]))
        root = parent.child(parent.childCount() - 1)
        root.setToolTip(0, f"{label} ({child.__class__.__name__})")
        root.reference = child

        if last_obj is not None and last_obj == child:
            self.tree.setCurrentItem(root)

        for i, item in enumerate(root.reference.get_children()):
            if child.__class__.__name__ in ("XTick", "YTick"):
                item._physplot_parent_tick = child
            if child.__class__.__name__ == "Legend":
                item._physplot_in_legend = True
            self.add_item(root, item, last_obj)

    def on_item_clicked(self, item):
        self.itemSelected.emit(item.reference)

    def select_object(self, obj) -> bool:
        """PhysPlot: highlight the tree item for ``obj`` (expanding its parents).

        Returns ``True`` when ``obj`` is in the tree. Does not emit ``itemSelected``.
        """
        stack = [self.tree.topLevelItem(i) for i in range(self.tree.topLevelItemCount())]
        while stack:
            item = stack.pop()
            if getattr(item, "reference", None) is obj:
                parent = item.parent()
                while parent is not None:
                    parent.setExpanded(True)
                    parent = parent.parent()
                self.tree.setCurrentItem(item)
                self.tree.scrollToItem(item)
                return True
            stack.extend(item.child(i) for i in range(item.childCount()))
        return False
