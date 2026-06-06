import pandas as pd
from matplotlib.figure import Figure

from physplot import PhysPlot


def _nano_pp():
    pp = PhysPlot()
    pp.load(
        pd.DataFrame(
            {
                "Depth (nm)": [0, 50, 100, 150],
                "Load (mN)": [0, 1.2, 3.8, 7.1],
                "Hardness (GPa)": [0, 20, 24, 25],
                "Modulus (GPa)": [0, 350, 370, 380],
                "Stiffness (N/m)": [0, 1000, 1500, 1800],
            }
        ),
        loader="dataframe",
    )
    pp.get_active_dataset().metadata["dataset_type"] = "nanoindentation"
    return pp


def test_nanoindentation_plotter_handles_load_depth_columns():
    fig = _nano_pp().plot_with_module("nanoindentation", "load_depth")
    assert isinstance(fig, Figure)


def test_oliver_pharr_plotter_shows_load_depth_without_inventing_fit_data():
    fig = _nano_pp().plot_with_module("oliver_pharr", "load_depth_with_unloading_fit")
    assert isinstance(fig, Figure)
    assert getattr(fig, "physplot_warnings", None)
