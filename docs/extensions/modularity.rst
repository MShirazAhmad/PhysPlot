Modularity and Auto-Loading Map
===============================

PhysPlot is intentionally modular. Most user extensions are ordinary Python or
JSON files placed in predictable folders. The GUI scans these locations at
startup, when the user clicks a reload button, or after
**File > Reload Config Modules**.

Every ``config/`` folder below has a per-user twin in
``Documents/PhysPlot/config/`` (created on first launch and seeded by the
Windows installer; relocate it with ``PHYSPLOT_USER_DIR``). The user copy is
searched first and a file with the same name there overrides the bundled one,
so modules can be added, edited, or removed without reinstalling.

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
     - ``config/data_importers/*.py``
     - Scanned at GUI startup by ``physplot_gui.app.plugin_discovery``
     - Simple Mode **Data Importer**
   * - Built-in loaders
     - ``physplot/loaders/``
     - Registered by the backend loader registry
     - GUI loader list and backend API
   * - User transform functions
     - ``config/transformations/*.py``
     - Scanned at GUI startup by ``physplot_gui.app.plugin_discovery``
     - Simple Mode **2. Mathematical Transformation**
   * - Built-in transforms
     - ``physplot/core/transformations.py``
     - Listed by the backend transformation registry
     - GUI transform dropdown and backend API
   * - Built-in plotter modules
     - ``physplot/plotting_modules/``
     - Registered by ``PlotterRegistry.default()``
     - Simple Mode **Plotter Module** and headless workflows
   * - User plotter modules
     - ``config/plotter_modules/*.py``
     - Registered by ``PlotterRegistry.default()`` through ``physplot.plotting_modules.user_modules``
     - Simple Mode **Plotter Module** and ``PlotModuleStep``
   * - Plot-type presets
     - ``config/plot_types/*.json``
     - Merged into ``PlotterRegistry.list_plot_types()`` and ``resolve_plot_type()``
     - Simple Mode **Plot Type** and ``PlotModuleStep(plot_type=...)``
   * - Loader-owned plotters
     - Declared inside ``config/data_importers/*.py``
     - Read from ``PLOTTERS`` / ``PLOTTER_MODULES`` / ``ALLOWED_PLOTTERS``
     - Simple Mode **Plotter Module**
   * - Figure templates
     - ``config/templates/*.json`` by default
     - Scanned by ``physplot_gui.plot_styles.list_style_modules()``
     - Simple Mode **Template** dropdown after **Reload**
   * - Curve-fit plugins
     - ``config/fit_functions/*.py``
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
   * - Complete reusable sequences
     - ``config/sequences/*.py`` by default
     - Imported by ``physplot.workflow.load_workflow_source()``
     - **Protocol > Import/Export Sequence.py**
   * - Protocol modules
     - ``config/protocol_modules/*.py``
     - Discovered by ``physplot.workflow.discover_protocol_modules()``
     - **Protocol > Insert Protocol Module** appends their steps
   * - Transformation pipelines
     - ``config/pipelines/*.json`` by default
     - Imported/exported by Advanced pipeline actions
     - Reusable transformation-only pipelines

Startup Versus Reload
---------------------

All ``config/`` folders are scanned at startup. To pick up new or edited files
while the app is running use **File > Reload Config Modules**, which re-scans:

- ``config/data_importers/*.py``
- ``config/transformations/*.py``
- ``config/plotter_modules/*.py`` and ``config/plot_types/*.json``
- ``config/protocol_modules/*.py``
- ``config/templates/*.json`` and ``config/figureforge_fit_styles/*.json``
  (also refreshed by their **Reload** buttons in Simple Mode)

Legacy ``config/fit_functions/*.py`` models are read when the legacy fit list
is built.

Figure templates are different. They are JSON files and can be refreshed while
the app is open:

1. Save a template from **Figure Editor > PhysPlot > Save as Template**.
2. Return to PhysPlot.
3. Click **Reload** beside the **Template** dropdown.

Creating a New File Loader
--------------------------

Create a file such as:

.. code-block:: text

   config/data_importers/my_instrument_loader.py

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

   config/transformations/15_normalize.py

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

   config/templates/*.json

Custom location:

.. code-block:: bash

   export PHYSPLOT_STYLE_DIR=/path/to/templates

Workflow:

1. Generate a Basic Plotter figure.
2. Style it in the Figure Editor.
3. Choose **Figure Editor > PhysPlot > Save as Template**.
4. Back in PhysPlot, click **Reload** beside **Template**.
5. Select the template before generating a new plot.

Creating and Reusing Sequences
------------------------------

Complete protocol sequences are normal Python files saved under:

.. code-block:: text

   config/sequences/*.py

The sequence file should define ``WORKFLOW_STEPS`` or ``build_workflow()``.
Use **Protocol > Export Sequence.py** to save the current Build Protocol
sequence, and **Protocol > Import Sequence.py** or **Run Sequence > Sequence
File** to reload it later.

Use ``config/protocol_modules/`` for smaller reusable fragments. Each fragment
is itself a sequence file (``WORKFLOW_STEPS`` plus optional ``DISPLAY_NAME``
and ``DESCRIPTION``) and can be appended to the current Build Protocol
sequence with **Protocol > Insert Protocol Module**.

Creating and Reusing Pipelines
------------------------------

Transformation pipelines are JSON files saved under:

.. code-block:: text

   config/pipelines/*.json

Use the Advanced pipeline import/export actions for reusable transformation-only
pipelines. Use ``config/sequences/`` when the reusable file should also include
load, role, plotting, fitting, or bulk-run workflow steps.

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

Generated Workflow File Format
------------------------------

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
