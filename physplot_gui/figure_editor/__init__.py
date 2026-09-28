import os

__version__ = "0.3.3"
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(CURRENT_DIR, "resources", "assets")
ICONS_DIR = os.path.join(CURRENT_DIR, "resources", "icons")
PLUGINS_DIR = os.path.join(CURRENT_DIR, "plugins")
# PhysPlot: the editor carries PhysPlot's name and icon only.
APP_NAME = "PhysPlot Figure Editor"
APP_ICON = os.path.join(os.path.dirname(os.path.dirname(CURRENT_DIR)), "physplot", "inc", "PhysPlot.png")
DOCS_URL = "https://physplot.readthedocs.io/"
ISSUES_URL = "https://github.com/MShirazAhmad/PhysPlot/issues"

# PhysPlot: the constants are defined before the plugins are imported, because the plugins
# package imports PLUGINS_DIR from here (upstream re-imported ``__init__`` to get around it).
import physplot_gui.figure_editor.plugins as plugins  # noqa: E402


def run(figure=None):
    from .main import main

    main(figure)
