Extension Guides
================

PhysPlot is designed so common scientific extensions can be added by creating
small Python or JSON files in predictable folders. You do not have to write them
yourself: every kind of module has a guide file written for AI assistants, and
:doc:`ai_assistant` shows how to get a finished module from ChatGPT, Claude,
Gemini, Copilot or any other assistant, and :doc:`ai_examples` shows a tested
example of every kind with sample data and the resulting plots. Each page below
ends with the same help for its own kind of module.

.. list-table::
   :header-rows: 1
   :widths: 30 30 40

   * - Module kind
     - Folder in ``Documents/PhysPlot/config/``
     - Page
   * - Data importers (file loaders)
     - ``data_importers/``
     - :doc:`fileloading`
   * - Mathematical transformations
     - ``transformations/``
     - :doc:`functions`
   * - Plotter modules and plot-type presets
     - ``plotter_modules/``, ``plot_types/``
     - :doc:`plotter_modules`
   * - Protocol sequences, protocol modules and pipelines
     - ``sequences/``, ``protocol_modules/``, ``pipelines/``
     - :doc:`protocol_files`
   * - Figure templates, fit-style presets and Figure Editor plugins
     - ``templates/``, ``figureforge_fit_styles/``, ``figureforge_plugins/``
     - :doc:`figure_extensions`
   * - Curve fits (typed models) and legacy fit-model files
     - ``fit_functions/`` (legacy only)
     - :doc:`curvefitting`

Put your files in ``Documents/PhysPlot/config/<folder>/``: **File → Open Config
Folder** opens it. PhysPlot searches that folder before its built-in one, so a
file there with the same name replaces the bundled module. Choose **File → Reload
Config Modules** (``Ctrl+Shift+R``) to load new or changed files without
restarting. :doc:`modularity` maps every folder to the code that loads it.

.. toctree::
   :maxdepth: 2

   modularity
   fileloading
   functions
   plotter_modules
   protocol_files
   figure_extensions
   curvefitting
