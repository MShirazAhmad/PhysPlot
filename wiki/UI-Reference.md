# UI Reference

This reference documents every part of the PhysPlot window: each panel, control,
menu item, context menu, dialog and message. Numbered red markers in the
screenshots match the numbered notes on each page. For a guided first session, see
the [GUI Walkthrough](GUI-Walkthrough); for saving and bulk-running a protocol, see the
[Sequence Walkthrough](Sequence-Walkthrough).

![PhysPlot main window with numbered regions](images/walkthrough/walk_01_overview.png)

| Marker | Area | Reference page |
| --- | --- | --- |
| 1 | Header and mode switcher | [Main Window, Menus and Status Bar](UI-Main-Window) |
| 2–4 | Column headers, role row, data cells | [Data Table](UI-Data-Table) |
| 5 | **1. Data Importer** panel (Simple Mode) | [Data Importer](UI-Data-Importer) |
| 6 | **2. Mathematical Transformation** panel (Simple Mode) | [Mathematical Transformation](UI-Mathematical-Transformation) |
| 7 | **3. Plotter Module** panel (Simple Mode) | [Plotter Module](UI-Plotter-Module) |
| 8 | Status bar | [Main Window, Menus and Status Bar](UI-Main-Window#status-bar) |
| – | **Build Protocol** tab (Advanced Mode) | [Build Protocol](UI-Build-Protocol) |
| – | **Run Sequence** tab (Advanced Mode) | [Run Sequence](UI-Run-Sequence) |
| – | Figure Editor window and plot windows | [Figure Editor and Plot Windows](UI-Figure-Editor) |
| – | Every dialog, error and status message | [Dialogs and Messages](UI-Dialogs-and-Messages) |

## How the window is organised

```text
┌──────────────────────────────────────────────────────────────────────┐
│ [LSF][PhysLab]            [PhysPlot logo]        Mode: [Simple][Advanced] │  header
├──────────────────────────────────────────────────────────────────────┤
│      1: Time │ 2: Voltage │ Column 3 │ …                              │  column headers
│      [X ▾]   │ [Y ▾]      │ [Ignore ▾] │ …                            │  role row
│  1   0.0     │ 1.0        │           │                               │
│  2   …       │ …          │           │                               │  data cells
├──────────────────────────────────────────────────────────────────────┤
│ Simple:   [1. Data Importer] [2. Mathematical Transformation] [3. Plotter Module] │
│ Advanced: [Build Protocol | Run Sequence] tabs                        │  mode panel
├──────────────────────────────────────────────────────────────────────┤
│ Status: …                        Rows: n  Columns: n  File: name      │  status bar
└──────────────────────────────────────────────────────────────────────┘
```

- **Table first.** The spreadsheet is always visible. Every panel works on it, and
  every change you make is recorded in the protocol.
- **Two modes, one table.** **Simple** shows the three everyday panels. **Advanced**
  shows the recorded protocol and bulk runs. Switching modes never changes your data.
- **Everything is replayable.** Imports, role changes, cell edits, renames, deletions,
  transformations and plots each become a step in **Build Protocol**. The protocol can
  be replayed, edited as Python, exported as `Sequence.py` and run over folders.

## Keyboard shortcuts

On macOS, **Ctrl** in these shortcuts is the **⌘ Command** key.

| Shortcut | Action |
| --- | --- |
| Ctrl+O | File → Import Data… (Auto Loader) |
| Ctrl+E | File → Export Data… |
| Ctrl+Shift+R | File → Reload Config Modules |
| Ctrl+S | Protocol → Export Sequence.py… |
| Ctrl+R | Protocol → Apply This Sequence |
| Ctrl+1 / Ctrl+2 | View → Simple Mode / Advanced Mode |
| Ctrl+G | Plot → Generate Plot |
| Ctrl+C / Ctrl+V | Copy / paste table cells (tab-separated, works with Excel) |
| Double-click a header | Rename the column |
