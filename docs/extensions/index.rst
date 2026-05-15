Extension Guides
================

PhysPlot is designed so common scientific extensions can be added by creating
small Python files in one of three folders:

- ``functions/`` for table-column transformations.
- ``curvefitting/`` for plot curve-fit models.
- ``fileloader/`` for importing new data formats.

These extension points let users add new behavior without editing the main GUI
code. Each file is discovered when PhysPlot starts, so restart the application
after adding or changing an extension file.

.. toctree::
   :maxdepth: 2

   functions
   curvefitting
   fileloading
