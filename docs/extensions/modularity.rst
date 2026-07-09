Modularity and Auto-Loading Map
===============================

PhysPlot is intentionally modular. Most user extensions are ordinary Python or
JSON files placed in predictable folders. The GUI scans these locations at
startup or when the user clicks a reload button.

Where Files Live
----------------

.. list-table::
   :header-rows: 1
   :widths: 22 26 28 24

   * - Feature
     - File location
     - How it is loaded
     - Where it appears
   * - User file loaders
     - ``fileloader/*.py``
     - Scanned at GUI startup by ``physplot_gui.app.plugin_discovery``
     - Simple Mode **Data Importer**
   * - Built-in loaders
     - ``physplot/loaders/``
     - Registered by the backend loader registry
     - GUI loader list and backend API
   * - User transform functions
     - ``functions/*.py``
     - Scanned at GUI startup by ``physplot_gui.app.plugin_discovery``
     - Simple Mode **Apply Mathematical Transformation**
   * - Built-in transforms
     - ``physplot/core/transformations.py``
     - Listed by the backend transformation registry
     - GUI transform dropdown and backend API
   * - Built-in plotter modules
     - ``physplot/plotting_modules/``
     - Registered by ``PlotterRegistry.default()``
     - Simple Mode **Plotter Module** and headless workflows
   * - Loader-owned plotters
     - Declared inside ``fileloader/*.py``
     - Read from ``PLOTTERS`` / ``PLOTTER_MODULES`` / ``ALLOWED_PLOTTERS``
     - Simple Mode **Plotter Module**
   * - Figure templates
     - ``styling/*.json`` by default
     - Scanned by ``physplot_gui.plot_styles.list_style_modules()``
     - Simple Mode **Template** dropdown after **Reload**
   * - Curve-fit plugins
     - ``curvefitting/*.py``
     - Scanned for legacy fit model lists
     - Legacy curve-fit configuration
   * - Figure Editor fit function
     - No file required
     - Entered interactively as an expression
     - **Figure Editor > Fitting > Add Fit Function**
   * - LSQ plotter fit
     - Stored in workflow config, not a separate plugin file
     - Saved inside ``PlotModuleStep(config={"lsq_fit": ...})``
     - Simple Mode **Plotter Module**
   * - Generated workflows
     - User-selected ``Sequence.py`` / ``workflow.py``
     - Imported by ``physplot.workflow.load_workflow_source()``
     - **Protocol > Import/Export Sequence.py**

Startup Versus Reload
---------------------

Some files require an app restart because the GUI scans them once at startup:

- ``fileloader/*.py``
- ``functions/*.py``
- ``curvefitting/*.py``

Figure templates are different. They are JSON files and can be refreshed while
the app is open:

1. Save a template from **Figure Editor > PhysPlot > Save as Template**.
2. Return to PhysPlot.
3. Click **Reload** beside the **Template** dropdown.

Creating a New File Loader
--------------------------

Create a file such as:

.. code-block:: text

   fileloader/my_instrument_loader.py

Minimum structure:

.. code-block:: python

   import pandas as pd

   title = "My Instrument Loader"
   DEFAULT_COLUMN_ROLES = ["X", "Y"]


   def load_data(file_path):
       return pd.read_csv(file_path)

Restart PhysPlot. The loader appears in Simple Mode's **Data Importer** panel.

Creating a Loader-Owned Plotter
-------------------------------

A file loader can also declare plotters that are specific to that instrument or
data format.

.. code-block:: python

   def publication_plot(dataset, plot_type="publication_ready", config=None):
       import matplotlib.pyplot as plt

       fig, ax = plt.subplots()
       ax.plot(dataset.dataframe["Time"], dataset.dataframe["Signal"])
       ax.set_xlabel("Time")
       ax.set_ylabel("Signal")
       return fig


   PLOTTERS = [
       {
           "plotter_id": "my_instrument_publication",
           "name": "My Instrument Publication Plot",
           "plot_types": ["publication_ready"],
           "callable": publication_plot,
       }
   ]

Restart PhysPlot. The plotter appears in Simple Mode's **Plotter Module** list
when the loader plugin is discovered.

Creating a New Transform Function
---------------------------------

Create a file such as:

.. code-block:: text

   functions/15_normalize.py

Minimum structure:

.. code-block:: python

   import numpy as np

   DISPLAY_NAME = "Normalize"
   DEFAULT_LABEL = "Normalized"


   def transform(values):
       values = np.asarray(values, dtype=float)
       return values / np.nanmax(values)

Restart PhysPlot. The function appears in the transformation dropdown.

Creating and Reusing Figure Templates
-------------------------------------

Templates store styling, not data. They are JSON files with figure and axes
appearance settings.

Default location:

.. code-block:: text

   styling/*.json

Custom location:

.. code-block:: bash

   export PHYSPLOT_STYLE_DIR=/path/to/templates

Workflow:

1. Generate a Basic Plotter figure.
2. Style it in the Figure Editor.
3. Choose **Figure Editor > PhysPlot > Save as Template**.
4. Back in PhysPlot, click **Reload** beside **Template**.
5. Select the template before generating a new plot.

Creating a New Backend Plotter Module
-------------------------------------

Backend plotters live under:

.. code-block:: text

   physplot/plotting_modules/

They should subclass or follow ``BasePlotter`` and define:

- ``plotter_id``
- ``name``
- ``category``
- ``supported_plot_types``
- ``plot(dataset, plot_type=None, config=None)``

Built-in plotters are registered in the plotting-module registry. A backend
plotter is the right place for reusable scientific plotting logic that must run
in notebooks, command-line workflows, and bulk folder runs.

Generated Workflow Files
------------------------

Protocol files are normal Python. They contain ``WORKFLOW_STEPS`` made from
step classes such as ``LoadDataStep``, ``SetRoleStep``, ``TransformColumnStep``,
and ``PlotModuleStep``.

The LSQ plotter fit is saved directly in the plot step:

.. code-block:: python

   PlotModuleStep(
       plotter_id="basic",
       plot_type="scatter",
       config={
           "lsq_fit": {
               "enabled": True,
               "expression": "a*x + b",
               "parameters": "a,b",
               "initial": "1,0",
               "line_style": "--",
               "line_width": 2.0,
               "show_legend": True,
           }
       },
   )

Because workflows are Python files, they can be used in notebooks, scripts, and
headless CLI commands.
