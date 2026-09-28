Plotter Modules and Plot-Type Presets
=====================================

A **plotter module** adds a new kind of figure to PhysPlot. A **plot-type preset**
adds a named variant of an existing plotter's figure. Both are small files in
``Documents/PhysPlot/config/``, and an AI assistant can write either of them for
you (see the "Let an AI Assistant Write It" sections below).

.. contents:: On this page
   :local:
   :depth: 1

.. youtube:: AHWbQDqHvQ0
   :title: How to Create a Plotter Module

What a Plotter Module Does
--------------------------

A plotter module is one Python file in ``config/plotter_modules/``. It reads the
columns you gave roles to (X, Y, Y Error, ...) and returns a Matplotlib figure. It
appears in Simple Mode's **3. Plotter Module** panel: its ``NAME`` in **Plotter
Module** and its ``PLOT_TYPES`` in **Plot Type**. **Generate Plot** records a
``PlotModuleStep(plotter_id=...)``, so saved sequences, **Run Sequence** and bulk
runs draw the same figure for every file.

The File
--------

.. list-table::
   :header-rows: 1
   :widths: 30 14 56

   * - Name
     - Type
     - Meaning
   * - ``PLOTTER_ID``
     - ``str``
     - Unique id, stored in saved sequences. Never change it once sequences use it.
   * - ``NAME``
     - ``str``
     - Label in the **Plotter Module** menu.
   * - ``CATEGORY``
     - ``str``
     - Optional group name, for example ``"User"``.
   * - ``PLOT_TYPES``
     - ``list[str]``
     - Entries of the **Plot Type** menu, in order; the first is the default.
   * - ``plot(dataset, plot_type=None, config=None)``
     - function
     - Draws and returns a ``matplotlib.figure.Figure``.

``plot`` receives:

- ``dataset.dataframe``: the table as a pandas ``DataFrame``;
- ``dataset.column_roles``: a dict from column name to role (``"X"``, ``"Y"``,
  ``"X Error"``, ``"Y Error"``, ``"Group"``, ``"Label"``, ``"Batch Key"``,
  ``"Fit Weight"`` or ``"Ignore"``);
- ``dataset.name``: usually the data file name without its extension;
- ``plot_type``: one of ``PLOT_TYPES``;
- ``config``: a dict of options from a plot-type preset or a sequence's
  ``PlotModuleStep(config=...)``, often empty. Simple Mode has no fields for your own
  options, so the defaults must give a finished figure.

The figure opens in a plot window. A selected **Template** restyles it, and **LSQ fit**
draws its line on the first axes. Headless and bulk runs save it as ``plot.png``.

A file can instead define a ``BasePlotter`` subclass, or a ``PLOTTERS`` list for
several plotters in one file; the form above is the simplest.

The bundled example, ``config/plotter_modules/example_xy_plotter.py``:

.. literalinclude:: ../../config/plotter_modules/example_xy_plotter.py
   :language: python
   :lines: 12-

Rules that keep plotters reliable:

- **Find columns by role**, not by name, so the plotter works for every file.
- **Return the figure.** Never call ``plt.show()`` or ``savefig``.
- **Raise a clear** ``ValueError`` when a role is missing; PhysPlot shows its text.
- **Keep** ``PLOTTER_ID`` **stable** and different from the built-in ids (``basic``,
  ``scatter``, ``line``, ``errorbar``, ...). A user plotter with a built-in id replaces
  the built-in one.

Save the file in ``Documents/PhysPlot/config/plotter_modules/`` (**File → Open Config
Folder**) and choose **File → Reload Config Modules**.

Let an AI Assistant Write a Plotter
-----------------------------------

The guide file `config/plotter_modules/AI_GUIDE.md
<https://github.com/MShirazAhmad/PhysPlot/blob/indevelopment/config/plotter_modules/AI_GUIDE.md>`_
tells an AI assistant exactly what PhysPlot expects and includes a complete, tested
plotter (derivative and normalized plots of Y against X). :doc:`ai_assistant` explains
the method for every kind of module.

1. **Download the guide.** Open the link above and click **Download raw file** (the ↓
   button).
2. **Start a new chat** with ChatGPT, Claude, Gemini, Copilot or another assistant, and
   attach:

   - ``AI_GUIDE.md``;
   - a data file, or its first 30–50 lines;
   - which column is X, Y, Y Error and so on;
   - optionally a picture or sketch of the figure you want.

3. **Say what you want**, for example:

   .. code-block:: text

      I measure current-voltage curves of solar cells (sample file attached).
      Voltage (V) is X and Current (mA) is Y. Please make a plotter with two plot
      types: "iv" (current vs voltage, markers joined by a line) and "power"
      (P = V x I in mW vs voltage, with the maximum power point marked). Label both
      axes with units and use the file name as the title. I will run it over a
      whole folder of files.

4. **Save the reply** in ``Documents/PhysPlot/config/plotter_modules/`` under the file
   name the assistant gives. Choose **File → Reload Config Modules**, pick the plotter
   in **Plotter Module**, and click **Generate Plot** for each plot type.
5. **If PhysPlot shows an error**, paste the whole message into the chat. The assistant
   sends a corrected complete file; save it over the old one and reload.

Plot-Type Presets
-----------------

A preset is a JSON file in ``config/plot_types/`` that adds an entry to one plotter's
**Plot Type** menu. The entry draws one of that plotter's own plot types with fixed
options:

.. code-block:: json

   {
     "plotter_id": "example_xy",
     "plot_type": "calibration_curve",
     "base_plot_type": "xy_markers",
     "description": "Absorbance standards against concentration, 5 x 4 inch figure",
     "config": {
       "x_label": "Concentration (mg/L)",
       "y_label": "Absorbance (a.u.)",
       "label": "Standards",
       "grid": true,
       "figsize": [5, 4]
     }
   }

.. list-table::
   :header-rows: 1
   :widths: 24 12 64

   * - Key
     - Required
     - Meaning
   * - ``plotter_id``
     - yes
     - Id of an installed plotter, for example ``basic`` or ``example_xy``.
   * - ``plot_type``
     - yes
     - The new menu entry, also stored in saved sequences. It must be new: a preset
       with an existing name silently changes that plot type.
   * - ``base_plot_type``
     - yes
     - One of the plotter's own plot types; this is what is drawn.
   * - ``config``
     - no
     - Options passed to the plotter's ``plot``. Keys in a sequence's
       ``PlotModuleStep(config=...)`` win over the preset's.
   * - ``description``
     - no
     - A note for people reading the file.

A file can also hold a JSON list of several presets. Saved sequences store only the
preset's name, so every replay reads the file again: editing it changes later replays,
and deleting it breaks them.

.. note::

   ``config`` has an effect only if the plotter reads those options. PhysPlot's
   built-in plotters (Basic, Scatter, Line, Error Bar, Histogram, Overlay, Subplot
   Grid and the nanoindentation plotters) read none, so a preset for them only adds
   a name for an existing plot type. To restyle their figures, use a
   :doc:`figure template <figure_extensions>` or write a plotter module. The Example
   XY Plotter reads ``figsize``, ``label``, ``x_label``, ``y_label`` and ``grid``; your
   own plotters read whatever their ``plot`` looks up in ``config``.

Let an AI Assistant Write a Preset
----------------------------------

Attach `config/plot_types/AI_GUIDE.md
<https://github.com/MShirazAhmad/PhysPlot/blob/indevelopment/config/plot_types/AI_GUIDE.md>`_
to a new chat, together with the plotter and plot type you use now (as named in the
menus) and, if it is your own plotter, its ``.py`` file. Then describe the variant, for
example:

.. code-block:: text

   I use my Derivative Plotter (file attached). Please make a plot type called
   "cooling_rate" based on its "derivative" type. It should smooth over 5 points,
   label the y-axis "Cooling rate (K/s)", use the title "Cooling curve", and make a
   5 x 3.5 inch figure without a grid.

The guide lists every plotter and the options it reads, so the assistant tells you when
a plotter cannot do what you ask. Save the reply in
``Documents/PhysPlot/config/plot_types/``, choose **File → Reload Config Modules**, and
pick the new entry in **Plot Type**.
