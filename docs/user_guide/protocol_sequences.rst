Protocol Sequences
==================

Advanced Mode's **Build Protocol** tab lists every recorded step of the
current analysis. The same steps are exported by **Export Sequence.py** and
replayed by **Run Sequence** and the ``physplot`` command line.

For a step-by-step example with screenshots (record a protocol, save it, reopen and
edit it, then bulk-process a folder), see :doc:`../ui/sequence_walkthrough`. Every
control on these tabs is described in :doc:`../ui/build_protocol` and
:doc:`../ui/run_sequence`.

.. youtube:: I5nPKIvLaWk
   :title: Recorded Protocol

.. youtube:: l1zGnY109j4
   :title: Saving a Sequence

.. youtube:: XzgZrVX2wkM
   :title: Bulk Processing

Step status
-----------

After **Apply This Sequence**, deleting a row, or a rerun, the **Status**
column reports what happened to each row:

- **OK**: the row ran. Hover to see how long it took.
- **Failed**: the row raised an error. Hover to read the error.
- **Skipped**: the row did not run because an earlier row failed.

A sequence always stops at the first failing row. The spreadsheet keeps the
state reached just before that row, so you can inspect the data that caused
the problem. The status bar names the failing row, for example
``Row 2 failed (TransformColumnStep): ValueError: Column 'Volts' not found.``

Statuses clear for any row whose step you replace, for example after
**Apply Code to Table**, until the sequence runs again.

Rerun from a step
-----------------

Right-click a row and choose **Rerun from this step** to resume the sequence
at that row without replaying the rows above it. PhysPlot restores the data
exactly as it was before that row last ran, then runs the row and everything
after it.

Typical use:

1. Apply the sequence. Row 5 fails.
2. Fix row 5 in the Code view and click **Apply Code to Table**.
3. Right-click row 5 and choose **Rerun from this step**.

Rows 1 to 4 are not replayed, which matters when they load large files or run
slow steps. If you edited a row above the one you rerun from, PhysPlot starts
from the earliest point it can still trust, which is normally the start of
the last full run. If no run has happened yet, apply the whole sequence
first.

Editing steps
-------------

Every row can be changed from the table without touching Python:

- **Edit**: double-click a row, or right-click and choose **Edit step...**.
  The editor lists the row's settings; fields marked ``*`` are required.
  Column fields offer the current table columns. Invalid values, such as a
  parameter that is not a ``{...}`` dictionary, are explained in red and the
  dialog stays open. After **OK** the sequence resumes from that row.
- **Enable or disable**: untick the **On** checkbox, or right-click and
  choose **Disable step**. A disabled row stays in the sequence, is shown in
  grey, and reports **Skipped**; the rows after it still run. Exported
  sequence files keep the setting as ``enabled=False``.
- **Reorder**: right-click and choose **Move up** or **Move down**. Rows that
  load data stay first and nothing can move above them.
- **Insert**: right-click a row and choose **Insert step after...**, or use
  **Protocol > Insert Step...** and **Protocol > Insert Protocol Module**.
  New rows go after the selected row, or at the end when no row is selected.

Each of these changes replays the sequence from the first affected row, the
same way **Rerun from this step** does. If the change breaks a later row, for
example moving **Set Roles** below **Generate Plot**, that row shows
**Failed** and the status bar explains why; no dialog interrupts you.

Headless use
------------

.. youtube:: 9Waw3iNOO1s
   :title: Bulk Processing OES Spectra

The same behavior is available in Python:

.. code-block:: python

   from physplot import PhysPlot
   from physplot.workflow import load_workflow

   pp = PhysPlot()
   pp.load("data.csv")
   steps = load_workflow("sequence.py")

   results = pp.run_workflow_detailed(steps, allow_column_number_fallback=True)
   for result in results:
       print(result.index + 1, result.step_name, result.status, result.error or "")

   # After fixing steps[4]:
   pp.rerun_from(4, steps, allow_column_number_fallback=True)

``pp.run_workflow(steps)`` keeps its original behavior: it raises the first
error. It also records per-step results on ``pp.last_results``.

Steps can be edited in code with the same checks the editor uses:

.. code-block:: python

   step = steps[1]
   print(step.describe())            # editable fields, types, and current values
   step.update(function_name="divide", params={"divisor": 2})
   step.update(enabled=False)        # keep the step but skip it
   pp.move_step(3, 2)                # reorder pp.workflow
   pp.insert_step(1, step)           # insert before position 1
