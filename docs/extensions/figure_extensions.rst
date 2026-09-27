Figure Templates, Fit Styles and Figure Editor Plugins
======================================================

Three kinds of files change how PhysPlot's figures look:

- a **figure template** (``config/templates/*.json``) restyles each plot after
  **Generate Plot**;
- a **fit-style preset** (``config/figureforge_fit_styles/*.json``) fills the **Fit
  Line** fields of the LSQ fit;
- a **Figure Editor plugin** (``config/figureforge_plugins/*.py``) adds a command to the
  Figure Editor.

All three can be written for you by an AI assistant: see the "Let an AI Assistant Write
It" sections below and :doc:`ai_assistant`. :doc:`../user_guide/plot_customization`
shows how to style a plot by hand.

.. contents:: On this page
   :local:
   :depth: 1

Figure Templates
----------------

A template is a JSON file with figure and axes styling and no data: figure size and
background, the fonts of the axes title and axis labels, grid, spines, tick-label size
and colour, line and marker colours, and the legend. Choose it in **3. Plotter Module →
Template**; every **Generate Plot** then applies it. Templates are not part of the
protocol, so replays and bulk runs do not apply them.

The usual way to make one:

1. Generate a Basic Plotter figure.
2. Style it in the Figure Editor.
3. Choose **Figure Editor → PhysPlot → Save as Template**. It is saved in
   ``Documents/PhysPlot/config/templates/``.
4. Back in PhysPlot, click **Reload** beside **Template** and select it.

A template cannot set tick direction, tick length or minor ticks, the font family of
tick labels and legend entries, marker shape and size, axis limits, or the text of the
title and labels. A Figure Editor plugin can change ticks (see below).

Let an AI Assistant Write a Template
------------------------------------

The guide file `config/templates/AI_GUIDE.md
<https://github.com/MShirazAhmad/PhysPlot/blob/indevelopment/config/templates/AI_GUIDE.md>`_
lists every key PhysPlot reads and includes a tested journal-style template. The best
start is a template you saved from the Figure Editor for the kind of plot you use, so
the assistant only changes what you ask.

1. **Download the guide.** Open the link above and click **Download raw file** (the ↓
   button).
2. **Start a new chat** with ChatGPT, Claude, Gemini, Copilot or another assistant, and
   attach ``AI_GUIDE.md``, your saved template and, optionally, a picture of the target
   style or the journal's figure guidelines.
3. **Say what you want**, for example:

   .. code-block:: text

      Attached is a template I saved from a Basic Plotter scatter plot with an LSQ
      fit. Make it a single-column figure for my journal: 3.4 by 2.6 inches, 8 pt
      axis labels, 7 pt tick labels, thin black axes on all four sides, open black
      circles, a red fit line, and a legend without a frame. No grid.

4. **Save the reply** in ``Documents/PhysPlot/config/templates/`` (**File → Open
   Config Folder**), click **Reload** beside **Template**, select it and click
   **Generate Plot**.

The assistant tells you when a request, such as inward ticks, needs a Figure Editor
plugin instead.

Fit-Style Presets
-----------------

A fit-style preset sets how the LSQ fit line is drawn. Choosing it in **3. Plotter
Module → Fit Style** fills the **Fit Line** fields:

.. code-block:: json

   {
     "name": "Thin Dashed Fit",
     "line_style": "--",
     "line_width": 1.0,
     "label": "Linear fit",
     "show_legend": true
   }

``line_style`` is one of ``"--"``, ``"-"``, ``"-."`` or ``":"``; ``line_width`` is in
points; an empty ``label`` gives the automatic label with the fitted values. A preset
has no colour and no fit function; a template can colour the fit line. The chosen
values are saved in the protocol with the fit, so replays draw the same line. Click
**Reload** beside **Fit Style** after adding a file.

Let an AI Assistant Write a Fit Style
-------------------------------------

Attach `config/figureforge_fit_styles/AI_GUIDE.md
<https://github.com/MShirazAhmad/PhysPlot/blob/indevelopment/config/figureforge_fit_styles/AI_GUIDE.md>`_
to a new chat and describe the line, for example:

.. code-block:: text

   Make a fit style called "Thin Dotted Fit": a dotted line 1 pt wide, labelled
   "Exponential fit", with the legend shown.

Save the reply in ``Documents/PhysPlot/config/figureforge_fit_styles/``, click
**Reload** beside **Fit Style** and choose it.

Figure Editor Plugins
---------------------

A Figure Editor plugin is a Python file that adds a command to the Figure Editor's
**Figure Editor** menu. You select a part of the figure in the **Figure Explorer** (the
figure, an axes, a line, ...) and choose the command; it changes that part and the
editor redraws the figure. Good uses are restyling the Property Inspector and templates
cannot do (tick direction, minor ticks), reference lines, annotations and small
calculations. The changes stay in that editor window: save them with the editor's
**File → Export**.

PhysPlot copies the ``.py`` files from ``Documents/PhysPlot/config/figureforge_plugins/``
into the Figure Editor each time a new Figure Editor opens, so to try a new or changed
plugin, generate a new Basic Plotter plot. A plugin you rename or delete there is removed
from the next Figure Editor as well. The bundled ``physplot_fit_function.py`` and
``physplot_save_style_module.py`` are working examples.

Two messages can appear when a plugin has a problem:

- **Figure Editor failed** appears a few seconds after **Generate Plot** when a plugin
  stops the Figure Editor from opening, for example because of a syntax error or a
  missing package. The message names the plugin file and the error; **Show Details...**
  holds the full error output. No plot opens in the Figure Editor until you fix or remove
  that file.
- **Figure Editor plugin skipped** means a plugin file has the name of one of the Figure
  Editor's own files (``__init__.py``, ``add_annotation.py``, ``add_legend.py``,
  ``add_minor_data_ticks.py``, ``reduce_tick_limits.py``, ``set_spine_bounds.py``,
  ``toggle_spines.py`` or ``utils.py``). PhysPlot does not copy it, because it would
  overwrite part of the Figure Editor. Rename the file; the Figure Editor opens without it
  until then.

Let an AI Assistant Write a Plugin
----------------------------------

Attach `config/figureforge_plugins/AI_GUIDE.md
<https://github.com/MShirazAhmad/PhysPlot/blob/indevelopment/config/figureforge_plugins/AI_GUIDE.md>`_
to a new chat, with a screenshot of the Figure Editor or the figure if it helps and the
menu name you want. For example:

.. code-block:: text

   In the Figure Editor I want a command "Reference Line" under a new submenu
   "Guides". With an Axes selected, it asks me for a y value and draws a thin grey
   dashed horizontal line there.

Save the reply in ``Documents/PhysPlot/config/figureforge_plugins/`` and generate a new
Basic Plotter plot to open a fresh Figure Editor. If PhysPlot shows **Figure Editor
failed** instead, click **Show Details...**, copy the error output and paste it into the
chat for a corrected file.
