import pandas as pd
from matplotlib.figure import Figure

from physplot import PhysPlot


def _loaded_pp():
    pp = PhysPlot()
    pp.load(
        pd.DataFrame(
            {
                "Time": [0, 1, 2, 3],
                "Voltage": [1.0, 2.0, 4.0, 8.0],
                "Error": [0.1, 0.2, 0.2, 0.3],
                "Group": ["A", "A", "B", "B"],
            }
        ),
        loader="dataframe",
    )
    pp.set_roles(x="Time", y="Voltage", yerr="Error", group="Group")
    return pp


def test_basic_plotter_returns_matplotlib_figure():
    fig = _loaded_pp().plot_with_module("basic", "scatter")
    assert isinstance(fig, Figure)


def test_histogram_plotter_returns_matplotlib_figure():
    fig = _loaded_pp().plot_with_module("histogram", "histogram")
    assert isinstance(fig, Figure)


def test_errorbar_plotter_returns_matplotlib_figure_when_y_error_exists():
    fig = _loaded_pp().plot_with_module("errorbar", "y_errorbar")
    assert isinstance(fig, Figure)


def test_overlay_and_subplot_plotters_return_figures():
    pp = _loaded_pp()
    assert isinstance(pp.plot_with_module("overlay", "overlay_by_group"), Figure)
    assert isinstance(pp.plot_with_module("subplot_grid", "subplots_by_group"), Figure)
