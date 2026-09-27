Sequences, Protocol Modules and Pipelines
=========================================

PhysPlot records what you do as a protocol. Three kinds of files keep a protocol, or
part of one, for reuse:

- a **sequence** (``config/sequences/*.py``) is a complete recipe: roles,
  transformations and a plot, replayed on one file or a whole folder;
- a **protocol module** (``config/protocol_modules/*.py``) is a short block of steps
  that **Protocol → Insert Protocol Module** adds to the current protocol;
- a **pipeline** (``config/pipelines/*.json``) is a list of column transformations.

All three can be written for you by an AI assistant: see the "Let an AI Assistant
Write It" sections below. :doc:`../user_guide/protocol_sequences` and the
:doc:`../ui/sequence_walkthrough` show how to record and run protocols in the window.

.. contents:: On this page
   :local:
   :depth: 1

.. youtube:: l1zGnY109j4
   :title: Saving a Sequence

Sequence Files
--------------

A sequence is a plain Python file. It defines ``WORKFLOW_STEPS``, a list of step
objects from ``physplot.steps`` in run order (or a function ``build_workflow()`` that
returns that list). The easiest way to get one is **Protocol → Export Sequence.py**
after doing the steps once on a real file.

.. list-table::
   :header-rows: 1
   :widths: 28 72

   * - Step
     - What it does
   * - ``LoadDataStep``
     - Loads a file. Run Sequence and the command line replace it with each input file.
   * - ``SetRoleStep``
     - Assigns column roles, for example ``roles={"x": "Wavelength (nm)", "y": "Absorbance"}``.
   * - ``TransformColumnStep``
     - Writes a transformation of one column to a new or existing column.
   * - ``CalculateColumnStep``
     - Writes an arithmetic formula of columns to a column.
   * - ``RenameColumnStep``, ``DeleteColumnsStep``, ``DeleteRowsStep``, ``SetCellValueStep``
     - Edit the table.
   * - ``PlotModuleStep``
     - Draws a plot with a plotter module, optionally with an LSQ fit.

A sequence runs in three places:

- **Protocol → Import Sequence.py**, then **Apply This Sequence**, on the table that is
  open;
- **Run Sequence** (Advanced Mode) on every file in a folder;
- the command line: ``physplot run-workflow Sequence.py --input data.csv --output out``
  for one file, ``physplot run-bulk`` for a folder.

Refer to columns by their exact header text, including units. Transformations are
named by their built-in name (``multiply``, ``subtract``, ``normalize_max``, ...) or by
the file name of a transformation plugin (``"20_wavenumber_to_wavelength"``).

Let an AI Assistant Write a Sequence
------------------------------------

The guide file `config/sequences/AI_GUIDE.md
<https://github.com/MShirazAhmad/PhysPlot/blob/indevelopment/config/sequences/AI_GUIDE.md>`_
gives an AI assistant the complete step reference and a tested example.
:doc:`ai_assistant` explains the method for every kind of module.

The most reliable route is to **do the steps once in PhysPlot on one real file, save
them with Protocol → Export Sequence.py, and attach that file**: the assistant then edits
a known-good sequence and changes only what you ask.

1. **Download the guide.** Open the link above and click **Download raw file** (the ↓
   button).
2. **Start a new chat** with ChatGPT, Claude, Gemini, Copilot or another assistant, and
   attach:

   - ``AI_GUIDE.md``;
   - your exported ``Sequence.py``, if you have one;
   - the first 20–30 lines of one data file (or its column headers exactly as PhysPlot
     shows them);
   - for file types other than ``.csv``, ``.txt``, ``.dat``, ``.tsv``, ``.msa``,
     ``.xls``, ``.xlsx`` and ``.xrdml``: the full path of one sample file.

3. **Say what you want**, for example:

   .. code-block:: text

      I attached PhysPlot's sequence guide and the first lines of one UV-Vis spectrum
      (CSV, columns "Wavelength (nm)" and "Absorbance"). Write a sequence that
      subtracts the blank level 0.02 from Absorbance, scales the strongest peak to 1,
      and plots it against wavelength as a line. I will run it on a folder of about
      40 spectra with Run Sequence.

4. **Save the reply** in ``Documents/PhysPlot/config/sequences/`` under the file name
   the assistant gives. Try it on one file with **Protocol → Import Sequence.py** and
   **Apply This Sequence**, then on the folder with **Run Sequence**.
5. **If PhysPlot shows an error**, paste the whole message into the chat. The assistant
   sends a corrected complete file.

Protocol Modules
----------------

A protocol module is a sequence file meant as a building block. Besides
``WORKFLOW_STEPS`` it can set ``DISPLAY_NAME`` (the menu label) and ``DESCRIPTION``
(the tooltip):

.. code-block:: python

   """Protocol module: plot resistance against temperature in kelvin."""

   from physplot.steps import PlotModuleStep, SetRoleStep, TransformColumnStep

   DISPLAY_NAME = "Resistance vs Temperature (K)"
   DESCRIPTION = "Add 273.15 to Temperature_C as a new column Temperature_K, plot Resistance_ohm against it."

   WORKFLOW_STEPS = [
       TransformColumnStep(
           input_column="Temperature_C",
           input_column_number=1,
           function_name="add",
           output="Temperature_K",
           params={"value": 273.15},
       ),
       SetRoleStep(roles={"x": "Temperature_K", "y": "Resistance_ohm"}),
       PlotModuleStep(plotter_id="basic", plot_type="scatter_line", config={}),
   ]

Save it in ``Documents/PhysPlot/config/protocol_modules/`` and choose **File → Reload
Config Modules**. It then appears under **Protocol → Insert Protocol Module**; choosing
it adds its steps to the end of the Build Protocol sequence, and **Apply This
Sequence** runs them.

Let an AI Assistant Write a Protocol Module
-------------------------------------------

Attach `config/protocol_modules/AI_GUIDE.md
<https://github.com/MShirazAhmad/PhysPlot/blob/indevelopment/config/protocol_modules/AI_GUIDE.md>`_
to a new chat, with the first lines of a data file (or an exported ``Sequence.py`` that
already contains the steps) and the menu name you want. For example:

.. code-block:: text

   Using the attached guide, make a protocol module for my resistance-temperature
   files (columns Temperature_C, Resistance_ohm). It should add Temperature_K =
   Temperature_C + 273.15 and plot Resistance_ohm against it with lines and markers.
   Menu name: "Resistance vs Temperature (K)".

Save the reply in ``Documents/PhysPlot/config/protocol_modules/``, choose **File →
Reload Config Modules**, insert it from **Protocol → Insert Protocol Module** and click
**Apply This Sequence**. Paste any error message back into the chat.

Pipelines
---------

A pipeline is a JSON list of column transformations:

.. code-block:: json

   [
     {"input": "Absorbance", "function": "subtract", "params": "value=0.02", "output": "Absorbance_corr"},
     {"input": "Absorbance_corr", "function": "normalize_max", "params": "-", "output": "Absorbance_norm"}
   ]

.. note::

   PhysPlot 1.0 has no menu item or button for pipeline files. A pipeline is applied
   with a short Python script, given in the pipeline guide, which also saves it as a
   sequence. To add transformations from PhysPlot's menus, write a protocol module
   instead; for a whole recipe with roles and a plot, write a sequence.

Let an AI Assistant Write a Pipeline
------------------------------------

Attach `config/pipelines/AI_GUIDE.md
<https://github.com/MShirazAhmad/PhysPlot/blob/indevelopment/config/pipelines/AI_GUIDE.md>`_
to a new chat with the first lines of a data file and the list of transformations, for
example:

.. code-block:: text

   With the attached guide, write a pipeline for my UV-Vis CSVs (columns
   "Wavelength (nm)", "Absorbance"): subtract 0.02 from Absorbance into
   Absorbance_corr, then scale the strongest peak to 1 into Absorbance_norm.

The assistant first suggests a protocol module if that suits you better. Save the
pipeline in ``Documents/PhysPlot/config/pipelines/`` and run the script from the guide.
