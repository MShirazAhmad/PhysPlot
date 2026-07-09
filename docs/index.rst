PhysPlot: Advanced Plotting Made Simple
=======================================

.. image:: _static/PhysPlotWide.png
   :alt: PhysPlot logo
   :align: center
   :width: 620px

PhysPlot is a scientific plotting and workflow automation application with a
spreadsheet-first PyQt6 graphical interface. It supports importing,
transforming, plotting, fitting, templating figure appearance, exporting
datasets, and replaying saved protocol sequences in headless workflows.

Main Features
-------------

- Spreadsheet-first data entry and import with explicit column-role dropdowns.
- Replayable protocol sequences for transformations, plotting, and batch runs.
- Simple Mode panels for importing data, transforming columns, and generating plots.
- Advanced Mode tabs for building a protocol sequence and running that sequence
  across folders.
- Figure Editor-based editing for Basic Plotter output.
- Reusable figure templates saved from **Figure Editor > PhysPlot > Save as Template** and selected from Simple Mode's **Template** dropdown.
- Custom fit functions through **Figure Editor > Fitting > Add Fit Function**.
- Backend plotting modules for headless use, notebooks, and bulk workflows.
- Native **Help** menu links for documentation, GitHub, issue reporting, and
  the About dialog.

Plugin System
-------------

PhysPlot supports plugin-based extension points for importing, transforming, fitting, and editing figures without editing core GUI files.
For a complete map of file locations, auto-loading behavior, and how to create
new loaders, functions, plotters, templates, and workflow files, see
:doc:`extensions/modularity`.

File Loader plugins
~~~~~~~~~~~~~~~~~~~

- Add ``.py`` files to ``fileloader/`` with ``title`` or ``DISPLAY_NAME`` and
  ``load_data(file_path)``.
- Built-in loaders include ``auto``, ``csv``, ``txt``, ``excel``,
  ``nanoindentation``, and ``dataframe``.
- Loaders are auto-discovered and appear in Simple Mode's **Data Importer**
  panel.

Transform Function plugins
~~~~~~~~~~~~~~~~~~~~~~~~~~

- Add ``.py`` files to ``functions/`` with ``DISPLAY_NAME``, ``DEFAULT_LABEL``, and ``transform(values)``.
- Built-in transform categories include identity, powers, reciprocal, logarithmic, exponential, and trigonometric operations.
- Functions are auto-discovered and shown in Simple Mode's **Apply Mathematical
  Transformation** panel.

Curve-Fitting plugins
~~~~~~~~~~~~~~~~~~~~~

- Add ``.py`` files to ``curvefitting/`` for polynomial or callable models.
- Files are discovered at startup and shown in the curve-fit configuration list.
- Use this for custom equations and domain-specific fitting workflows.

Project links
-------------

- `PhysPlot documentation home <https://physplot.readthedocs.io/>`_
- `PhysPlot repository <https://github.com/MShirazAhmad/PhysPlot>`_
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
