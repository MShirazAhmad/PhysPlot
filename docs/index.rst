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

Install on macOS with one command (details in :doc:`installation`):

.. code-block:: bash

   curl -fsSL https://raw.githubusercontent.com/MShirazAhmad/PhysPlot/indevelopment/scripts/install_macos.sh | bash

Video tutorials
---------------

Short live recordings, one per feature, are on YouTube in two playlists:
`PhysPlot Basics <https://www.youtube.com/playlist?list=PLPkYnHekjU24>`_ (Simple Mode)
and `PhysPlot Advanced <https://www.youtube.com/playlist?list=PLelbbYnCXEdU>`_
(protocols, bulk runs, writing file loaders and plotter modules). Every video is
listed in :doc:`ui/videos`.

Main Features
-------------

- Spreadsheet-first data entry and import with explicit column-role dropdowns.
- Instrument exports load directly: Malvern Panalytical ``.xrdml`` and CSV,
  EDAX EDS maps and SmartQuant tables, EMSA ``.msa`` spectra, PHI XPS scans,
  Rigaku ``.ras`` scans, TA Instruments TGA/DSC exports, JCAMP-DX spectra, and plain
  CSV/TXT/Excel tables.
- Replayable protocol sequences: every import, transformation (including plugin
  functions such as ``XRD: Baseline Remove``), role change, and plot is recorded
  and can be replayed, exported as Python, and run over whole folders.
- Simple Mode panels for importing data, transforming columns, and generating plots.
- Advanced Mode tabs for building and editing the protocol (**Build Protocol**)
  and running it across folders (**Run Sequence**).
- Figure Editor-based editing for Basic Plotter output.
- Reusable figure templates saved from **Figure Editor > PhysPlot > Save as Template**
  and selected from Simple Mode's **Template** dropdown.
- Custom fit functions through **Figure Editor > Fitting > Add Fit Function**, or a
  least-squares fit from the Plotter Module.
- Backend API and ``physplot`` command line for headless use, notebooks, and bulk workflows.
- Native **Help** menu links for documentation, GitHub, issue reporting, and
  the About dialog.

Plugin System
-------------

PhysPlot supports plugin-based extension points for importing, transforming, fitting, and editing figures without editing core GUI files.
Put your own files in ``Documents/PhysPlot/config/<folder>/`` (**File > Open Config
Folder**); they override bundled files with the same name. For a complete map of
file locations, auto-loading behavior, and how to create new loaders, functions,
plotters, templates, and workflow files, see :doc:`extensions/modularity`.

File Loader plugins
~~~~~~~~~~~~~~~~~~~

- Add ``.py`` files to ``config/data_importers/`` with ``title`` and
  ``load_data(file_path)``, and optionally ``COLUMN_NAMES``,
  ``DEFAULT_COLUMN_ROLES``, and ``FILE_EXTENSIONS``.
- A plugin that declares ``FILE_EXTENSIONS`` (for example ``[".ras"]``) is used
  by **Auto Loader**, by replayed sequences, and by bulk runs for those files.
- Worked examples with raw files, loader code and GUI results (Rigaku ``.ras`` XRD
  scans, TA Instruments TGA/DSC exports, JCAMP-DX spectra) are in
  :doc:`extensions/fileloading`.
- Built-in loaders: ``auto``, ``csv``, ``txt``, ``excel``, ``nanoindentation``,
  ``xrdml``, and ``dataframe``.
- Loaders appear in Simple Mode's **Data Importer** panel.

Transform Function plugins
~~~~~~~~~~~~~~~~~~~~~~~~~~

- Add ``.py`` files to ``config/transformations/`` with ``transform(values)`` and
  an optional ``DISPLAY_NAME`` (the menu label).
- Bundled functions include identity, powers, reciprocal, logarithmic,
  exponential, trigonometric, and XRD baseline removal.
- Functions appear in Simple Mode's **2. Mathematical Transformation** panel and
  are recorded as replayable protocol steps.

Curve-Fitting plugins
~~~~~~~~~~~~~~~~~~~~~

- Add ``.py`` files to ``config/fit_functions/`` for polynomial or callable models.
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
   ui/videos
   ui/sequence_walkthrough
   ui/index
   user_guide/data_entry
   user_guide/data_import
   user_guide/data_manipulation
   user_guide/protocol_sequences
   user_guide/plot_generation
   user_guide/curve_fitting
   user_guide/plot_customization
   user_guide/data_export
   extensions/index
   api/index
   reference/classes
   CODEX_PROJECT_GUIDE
