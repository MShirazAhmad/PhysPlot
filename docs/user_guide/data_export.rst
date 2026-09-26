Data Export
===========

For a full step-by-step flow, see :ref:`GUI Walkthrough — Exporting Processed Data <gui-exporting-processed-data>`.

Export behavior
---------------

Click **Export Data** in Simple Mode's **1. Data Importer** panel, or choose
**File > Export Data...**, then pick a folder. PhysPlot writes:

- ``data.csv``: the current table.
- ``columns.csv``: column metadata and provenance (source columns,
  transformations, formulas).
- ``workflow.py``: the protocol that produced the table.
- ``fit.json`` and ``plot.png``: when a fit or a figure exists.

Reproducible runs
-----------------

Export the protocol with **Protocol > Export Sequence.py...** and run it later
on the same or other files:

.. code-block:: bash

   physplot run-workflow Sequence.py --input data.csv --output outputs/run
   physplot run-bulk Sequence.py --input-folder data/ --output-folder outputs/batch

Or process a folder from **Advanced > Run Sequence**; each input file gets its
own output folder with the files listed above.

.. image:: ../_static/gui_walkthrough/bulk_01_run_sequence.png
   :alt: Run Sequence bulk export
   :width: 700px
