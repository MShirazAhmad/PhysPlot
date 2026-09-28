import os
import pickle
import json

from PyQt6.QtWidgets import (
    QWidget,
    QMessageBox,
)
from PyQt6.QtCore import pyqtSignal as Signal

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np

from physplot_gui.figure_editor import CURRENT_DIR
from physplot_gui.figure_editor.property_inspector import PropertyInspector
from physplot_gui.figure_editor.figure_explorer import FigureExplorer, friendly_name, is_hidden_part


class FigureManager(QWidget):
    updateLabel = Signal(str)
    selectionMessage = Signal(str)  # PhysPlot: what a click on the figure selected
    """
    A class that manages the creation, loading, and modification of figures.

    Attributes:
        pi (PropertyInspector): An instance of the PropertyInspector class.
        fe (FigureExplorer): An instance of the FigureExplorer class.
        figure (Figure): The matplotlib Figure object.
        canvas (FigureCanvas): The canvas for displaying the figure.
        unsaved_changes (bool): A flag indicating whether there are unsaved changes.
        file_name (str): The name of the file associated with the figure.
        structure (dict): The JSON figure property structure.

    Signals:
        itemSelected: A signal emitted when an item is selected in the FigureExplorer.
        propertyChanged: A signal emitted when a property is changed in the PropertyInspector.
    """

    def __init__(self, preferences, figure=None) -> None:
        """
        Initializes a new instance of the FigureManager class.
        """
        super().__init__()
        self.preferences = preferences

        self.pi = PropertyInspector()
        self.fe = FigureExplorer()

        # Setup the figure and canvas
        self.unsaved_changes = False
        self.file_name = None
        if figure is not None:
            # PhysPlot: edit the given figure itself (it is shared with PhysPlot's plot
            # window), not a copy of its attributes in a new Figure.
            self.figure = figure
            self.canvas = FigureCanvas(self.figure)
        else:
            self.figure = Figure()
            self.canvas = FigureCanvas(self.figure)
            self.new_figure()
            self.figure.__dict__.update(create_default_figure().__dict__)
        self.canvas.draw()
        self.fe.build_tree(self.figure)

        # PhysPlot: click a part of the figure to edit its properties; clicking the same
        # spot again cycles through the parts that overlap there.
        self._last_click = None  # ((x, y), parts under the mouse, index shown)
        self.canvas.mpl_connect("button_press_event", self.on_canvas_press)

        # Connect signals to slots
        self.fe.itemSelected.connect(self.on_item_selected)
        self.fe.refreshTree.connect(lambda: self.load_figure(self.file_name))
        self.pi.propertyChanged.connect(self.on_property_changed)
        self.selected_obj = None

        # Load the JSON figure property structure as a dict
        self.load_json_structure()

    def load_json_structure(self) -> None:
        """
        Loads the JSON figure property structure from a file.
        """
        json_file = os.path.join(CURRENT_DIR, "structure.json")
        with open(json_file) as f:
            self.structure = json.load(f)
        if self.preferences.get("debug"):
            print(f"Loaded structure: {json_file}")

    def load_figure(self, file_name) -> None:
        """
        Loads a figure from a file.

        Args:
            file_name (str): The name of the file to load the figure from.
        """
        if file_name is None:
            return
        self.new_figure()
        with open(file_name, "rb") as f:
            data = pickle.load(f)
        self.figure.__dict__.update(data.__dict__)
        self.canvas.draw()
        self.unsaved_changes = False
        self.updateLabel.emit(
            file_name.split("/")[-1] if self.file_name is not None else "New Figure"
        )
        self.fe.build_tree(self.figure)
        self.pi.clear_properties()
        self.file_name = file_name
        if self.preferences.get("debug"):
            print(f"Loaded figure from {file_name}")

    def save_figure(self, file_name) -> None:
        """
        Saves the figure to a file.

        Args:
            file_name (str): The name of the file to save the figure to.
        """
        with open(file_name, "wb") as f:
            pickle.dump(self.figure, f)
        self.unsaved_changes = False
        self.updateLabel.emit(file_name.split("/")[-1])
        if self.preferences.get("debug"):
            print(f"Saved figure to {file_name}")

    def new_figure(self) -> None:
        """
        Creates a new empty figure.
        """
        self.figure.clear()
        self.file_name = None
        self.unsaved_changes = False
        self.updateLabel.emit("New Figure")
        self.canvas.draw()
        self.fe.build_tree(self.figure)
        if self.preferences.get("debug"):
            print("Created new figure")

    def artists_at(self, event) -> list:
        """PhysPlot: return the editable figure parts under a mouse event, most specific first.

        Every visible artist in the figure tree whose class the Property Inspector knows
        (``structure.json``) and whose ``contains(event)`` is true is returned, deepest in the
        tree first (a tick label before its axis, a line before its axes), then by z-order.
        The figure itself is always last.
        """
        hits = []

        def walk(artist, depth):
            for child in artist.get_children():
                if child is artist:
                    continue
                if child.get_visible() and child.__class__.__name__ in self.structure and not is_hidden_part(child):
                    try:
                        inside = child.contains(event)[0]
                    except Exception:
                        inside = False
                    if inside:
                        hits.append((depth, child.get_zorder(), child))
                walk(child, depth + 1)

        walk(self.figure, 1)
        hits.sort(key=lambda hit: (-hit[0], -hit[1]))
        found = []
        for _, _, artist in hits:
            if not any(artist is seen for seen in found):
                found.append(artist)
        if self.figure.__class__.__name__ in self.structure:
            found.append(self.figure)
        return found

    @staticmethod
    def describe_artist(artist) -> str:
        """PhysPlot: a readable name for a figure part, e.g. ``Title "Intensity vs Angle"``."""
        return friendly_name(artist)

    def on_canvas_press(self, event) -> None:
        """PhysPlot: on a click (left or right), open the properties of the part under the mouse.

        The most specific editable part under the mouse (for example the title rather than
        the axes behind it, or a fit line drawn over the data) is shown in the Property
        Inspector straight away. Clicking the same spot again (within 4 pixels, with the
        same parts under it) shows the next part there, wrapping round; ``selectionMessage``
        names it, for example ``Line2D - fit (1 of 3)``.
        """
        if event.button not in (1, 3):
            return
        artists = self.artists_at(event)
        if not artists:
            return
        index = 0
        if self._last_click is not None:
            (x, y), previous, previous_index = self._last_click
            same_spot = abs(event.x - x) <= 4 and abs(event.y - y) <= 4
            same_parts = len(previous) == len(artists) and all(a is b for a, b in zip(previous, artists))
            if same_spot and same_parts:
                index = (previous_index + 1) % len(artists)
        self._last_click = ((event.x, event.y), artists, index)
        self.select_artist(artists[index])
        message = self.describe_artist(artists[index])
        if len(artists) > 1:
            message += f" ({index + 1} of {len(artists)}, click again for the next)"
        self.selectionMessage.emit(message)

    def select_artist(self, obj) -> None:
        """PhysPlot: show ``obj`` in the Property Inspector and highlight it in the explorer."""
        if not self.fe.select_object(obj):
            self.fe.build_tree(self.figure, obj)
        self.on_item_selected(obj)

    def on_item_selected(self, obj) -> None:
        """
        Handles the selection of an item in the FigureExplorer.

        Args:
            obj: The selected object.
        """
        self.selected_obj = obj
        self.pi.clear_properties()
        properties = self.structure[obj.__class__.__name__]["attributes"]

        for property_name in properties:
            prop = properties[property_name]
            value_type = prop["type"]
            value_options = prop["value_options"] if "value_options" in prop else None
            types = prop["types"] if "types" in prop else None
            get_index = prop["get_index"] if "get_index" in prop else None
            value = self.get_value(obj, prop["get"], get_index)

            if value_type == "tuple" or value_type == "dict":
                types = prop["types"]

            self.pi.add_property(property_name, value_type, value, value_options, types)

        if self.preferences.get("debug"):
            print(f"Selected {obj.__class__.__name__}")

    def on_property_changed(self, property_name: str, value) -> None:
        """
        Handles the change of a property in the PropertyInspector.

        Args:
            property_name (str): The name of the property that changed.
            value: The new value of the property.
        """
        obj = self.selected_obj
        obj_class = obj.__class__.__name__
        prop = self.structure[obj_class]["attributes"][property_name]
        set_method = prop["set"]

        if "set_parameter" in prop:
            parameter = prop["set_parameter"]
            value = {parameter: value}
        self.set_value(obj, set_method, value)

        self.canvas.draw()
        self.unsaved_changes = True
        self.updateLabel.emit(
            f"{self.file_name.split('/')[-1] if self.file_name is not None else 'New Figure'} *"
        )

        if self.preferences.get("debug"):
            print(f"Changed {property_name} to {value} on {obj_class}")

    def delete_obj(self) -> None:
        """
        Deletes the selected object and removes it from the figure explorer.
        """
        if self.selected_obj is None:
            return

        self.attempt_delete(self.selected_obj)
        self.canvas.draw()
        self.unsaved_changes = True
        self.updateLabel.emit(
            f"{self.file_name.split('/')[-1] if self.file_name is not None else 'New Figure'} *"
        )

        self.fe.build_tree(self.figure)
        self.selected_obj = None

        if self.preferences.get("debug"):
            print(f"Attempting to delete {self.selected_obj}")

    def attempt_delete(self, obj) -> None:
        """
        Attempts to delete an object, if it can be.

        Args:
            obj: The object to delete.
        """
        try:
            obj.remove()
        except NotImplementedError:
            QMessageBox.critical(self, "Error", "Cannot delete this item.")

    def get_value(self, obj, attr_path: str, index: None | int = None):
        """
        Gets the value of an attribute of an object.

        Args:
            obj: The object.
            attr_path (str): The path to the attribute.
            index: The index to use if the attribute is iterable.

        Returns:
            The value of the attribute.
        """
        attrs = attr_path.split(".")
        for attr in attrs:
            obj = getattr(obj, attr)
            if callable(obj):
                obj = obj()
        if callable(obj):
            value = obj()
        else:
            value = obj
        if index is not None:
            try:
                value = value[index]
            except TypeError:
                if self.preferences.get("debug"):
                    print(f"Indexing failed on {value} for {obj}")
                value = value
        return value

    def set_value(self, obj, attr_path: str, value) -> None:
        """
        Sets the value of an attribute of an object. Attempts to discern whether
        `attr_path` is is an attribute or setter method.

        Args:
            obj: The object.
            attr_path (str): The path to the attribute.
            value: The new value of the attribute.
        """
        attrs = attr_path.split(".")
        for attr in attrs[:-1]:
            obj = getattr(obj, attr)
            if callable(obj):
                obj = obj()
        if type(value) == dict:
            if self.preferences.get("debug"):
                print(f"Calling {attr_path}({value}) on {obj}")
            getattr(obj, attrs[-1])(**value)
        elif callable(getattr(obj, attrs[-1])):
            if self.preferences.get("debug"):
                print(f"Calling {attr_path}({value}) on {obj}")
            getattr(obj, attrs[-1])(value)
        else:
            if self.preferences.get("debug"):
                print(f"Setting {attr_path} to {value} on {obj}")
            setattr(obj, attrs[-1], value)


def create_default_figure():
    """
    Creates a default figure.

    Returns:
        The default figure.
    """
    x = np.linspace(0, 10, 100)
    y = np.sin(x)

    np.random.seed(0)
    x_scatter = np.random.rand(100)
    y_scatter = np.random.rand(100)
    colors = np.random.rand(100)
    sizes = 1000 * np.random.rand(100)

    categories = ["A", "B", "C", "D"]
    values = np.random.rand(len(categories))

    data = np.random.randn(100, 4)

    # Create the figure
    fig, axs = plt.subplots(2,2)
    fig.suptitle("New Figure", fontsize=16, label="suptitle")

    # Line plot
    axs[0, 0].plot(x, y, marker="o", linestyle="-", color="b", label="sin(x)")
    axs[0, 0].set_label("Line Plot")
    axs[0, 0].set_title("Line Plot")
    axs[0, 0].legend()
    axs[0, 0].set_xscale("symlog")
    axs[0, 0].set_xlabel("x")
    axs[0, 0].set_ylabel("sin(x)")

    for spine in axs[0, 0].spines:
        if spine == "top" or spine == "right":
            axs[0, 0].spines[spine].set_visible(False)
        if spine == "bottom":
            axs[0, 0].spines[spine].set_bounds(min(x), max(x))
        if spine == "left":
            axs[0, 0].spines[spine].set_bounds(min(y), max(y))

    # Scatter plot
    scatter = axs[0, 1].scatter(
        x_scatter, y_scatter, c=colors, s=sizes, alpha=0.3, cmap="viridis"
    )
    axs[0, 1].set_label("Scatter Plot")
    axs[0, 1].set_title("Scatter Plot")
    axs[0, 1].annotate(
        "Example Annotation",
        xy=(0.5, 0.5),
        xytext=(0.7, 0.7),
        arrowprops=dict(
            arrowstyle="->", connectionstyle="arc3,rad=0.5", facecolor="black", lw=0.5
        ),
    )
    fig.colorbar(scatter, ax=axs[0, 1])

    # Bar chart
    axs[1, 0].bar(
        categories, values, color=["lightgray", "darkgray", "lightgray", "lightgray"]
    )
    axs[1, 0].set_label("Bar Chart")
    axs[1, 0].set_title("Bar Chart")
    axs[1, 0].grid(True, axis="y", color="white")

    for spine in axs[1, 0].spines:
        axs[1, 0].spines[spine].set_visible(False)

    # Box plot
    axs[1, 1].boxplot(data)
    axs[1, 1].set_label("Box Plot")
    axs[1, 1].set_title("Box Plot")

    return fig
