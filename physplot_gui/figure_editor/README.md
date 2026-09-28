# Figure Editor (PhysPlot's copy of FigureForge)

This folder is PhysPlot's own, editable copy of
[FigureForge](https://github.com/nogula/FigureForge) 0.3.3 by Noah Gula, used under the
MIT License (see `LICENSE`, which must stay with this code). PhysPlot no longer depends on
the `FigureForge` package from PyPI; change the editor here.

Nothing in the interface carries the FigureForge name or logo: the editor is
"PhysPlot Figure Editor". This README and `LICENSE` keep the MIT attribution.

Changes from upstream 0.3.3:

- Imports use `physplot_gui.figure_editor` instead of `FigureForge`; `__init__.py` defines
  its constants before importing the plugins (no circular import).
- `gui.py` also loads plugins in place from the folders listed in the
  `PHYSPLOT_FIGURE_EDITOR_PLUGIN_DIRS` environment variable (PhysPlot passes
  `config/figureforge_plugins` and the per-user copy), so they are never copied in here.

- Ported from PySide6 to PyQt6 (full enum names, `pyqtSignal`, `exec()`), so it shares
  PyQt6 and Matplotlib with the rest of PhysPlot and runs in PhysPlot's process.
- qdarktheme removed: it restyles the whole application, so the editor follows PhysPlot's
  look and the Theme preference is hidden.
- `FigureManager` edits a figure it is given in place (PhysPlot's plot window shares it)
  instead of copying its attributes into a new `Figure`.
- `MainWindow.linked_managers`: figures that live in PhysPlot; closing them never asks to
  save.
- Click (or right-click) the figure: `FigureManager.on_canvas_press` opens the most specific
  editable part under the mouse (`artists_at`) in the Property Inspector and highlights it
  in the Figure Explorer (`FigureExplorer.select_object`). Clicking the same spot again
  cycles through the overlapping parts; `selectionMessage` names the selection in the
  status bar.

- Rebranded: PhysPlot name and icon; FigureForge's logo, splash, welcome screen, online
  update check, About and bug-report dialogs removed; Help points to PhysPlot's docs.
- Toolbar and File menu: *Export Figure* (`dialogs/physplot_export.py`: format, DPI,
  size, transparency, formatting as shown or a PhysPlot template, live preview) and
  *Export Style* (saves the formatting as a PhysPlot template).
- Figure Explorer uses readable names (`friendly_name`) and hides helpers
  (`is_hidden_part`); the Property Inspector is Property | Value, fitting the panel.
- Number fields show the current value (upstream showed 0.0).

PhysPlot opens the editor with `MainWindow._open_figure_editor(figure, plot_canvas)`
in `physplot_gui/app/main_window.py`.
