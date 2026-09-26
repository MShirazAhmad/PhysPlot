# Bulk Runs and Headless Use

A protocol built in the GUI can be applied to every file in a folder, from the
command line, or from Python. All of these run the same steps as
**Apply This Sequence**.

## Run Sequence (bulk run in the GUI)

This example records a protocol on one OES spectrum, then runs it over the folder:

1. Import `test_data/OES/spectrum_1.HRF` with **Auto Loader**.
2. Apply `normalize_max` to `Intensity`, with output `Intensity_norm`.
3. Open **Advanced → Run Sequence**.

![Run Sequence bulk run](images/bulk/bulk_01_run_sequence.png)

1. **Input Folder.** The folder of files to process (`test_data/OES`).
2. **Sequence File.** Optional. Leave it blank to use the current Build Protocol
   sequence, or choose an exported `Sequence.py`.
3. **Output Folder.** Each input file gets its own subfolder here.
4. **Run Bulk Workflow.** Starts the run.
5. **Current Protocol Sequence.** The steps that will run. The protocol's File Loader
   row is replaced by each file in turn.
6. **Status bar.** `Bulk complete: 3 outputs` when every file has been processed.

**Which files are processed**

- If the protocol was recorded on a plugin format (for example `.HRF`), only files
  with that extension are processed, using the same loader.
- Otherwise, all table formats are processed: `.csv`, `.txt`, `.dat`, `.tsv`, `.msa`,
  `.xls`, `.xlsx` and `.xrdml`.

**What each output folder contains**

- `data.csv`: the final table.
- `columns.csv`: column metadata and provenance.
- `workflow.py`: the protocol that produced it.
- `plot.png` and `fit.json`, when the protocol plots or fits.

**If a file fails**, the run stops at that file and the dialog names it, for example
*"Bulk run stopped at b_text.csv: …"*. Files before it are already exported. If a
column is missing, the GUI falls back to the same column number and logs a warning.

## Command line

Export the protocol first with **Protocol → Export Sequence.py…**, then:

```bash
# One file
physplot run-workflow Sequence.py --input scan.xrdml --output outputs/scan

# Every file in a folder
physplot run-bulk Sequence.py --input-folder scans/ --output-folder outputs/bulk
```

Add `--allow-column-number-fallback` to use column numbers when a column name is
missing, as the GUI does. A protocol recorded on a plugin format (for example
`.HRF`) reuses that plugin for each file.

## From Python or a notebook

An exported `Sequence.py` is ordinary Python. It contains `WORKFLOW_STEPS`,
`build_workflow()` and `run()`:

```python
import runpy

sequence = runpy.run_path("Sequence.py")
pp = sequence["run"](input_path="test_data/OES/spectrum_2.HRF", output_dir="outputs/spectrum_2")
print(pp.dataset.dataframe.head())
```

Or build a protocol in code with the backend API:

```python
from physplot import PhysPlot

pp = PhysPlot()
pp.load("test_data/XRD/quick_scan.xrdml")          # Auto Loader
pp.set_roles(x="2Theta", y="Intensity")
pp.transform("Intensity", "14_xrd_baseline_remove", output="Intensity_bg")
pp.plot_with_module("basic", "line")
pp.export("outputs/quick_scan")                     # data, metadata, workflow.py, plot.png
pp.export_workflow("Sequence.py")                   # the recorded protocol
```

None of this imports the GUI, so it runs on servers and in CI.
