import numpy as np
import pandas as pd
import pytest

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from physplot import PhysPlot
from physplot.plotting_modules.gallery import PLOT_CATEGORIES, PLOT_TYPES, roles_hint
from physplot.plotting_modules.registry import PlotterRegistry


def _dataset():
    rng = np.random.default_rng(0)
    gx, gy = np.meshgrid(np.linspace(-2, 2, 12), np.linspace(-2, 2, 10))
    x, y = gx.ravel(), gy.ravel()
    return pd.DataFrame(
        {
            "x": x,
            "y": np.sin(x) + y,
            "y2": np.cos(x),
            "z": np.exp(-(x**2 + y**2)),
            "u": -y,
            "v": x,
            "w": np.ones_like(x) * 0.5,
            "xerr": np.full_like(x, 0.05),
            "yerr": np.full_like(x, 0.1),
            "group": np.where(x > 0, "right", "left"),
            "label": [f"p{i}" for i in range(len(x))],
            "noise": rng.normal(size=len(x)),
        }
    )


def test_gallery_matches_matplotlib_plot_types_page():
    names = [category["name"] for category in PLOT_CATEGORIES]
    assert names == [
        "Lines, bars and markers",
        "Statistics",
        "Images, contours and fields",
        "Pie and polar charts",
        "3D plotting",
        "Specialty plots",
    ]
    assert sum(len(c["types"]) for c in PLOT_CATEGORIES) == 84
    # every type from https://matplotlib.org/stable/plot_types/ is present
    plot_types_page = {
        "line", "scatter", "bar", "stem", "fill_between", "stackplot", "stairs",
        "hist", "boxplot", "errorbar", "violinplot", "eventplot", "hist2d", "hexbin", "pie", "ecdf",
        "imshow", "pcolormesh", "contour", "contourf", "barbs", "quiver", "streamplot",
        "tricontour", "tricontourf", "tripcolor", "triplot",
        "bar3d", "fill_between3d", "plot3d", "quiver3d", "scatter3d", "stem3d",
        "plot_surface", "plot_trisurf", "voxels", "plot_wireframe",
    }
    assert plot_types_page <= set(PLOT_TYPES)
    assert roles_hint("fill_between") == "Uses: X, Y (Y2 optional)"
    basic = PlotterRegistry.default().get("basic")
    assert basic.plot_categories is PLOT_CATEGORIES
    assert {"scatter", "line", "scatter_line"} <= set(basic.supported_plot_types)


@pytest.mark.parametrize("plot_type", list(PLOT_TYPES))
def test_every_plot_type_renders_from_table_roles(plot_type):
    pp = PhysPlot()
    df = _dataset()
    if plot_type in ("pie", "donut", "nested_pie", "radar", "bar_categorical"):
        df = df.head(5).assign(y=[1, 2, 3, 4, 5])
    if plot_type == "sankey":
        df = df.head(4).assign(y=[3.0, -1.0, -1.0, -1.0])
    if plot_type == "voxels":
        df = df.head(8).assign(x=[0, 1, 0, 1, 0, 1, 0, 1], y=[0, 0, 1, 1, 0, 0, 1, 1], z=[0, 0, 0, 0, 1, 1, 1, 1])
    pp.load(df, loader="dataframe", dataset_name="gallery")
    pp.set_roles(x="x", y="y", y2="y2", z="z", u="u", v="v", w="w", xerr="xerr", yerr="yerr", group="group", label="label")
    figure = pp.plot_with_module("basic", plot_type)
    assert figure.axes
    figure.canvas.draw()
    plt.close(figure)
    assert pp.workflow[-1].plot_type == plot_type


def test_missing_role_is_reported_clearly():
    pp = PhysPlot()
    pp.load(pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]}), loader="dataframe", dataset_name="t")
    pp.set_roles(x="a", y="b")
    with pytest.raises(ValueError, match="role 'Z'"):
        pp.plot_with_module("basic", "contourf")


def _gui_window(frame):
    import os

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    pytest.importorskip("PyQt6")
    from physplot.qt_compat import QtWidgets
    from physplot_gui.app.main_window import MainWindow

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    window = MainWindow()
    window.state.load_dataframe(frame, name="grid")
    window.central_table.set_dataframe(window.state.dataframe, window.state.roles)
    window._refresh_all()
    return app, window, window.mode_manager.panels["Simple"]


def test_category_and_plot_type_menus_limit_roles_and_fill_them_in():
    frame = pd.DataFrame({"a": [0, 1, 0, 1], "b": [0, 0, 1, 1], "c": [1.0, 2.0, 3.0, 4.0], "name": list("pqrs")})
    app, window, panel = _gui_window(frame)
    panel.plotter.setCurrentIndex(panel.plotter.findData("basic"))
    categories = [panel.plot_category.itemText(i) for i in range(panel.plot_category.count())]
    assert categories[0] == "Lines, bars and markers" and "3D plotting" in categories
    assert not panel.plot_category.isHidden()

    # Choosing a category lists its types by their Matplotlib call.
    panel.plot_category.setCurrentText("Images, contours and fields")
    labels = [panel.plot_type.itemText(i) for i in range(panel.plot_type.count())]
    assert "contourf(X, Y, Z)" in labels
    assert panel.select_plot_type("contourf")
    assert panel.plot_roles_hint.text() == "Uses: X, Y, Z"

    # The table's role menus offer only what contourf uses.
    combo = window.central_table.table.cellWidget(0, 0)
    offered = [combo.itemText(i) for i in range(combo.count())]
    assert offered == ["Ignore", "X", "Y", "Z", "Group", "Label", "Batch Key"]

    # Picking the type fills in X, Y and Z on the free numeric columns, as protocol rows.
    panel._plot_type_chosen()
    assert window.state.roles == {"a": "X", "b": "Y", "c": "Z", "name": "Ignore"}
    assert [row["action"] for row in window.state.timeline[-3:]] == ["Set X", "Set Y", "Set Z"]
    panel._generate_plot()
    assert window.state.timeline[-1]["details"].startswith("Create basic contourf")

    # A role the next type does not use is kept but shown as unused.
    panel.select_plot_type("hist")
    combo = window.central_table.table.cellWidget(0, 2)
    assert combo.currentText() == "Z" and "Not used" in combo.toolTip()

    # Other plotters have no category menu and offer the roles they read.
    panel.plotter.setCurrentIndex(panel.plotter.findData("histogram"))
    assert panel.plot_category.isHidden()
    combo = window.central_table.table.cellWidget(0, 1)
    assert [combo.itemText(i) for i in range(combo.count())][:2] == ["Ignore", "Y"]
    window.close()
    app.processEvents()


def test_picking_a_plot_type_or_plotter_makes_the_table_roles_follow_it():
    frame = pd.DataFrame({"angle": [1.0, 2.0, 3.0], "intensity": [4.0, 5.0, 6.0], "err": [0.1, 0.1, 0.1]})
    app, window, panel = _gui_window(frame)
    panel.plotter.setCurrentIndex(panel.plotter.findData("basic"))
    panel.select_plot_type("scatter")
    panel._plot_type_chosen()
    assert window.state.roles == {"angle": "X", "intensity": "Y", "err": "Ignore"}

    # hist reads only Y: X is cleared, so the table shows exactly what the plot uses.
    panel.select_plot_type("hist")
    panel._plot_type_chosen()
    assert window.state.roles == {"angle": "Ignore", "intensity": "Y", "err": "Ignore"}
    combo = window.central_table.table.cellWidget(0, 0)
    assert [combo.itemText(i) for i in range(combo.count())] == ["Ignore", "Y", "Group", "Label", "Batch Key"]

    # Back to scatter: X returns to the first free numeric column.
    panel.select_plot_type("scatter")
    panel._plot_type_chosen()
    assert window.state.roles["angle"] == "X"

    # Other plotters follow their own role_requirements.
    panel.plotter.setCurrentIndex(panel.plotter.findData("errorbar"))
    panel.select_plot_type("y_errorbar")
    panel._plot_type_chosen()
    assert window.state.roles == {"angle": "X", "intensity": "Y", "err": "Y Error"}
    assert panel.plot_roles_hint.text() == "Uses: X, Y, Y Error"
    window.close()
    app.processEvents()
