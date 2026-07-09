Plot Generation
===============

For a full step-by-step flow, see :ref:`GUI Walkthrough — Generating and Formatting a Plot <gui-generating-and-formatting-plot>`.

Requirements
------------

To generate a standard plot, assign at least one **X** column and one **Y**
column. Some specialized plotter modules also use optional roles such as
**X Error**, **Y Error**, **Group**, or **Label**.

Generate plot flow
------------------

1. Choose a plotter and plot type in Simple Mode.
2. Optionally choose a saved **Template**.
3. Optionally enable **LSQ fit** and enter a fit function, parameter names,
   and initial guesses.
4. Click **Generate Plot**.
5. For Basic Plotter output, PhysPlot opens the Figure Editor.

Least-squares fitted line
-------------------------

The **Plotter Module** panel can overlay a least-squares fitted line while the
plot is generated. Enable **LSQ fit** and provide:

- **Fit Function**: an expression in ``x``, for example ``a*x + b`` or
  ``a*np.exp(b*x) + c``.
- **Params**: comma-separated parameter names, for example ``a,b``.
- **Initial**: comma-separated starting guesses matching the parameter list,
  for example ``1,0``.
- **Fit Style**: optional curve label, line style, line width, and legend
  display.

The fit uses the columns assigned as **X** and **Y**. The fitted line is stored
in the generated figure, and the fit configuration is saved in the
``PlotModuleStep`` so exported sequences and bulk runs can replay it.

Built-in plotter modules
------------------------

- **Basic Plotter**: ``scatter``, ``line``, ``scatter_line``
- **Histogram Plotter**: ``histogram``, ``density_histogram``
- **Scatter Plotter**: ``scatter``
- **Line Plotter**: ``line``
- **Error Bar Plotter**: ``x_y_errorbar``, ``y_errorbar``
- **Overlay Plotter**: ``overlay_by_group``, ``overlay_by_dataset``
- **Subplot Grid Plotter**: ``subplots_by_group``, ``subplots_by_dataset``
- **Nanoindentation Plotter**: ``load_depth``, ``hardness_depth``,
  ``modulus_depth``, ``stiffness_depth``, ``contact_depth``
- **Oliver-Pharr Plotter**: ``load_depth_with_unloading_fit``,
  ``unloading_fit``, ``contact_stiffness_fit``, ``area_function``,
  ``hardness_summary``, ``modulus_summary``

When a plot is generated, the selected plotter, plot type, and configuration
are stored as a ``PlotModuleStep`` in the protocol sequence. Bulk runs replay
that recorded step instead of using a separate bulk plotting choice.

Figure Editor
-------------

The Figure Editor opens with the generated Matplotlib figure and lets you inspect and edit the figure tree. It draws:

- Main data series
- Optional error bars (if **X Error** or **Y Error** columns are assigned)
- Title and axis labels
- Legend entries and titles
- Optional fit overlays added through **Figure Editor > Fitting > Add Fit Function**

Use **Figure Editor > PhysPlot > Save as Template** to save the current appearance. Back in Simple Mode, click **Reload** next to **Template** and select the saved template before generating another plot.

.. image:: ../_static/gui_walkthrough/04_plot_generated_and_formatting_window.png
   :alt: Plot generation and output window
   :width: 700px
