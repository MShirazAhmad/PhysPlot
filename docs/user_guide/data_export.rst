Data Export
===========

For a full step-by-step flow, see :ref:`GUI Walkthrough — Exporting Processed Data <gui-exporting-processed-data>`.

Export behavior
---------------

Click **Export Data** from Simple Mode or use **File > Export Data...** to save
the current table output.

Backend exports can also include metadata, column summaries, generated workflow
source, fit results, and ``plot.png`` when a figure exists.

Workflow
--------

1. Click **Export Data** or choose **File > Export Data...**.
2. Choose destination path and filename.
3. Confirm save.

For reproducible runs, export the protocol with **Protocol > Export
Sequence.py...** and run it later with:

.. code-block:: bash

   physplot run-workflow sequence.py --input data.csv --output outputs/run

.. image:: ../_static/gui_walkthrough/08_export_data_workflow.png
   :alt: Data export workflow
   :width: 700px
