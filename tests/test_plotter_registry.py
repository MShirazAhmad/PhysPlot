from physplot.plotting_modules import PlotterRegistry


def test_plotter_registry_lists_expected_plotters():
    registry = PlotterRegistry.default()
    plotters = {plotter.plotter_id: plotter for plotter in registry.list_plotters()}
    assert "basic" in plotters
    assert "histogram" in plotters
    assert "errorbar" in plotters
    assert "overlay" in plotters
    assert "subplot_grid" in plotters
    assert registry.list_plot_types("basic") == ["scatter", "line", "scatter_line"]
    assert registry.get("histogram").name == "Histogram Plotter"
