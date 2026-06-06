PhysPlot: Advanced Plotting Made Simple
=======================================

.. image:: _static/PhysPlotWide.png
   :alt: PhysPlot logo
   :align: center
   :width: 620px

PhysPlot is a scientific plotting software with a graphical user interface, designed to produce publication-ready 2D plots. It supports vector and bitmap outputs and allows importing, transforming, plotting, fitting, and exporting datasets.

Plugin System
-------------

PhysPlot supports plugin-based extension points for importing, transforming, and fitting data without editing core GUI files.

File Loader plugins
~~~~~~~~~~~~~~~~~~~

- Add ``.py`` files to ``fileloader/`` with ``title`` and ``load_data(file_path)``.
- The default loader keeps CSV/XLSX/TXT/TSV support.
- Loaders are auto-discovered and appear in both:

  - **Settings > File Loader**
  - The **Data Loader** dropdown above **Import Data**

Transform Function plugins
~~~~~~~~~~~~~~~~~~~~~~~~~~

- Add ``.py`` files to ``functions/`` with ``DISPLAY_NAME``, ``DEFAULT_LABEL``, and ``transform(values)``.
- Built-in transform categories include identity, powers, reciprocal, logarithmic, exponential, and trigonometric operations.
- Functions are auto-discovered and shown in the top-bar **Functions** menu and transform dropdown.

Curve-Fitting plugins
~~~~~~~~~~~~~~~~~~~~~

- Add ``.py`` files to ``curvefitting/`` for polynomial or callable models.
- Files are discovered at startup and shown in the curve-fit configuration list.
- Use this for custom equations and domain-specific fitting workflows.

Project links
-------------

- `PhysPlot documentation home <https://physplot.readthedocs.io/>`_
- `Feature requests and bug reports <https://github.com/MShirazAhmad/PhysPlot/issues>`_

.. toctree::
   :maxdepth: 2
   :caption: Contents

   installation
   getting_started
   user_guide/data_entry
   user_guide/data_import
   user_guide/data_manipulation
   user_guide/plot_generation
   user_guide/curve_fitting
   user_guide/plot_customization
   user_guide/data_export
   extensions/index
   api/index
   reference/classes
   CODEX_PROJECT_GUIDE
