Plot Generation
===============

For a full step-by-step flow, see :ref:`GUI Walkthrough — Generating and Formatting a Plot <gui-generating-and-formatting-plot>`.

Requirements
------------

To generate a plot, assign exactly one **X-axis** column and one **Y-axis** column.

Generate plot flow
------------------

1. Choose a plotter and plot type in Simple Mode.
2. Optionally choose a saved **Template**.
3. Click **Generate Plot**.
4. For Basic Plotter output, PhysPlot opens the Figure Editor.

Figure Editor
-------------

The Figure Editor opens with the generated Matplotlib figure and lets you inspect and edit the figure tree. It draws:

- Main data series
- Optional error bars (if Xerr/Yerr columns are assigned)
- Title and axis labels
- Legend entries and titles
- Optional fit overlays added through **Figure Editor > Fitting > Add Fit Function**

Use **Figure Editor > PhysPlot > Save as Template** to save the current appearance. Back in Simple Mode, click **Reload** next to **Template** and select the saved template before generating another plot.

.. image:: ../_static/gui_walkthrough/04_plot_generated_and_formatting_window.png
   :alt: Plot generation and output window
   :width: 700px
