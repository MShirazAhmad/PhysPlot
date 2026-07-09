Extension Guides
================

PhysPlot is designed so common scientific extensions can be added by creating
small Python or JSON files in predictable folders:

- ``functions/`` for table-column transformations.
- ``curvefitting/`` for plot curve-fit models.
- ``fileloader/`` for importing new data formats.
- ``styling/`` for reusable Figure Editor templates.

These extension points let users add new behavior without editing the main GUI
code. Each file is discovered when PhysPlot starts, so restart the application
after adding or changing Python extension files. Figure templates can be
refreshed with the **Reload** button beside the **Template** dropdown.

.. toctree::
   :maxdepth: 2

   modularity
   functions
   curvefitting
   fileloading
