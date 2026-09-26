# PhysPlot Wiki

PhysPlot is a table-first scientific plotting application. You load data into
the central table, assign column roles, apply transformations that are
recorded as a replayable protocol, and plot through backend plotter modules.
The same protocol can be exported as ordinary Python and run headlessly or over
whole folders of files.

![PhysPlot main window](images/getting-started/start_01_window_tour.png)

## Install

**macOS**: paste this into **Terminal**. It installs PhysPlot and creates
**PhysPlot.app** in `~/Applications`:

```bash
curl -fsSL https://raw.githubusercontent.com/MShirazAhmad/PhysPlot/indevelopment/scripts/install_macos.sh | bash
```

**Windows**: paste this into **PowerShell**. It installs PhysPlot and adds it to
the Start menu:

```powershell
irm https://raw.githubusercontent.com/MShirazAhmad/PhysPlot/indevelopment/scripts/install_windows.ps1 | iex
```

Details and other options are in [Getting Started](Getting-Started#install).

## Start here

1. **[Getting Started](Getting-Started)**: install, launch, and a tour of the window.
2. **[GUI Walkthrough](GUI-Walkthrough)**: one complete session with screenshots,
   from importing an XRD scan to a recorded, replayable protocol.
3. **[Sequence Walkthrough](Sequence-Walkthrough)**: record a protocol on one file,
   save it as `Sequence.py`, reopen and edit it, and bulk-process a whole folder.

## UI Reference

Every panel, control, menu, dialog and message, with annotated screenshots:
[Overview](UI-Reference) ·
[Main Window, Menus, Status Bar](UI-Main-Window) ·
[Data Table](UI-Data-Table) ·
[Data Importer](UI-Data-Importer) ·
[Mathematical Transformation](UI-Mathematical-Transformation) ·
[Plotter Module](UI-Plotter-Module) ·
[Build Protocol](UI-Build-Protocol) ·
[Run Sequence](UI-Run-Sequence) ·
[Figure Editor and Plot Windows](UI-Figure-Editor) ·
[Dialogs and Messages](UI-Dialogs-and-Messages)

## Guides

- **[Instrument Data](Instrument-Data)**: loading XRDML, Panalytical CSV,
  EDAX EDS, EMSA, PHI XPS, Rigaku `.ras`, TA Instruments and JCAMP-DX files, and what each
  becomes in the table.
- **[Replayable Plugin Transformations](Replayable-Plugin-Transformations)**:
  `x^2`, `sin(x)`, `XRD: Baseline Remove` and your own functions, recorded and replayed.
- **[Bulk Runs and Headless Use](Bulk-Runs-and-Headless)**: Run Sequence over a
  folder, the `physplot` command line, and exported `Sequence.py` files.
- **[Extending PhysPlot](Extending-PhysPlot)**: writing transformation and file
  loader plugins in `config/`.
- **[Troubleshooting](Troubleshooting)**: every error dialog, what it means, and how to fix it.

## Try it with the sample data

The repository's `test_data/` folder has an example of every supported format,
installed to `Documents\PhysPlot\test_data` on Windows. The files in its instrument
folders keep the layout of real exports, with simulated values.

## Links

- [Full documentation (Read the Docs)](https://physplot.readthedocs.io/en/latest/)
- [Source code](https://github.com/MShirazAhmad/PhysPlot)
- [Report an issue](https://github.com/MShirazAhmad/PhysPlot/issues)
