<!-- Generated from wiki/UI-Dialogs-and-Messages.md by scripts/sync_wiki_to_docs.py. Edit the wiki page. -->

# Dialogs and Messages

[UI Reference](index.md) › Dialogs and Messages

This page lists every file dialog, error dialog and status-bar message PhysPlot shows,
with what each one means and what to do. For step-by-step fixes, see
[Troubleshooting](https://github.com/MShirazAhmad/PhysPlot/wiki/Troubleshooting).

## How PhysPlot reports problems

When an action fails:

1. A **warning dialog** opens. Its title names the action (for example *Import
   failed*), and its text is the error.
2. The **status bar** shows the same title, so you can still see it after closing the
   dialog.
3. **Nothing is recorded** in the protocol, and the table is not changed. The
   exceptions are replays, which show the table as it was just before the failing
   step.

Replay failures are also marked in the Build Protocol **Status** column. See
[Build Protocol](build_protocol.md#status-column).

## File dialogs

| Title | Opened by | Starts in | File types |
| --- | --- | --- | --- |
| *Import Data* | **Import Data** (panel) / **File → Import Data…** | Current folder | Data Files (built-in types plus every loader plugin's `FILE_EXTENSIONS`), All Files |
| *Import Folder* | **Import Folder** | Current folder | Folders |
| *Export Data* | **Export Data** / **File → Export Data…** | Current folder | Folders |
| *Export Plot* | **Export Plot** | `physplot_plot.png` | PNG, PDF, SVG, All Files |
| *Load Sequence.py* | **Import Sequence.py** / **Protocol → Import Sequence.py…** | `config/sequences/` | Python Files |
| *Save Sequence.py* | **Export Sequence.py** / **Protocol → Export Sequence.py…** | `config/sequences/sequence.py` | Python Files |
| *Input Folder* / *Output Folder* | **Browse** in Run Sequence | Current folder | Folders |
| *Sequence File* | **Browse** in Run Sequence | `config/sequences/` | Python Files |

`config/…` means your per-user folder `Documents/PhysPlot/config/…`. **File → Open
Config Folder** opens it.

## Other dialogs

| Dialog | Where | Page |
| --- | --- | --- |
| *Rename Column* (text entry) | Double-click a header, or header menu → **Rename Column** | [Data Table](data_table.md#renaming-a-column) |
| *About PhysPlot* | **Help → About PhysPlot** | [Main Window](main_window.md#help) |
| *Save as Template*, *PhysPlot Template* | Figure Editor → **PhysPlot → Save as Template** | [Figure Editor](figure_editor.md#save-as-template) |
| *Add Fit Function* | Figure Editor → **Fitting → Add Fit Function** | [Figure Editor](figure_editor.md#add-fit-function) |
| *PhysPlot - <plotter>: <plot type>* | **Generate Plot** with a plotter other than Basic | [Plot windows](figure_editor.md#plot-windows) |

## Error dialogs

| Title | When | Typical message → what to do |
| --- | --- | --- |
| **Import failed** | Import Data | *No loader for '.xyz' files. Built-in formats: …* → pick a supported file, or add `FILE_EXTENSIONS = [".xyz"]` to a loader plugin ([Instrument Data](../user_guide/data_import.rst)). *Could not load file loader plugin from …* → the plugin file has an error; fix it and **Reload Config Modules**. |
| **Export failed** | Export Data | The folder cannot be written, or there is no data. |
| **Transformation failed** | Apply | *Column '…' does not contain numeric values for transformation.* → choose a numeric Input. *Unknown transformation '…'* → the plugin file is missing; restore it or choose another function. A plugin's own error names the plugin file. |
| **Role update failed** | Changing a role dropdown | Rare. The role could not be stored; try again after the table has data. |
| **Column rename failed** | Renaming a column | The backend rejected the new name. |
| **Rename Column** *(warning)* | Rename dialog | *Column name cannot be empty.* or *Column '…' already exists.* → choose another name. |
| **Plot failed** | Generate Plot | *No column has role 'X'.* → set roles. *Column '…' does not contain numeric data.* → choose numeric columns. LSQ messages → see [Plotter Module](plotter_module.md#when-plotting-fails). *Figure Editor is not installed…* → install FigureForge or use another plotter. |
| **Figure Editor failed** | Shortly after Generate Plot with the Basic Plotter | The editor process exited with an error; the text is its error output. See [Troubleshooting](https://github.com/MShirazAhmad/PhysPlot/wiki/Troubleshooting). |
| **Export plot failed** | Export Plot | *Generate a plot before exporting.* → press Generate Plot first. |
| **Apply sequence failed** | Apply This Sequence | *Build or import a protocol sequence first.*, or *Row N failed (StepName): error* → fix or delete that row and apply again. |
| **Apply revised sequence failed** | Deleting a protocol row | The shortened protocol could not even start. Usually a failing row is shown in the Status column instead, with no dialog. |
| **Rerun failed** | Row menu → Rerun from this step | *No saved state before step N…* → Apply This Sequence once, then rerun. |
| **Apply code to table failed** | Apply Code to Table / switching to Table | *Python syntax error on line N: …* (the line is selected) or another error. The protocol is unchanged. |
| **Load sequence failed** | Import Sequence.py | *Workflow '…' must define WORKFLOW_STEPS or build_workflow().*, or a Python error in the file. |
| **Save workflow failed** | Export Sequence.py | The file cannot be written. |
| **Insert protocol module failed** | Protocol → Insert Protocol Module | The module file has an error or no steps. |
| **Bulk run failed** | Run Bulk Workflow | *Bulk run stopped at <file>: <error>. Files before it … were exported; later files were not run.*, or *Build or import a protocol sequence before running bulk automation.* See [Run Sequence](run_sequence.md#when-a-run-fails). |

## Status-bar messages

| Message | After |
| --- | --- |
| *Ready* | Start-up; a successful import |
| *Folder selected: <name>* | Import Folder |
| *Exported* | Export Data |
| *Transformation applied* | Apply |
| *Enter or import data before applying a transformation* | Apply with an empty Input column (nothing happens) |
| *Plot generated* | Generate Plot |
| *Plot preview updated* | Plot → Update Integrated Preview |
| *Plot exported* | Export Plot |
| *Sequence complete* | Apply This Sequence with every row OK |
| *Row N failed (StepName): error* | A replay that stopped at row N |
| *Sequence updated* | Deleting a protocol row (the rest replayed) |
| *Sequence cleared* | Deleting the last protocol row |
| *Reran from row N* | Rerun from this step |
| *Row N has no replayable step* | Rerun from a note-only row |
| *Sequence code applied* | Apply Code to Table |
| *Sequence loaded* / *Sequence saved* | Import / Export Sequence.py |
| *Sequence script copied* | Copy as Script / Protocol → Copy Sequence Code |
| *Inserted protocol module <name>* | Protocol → Insert Protocol Module |
| *Reloaded config modules from <folder>* | File → Reload Config Modules |
| *Bulk complete: N outputs* | Run Bulk Workflow |
| *<Error title>* | Any failure (see [Error dialogs](#error-dialogs)) |

Long messages end in **…** in the status bar; hover over them to read the full text.

## Running without a display

When PhysPlot runs with `QT_QPA_PLATFORM=offscreen` (tests and CI), error dialogs are
not shown. The title and error are printed to standard error instead, and the window
keeps them in `last_error` so scripts can check them.
