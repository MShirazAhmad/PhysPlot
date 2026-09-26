"""Save, list, and re-apply reusable figure templates shared by PhysPlot and the Figure Editor.

A *template* (called a *style module* in the code) is a small JSON file that records how
a Matplotlib figure looks, not what it shows: figure size, DPI and background, the fonts,
sizes and colours of the axes title and axis labels, axis scales, grid, spines, tick-label
size and colour, line and marker styles, scatter/collection colours, and legend settings.
No data, axis limits, or axes-title/axis-label text are stored. PhysPlot applies a
template to each freshly generated plot so that a series of figures looks the same, and
the Figure Editor (FigureForge) writes new templates from a figure that was styled by
hand.

This module has no Qt dependency; it only reads and writes Matplotlib artist properties,
so it can also be used from scripts and notebooks. It is used by
``physplot_gui/app/main_window.py``, ``physplot_gui/panels/simple_mode_panel.py`` and the
Figure Editor plugin ``config/figureforge_plugins/physplot_save_style_module.py``. The
user-facing description of the same controls is in the *GUI Walkthrough* page (section
"Generating, Editing, and Templating a Plot") and in the *UI Reference* page (Simple
Mode, panel "3. Plotter Module", **Template**).

.. rubric:: Where templates are stored

Templates are ``*.json`` files. They are read from these folders, in this order (see
:func:`style_directories`):

1. ``Documents/PhysPlot/config/templates/`` -- the per-user, editable folder (in the
   ``Documents`` folder under ``%USERPROFILE%`` on Windows; the ``PHYSPLOT_USER_DIR``
   environment variable moves the whole ``PhysPlot`` user folder). **File > Open Config
   Folder** opens its parent ``config`` folder. Files here survive reinstalls.
2. ``config/templates/`` inside the PhysPlot installation -- the bundled defaults
   (``DEFAULT_STYLE_DIR``). PhysPlot ships ``Publication_Style.json``, listed as
   "Publication Style".
3. The legacy ``styling/`` folders (per-user, then bundled), still searched so that
   older installations keep working.

Only the first file with a given *file name* is used, so a per-user file named like a
bundled one (for example ``Publication_Style.json``) replaces the bundled template in the
dropdown. New templates are always written to :func:`style_directory`: the per-user
folder when it can be created and written to, otherwise the bundled folder. File names
are derived from the template name by :func:`style_path_from_name`.

Setting the ``PHYSPLOT_STYLE_DIR`` environment variable (``STYLE_DIR_ENV``) replaces all
of the above with one folder that is both searched and written to; bundled templates are
then not listed. When the main window launches the Figure Editor, it sets
``PHYSPLOT_STYLE_DIR`` to its own :func:`style_directory` in the editor's environment, so
**Save as Template** writes into the folder that the **Template** dropdown reads.

.. rubric:: File format

:func:`save_style_module` writes UTF-8 JSON indented by two spaces::

    {
      "schema_version": 1,
      "name": "Publication Style",
      "figure": {"facecolor": "#ffffffff", "edgecolor": "#ffffffff", "dpi": 200.0,
                 "size_inches": [3.82, 3.315], "suptitle": ""},
      "axes": [
        {"facecolor": "...", "title": {...}, "x_label": {...}, "y_label": {...},
         "x_scale": "linear", "y_scale": "linear", "grid": {...},
         "spines": {"left": {...}, "right": {...}, "bottom": {...}, "top": {...}},
         "ticks": {"x": {...}, "y": {...}},
         "lines": [{...}, ...], "collections": [{...}, ...],
         "legend": {...}}
      ]
    }

``schema_version`` is ``STYLE_SCHEMA_VERSION`` (currently 1); it is written but not
checked when a template is loaded. ``name`` is the label shown in the **Template**
dropdown. There is one ``axes`` entry per axes of the figure, in ``figure.get_axes()``
order. Colours are normally stored as ``#rrggbbaa`` hex strings (see :func:`_color`).
Every key is optional when a template is applied, so hand-written or trimmed files work:
a missing key leaves the corresponding property as the plotter module drew it (with the
one exception for axis scales noted below).

.. rubric:: What a template captures and re-applies

Figure (``"figure"``)
    Face (background) colour, edge colour, DPI, size in inches, and the *text* of the
    figure suptitle. The suptitle is re-applied only when it is non-empty, and it is
    re-created with default font settings.

Axes background and scales (``"facecolor"``, ``"x_scale"``, ``"y_scale"``)
    Axes face colour and the x and y scale names (``"linear"``, ``"log"``, ...).

Axes title and axis labels (``"title"``, ``"x_label"``, ``"y_label"``)
    Colour, font size, font family, font style, font weight, and horizontal/vertical
    alignment (:func:`_text_style`). The title and label *text* of the new plot is kept.

Grid (``"grid"``)
    Whether any major gridline is visible, plus colour, line style, line width, and alpha
    of the first visible gridline. On re-apply the grid is switched on for both axes with
    those settings, or switched off when the template grid was hidden.

Spines (``"spines"``)
    For each spine (``left``, ``right``, ``bottom``, ``top``): visibility, colour, line
    width, and line style. Spines that the new axes do not have are ignored.

Tick labels (``"ticks"``)
    Font size and colour of the first x and the first y tick label, re-applied to all
    tick labels of that axis with ``Axes.tick_params``.

Lines (``"lines"``)
    For each ``Line2D`` in ``axes.lines`` (data lines, fit curves, error-bar data lines and
    caps): colour, line style, line width, marker, marker size, marker edge colour,
    marker face colour, and alpha.

Collections (``"collections"``)
    For each collection in ``axes.collections`` (scatter points, error-bar segments,
    filled areas): the first face colour, the first edge colour, the first line width,
    and alpha.

Legend (``"legend"``)
    Visibility, frame on/off, entry font size, title text, title font styling (as for the
    axes title), and Matplotlib's location code. A visible template legend rebuilds the
    legend of the new plot from its labelled artists (or as an empty legend that only
    carries the title); a hidden or missing template legend leaves the new plot's legend
    untouched.

.. rubric:: How a template is matched to a new figure

:func:`apply_style_module` matches strictly **by position**: the first stored ``axes``
entry styles the first axes of the new figure, the first stored line style styles the
first line of that axes, the first stored collection style the first collection, and so
on. Surplus entries on either side are ignored, so a template gives the most predictable
result on figures made by the same plotter module and plot type as the figure it was
saved from. Colorbars and twin axes count as axes in this order (insets created with
``Axes.inset_axes`` are not part of ``figure.get_axes()`` and are not styled). Because the
LSQ fit line of the Plotter Module is drawn before the template is applied, it takes
part in the line matching too.

The axis scales are always set, and setting a scale (even to its current value) makes
Matplotlib reset that axis's tick locator and formatter to the scale's defaults, so
custom tick spacing or number formats drawn by a plotter module do not survive applying
a template. After styling, ``figure.tight_layout()`` is attempted; errors from it are
ignored.

.. rubric:: What a template does not capture

- Data, axis limits, tick positions, tick-label formats, tick direction/length/width,
  and minor ticks.
- The text of the axes title and axis labels (only their font styling), and the left
  and right axes titles.
- Annotations and other text artists, patches (for example bar and histogram
  rectangles), images, and colormaps. For collections only the *first* colour and line
  width are recorded, so per-point colours are not preserved; scatter marker shapes and
  sizes are not recorded.
- Legend options other than those listed above (number of columns, frame colours,
  marker scale, ...), and the font styling of the figure suptitle.
- Matplotlib ``rcParams``.

.. rubric:: Using templates in the PhysPlot window

- **Template** dropdown (Simple Mode, panel "3. Plotter Module", left column): the first
  entry is **None** (no template); the others come from :func:`list_style_modules`,
  sorted by name. Each item remembers the path of its JSON file, and its tooltip shows
  the full name.
- **Reload** (next to the dropdown, tooltip "Re-scan config/templates") re-scans the
  template folders and keeps the current selection when that file is still listed;
  otherwise the dropdown falls back to **None**. **File > Reload Config Modules**
  (Ctrl+Shift+R) does the same, and the dropdown is also rebuilt whenever the main
  window refreshes its panels (for example after loading data, applying a
  transformation, or generating a plot). No restart is needed after adding, editing, or
  deleting a template file.
- **Generate Plot** first lets the chosen plotter module draw the figure (including the
  optional LSQ fit line), then applies the selected template with
  :func:`apply_style_module`, then opens the figure in the Figure Editor (Basic Plotter)
  or in a separate plot window (other plotter modules). **Plot > Generate Plot**
  (Ctrl+G) applies the selected template to a Basic Plotter scatter plot in the same
  way. A missing or malformed template file is reported as "Plot failed".
- **Export Plot** saves the figure at a fixed 300 dpi, so a template's ``dpi`` affects
  the on-screen figure, not the exported resolution.
- The template choice is not stored in the protocol's ``PlotModuleStep``. Replaying the
  protocol, **Run Sequence**, exported ``Sequence.py`` files, and the ``physplot`` CLI
  therefore do not apply a template; only the GUI's Generate Plot actions do.

.. rubric:: Creating a template in the Figure Editor

1. Generate a plot and style it in the Figure Editor (Property Inspector).
2. Select the Figure, an Axes, or any artist of the figure and choose **Figure Editor >
   PhysPlot > Save as Template**. With nothing suitable selected, a warning asks for a
   selection.
3. In the "Save as Template" dialog, type a **Name** (default "Publication Style"). The
   read-only **Saved as** field shows the target path from :func:`style_path_from_name`
   while you type. **OK** calls :func:`save_style_module`; a message box reports the
   saved path, and failures are shown as "Could not save template." with the reason.
4. In PhysPlot, click **Reload** next to **Template** (or trigger any other refresh)
   and select the new entry before **Generate Plot**.

Saving under a name that maps to an existing file overwrites that file without asking.
The default name maps to ``Publication_Style.json``, so saving with it replaces the
bundled "Publication Style" entry in the dropdown.

Before a figure is opened in the Figure Editor, PhysPlot adds hidden placeholder artists
to every axes that lacks that kind of artist: an empty line (label
``_physplot_template_line``), an empty scatter (``_physplot_template_scatter``), a hidden
empty legend, and a hidden empty annotation (``_physplot_template_annotation``). When a
template is saved, placeholder lines and scatters are skipped (:func:`_is_template_artist`),
so styling them has no effect on the template; annotations are never saved; and the
legend is saved like any other legend, so it is only re-applied if it was made visible.

.. rubric:: Using templates from Python

::

    from physplot_gui.plot_styles import apply_style_module, save_style_module

    path = save_style_module(styled_figure, "My Lab Style")  # .../My_Lab_Style.json
    apply_style_module(new_figure, path)  # a loaded template dict works as well

.. rubric:: Module constants

``STYLE_SCHEMA_VERSION``
    Value written to ``schema_version`` (currently 1).

``STYLE_DIR_ENV``
    Name of the override environment variable, ``"PHYSPLOT_STYLE_DIR"``.

``DEFAULT_STYLE_DIR``
    The bundled ``config/templates`` folder, resolved at import time. The functions in
    this module do not use it; their search order comes from
    ``physplot.user_paths.plugin_search_dirs``.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

from physplot.user_paths import bundled_plugin_dir, plugin_search_dirs, writable_plugin_dir


STYLE_SCHEMA_VERSION = 1
STYLE_DIR_ENV = "PHYSPLOT_STYLE_DIR"
DEFAULT_STYLE_DIR = bundled_plugin_dir("templates")


def style_directory() -> Path:
    """Return the folder new templates are written to.

    If ``PHYSPLOT_STYLE_DIR`` is set, that folder is returned (with ``~`` expanded)
    without being created; :func:`save_style_module` creates it on the first save.
    Otherwise the result is ``writable_plugin_dir("templates")``: the per-user
    ``Documents/PhysPlot/config/templates`` folder, which is created if possible, or the
    bundled ``config/templates`` folder when the per-user folder cannot be created or
    written to.

    Used by :func:`style_path_from_name` (and therefore by the **Saved as** preview of the
    Figure Editor's "Save as Template" dialog and by :func:`save_style_module`), and by
    the main window, which passes this path to the Figure Editor process as
    ``PHYSPLOT_STYLE_DIR``.

    :returns: Folder for new template files.
    """
    configured = os.environ.get(STYLE_DIR_ENV)
    if configured:
        return Path(configured).expanduser()
    return writable_plugin_dir("templates")


def style_directories() -> list[Path]:
    """Return every folder searched for templates, editable folder first.

    Without ``PHYSPLOT_STYLE_DIR`` the order is:

    1. the per-user ``Documents/PhysPlot/config/templates`` folder,
    2. the bundled ``config/templates`` folder,
    3. the legacy per-user ``Documents/PhysPlot/styling`` folder,
    4. the legacy bundled ``styling`` folder,

    with duplicates removed. With ``PHYSPLOT_STYLE_DIR`` set, only that folder (with
    ``~`` expanded) is returned, so bundled templates are not listed. Folders are not
    checked for existence here; :func:`list_style_modules` skips missing ones.

    :returns: Folders in priority order. When two folders hold a file with the same
        name, the file in the earlier folder wins.
    """
    configured = os.environ.get(STYLE_DIR_ENV)
    if configured:
        return [Path(configured).expanduser()]
    return plugin_search_dirs("templates")


def style_path_from_name(name: str) -> Path:
    """Return the JSON file path that a template called *name* is saved to.

    The name is stripped of surrounding whitespace, every run of characters other than
    ASCII letters, digits, ``_``, ``.`` and ``-`` is replaced by a single ``_``, and
    leading or trailing ``.`` and ``_`` characters are removed. An empty result becomes
    ``physplot_style``. The file is placed in :func:`style_directory`. Examples:
    ``"Publication Style"`` gives ``Publication_Style.json``, ``" My/Lab  Style! "``
    gives ``My_Lab_Style.json``, and ``"!!!"`` gives ``physplot_style.json``.

    The read-only **Saved as** field of the Figure Editor's "Save as Template" dialog
    shows this path while the name is typed. Different names can map to the same file
    (for example ``"My Style"`` and ``"My_Style"``); whether the file already exists is
    not checked.

    :param name: Template display name, as typed in the dialog. Non-string values are
        converted with ``str()``.
    :returns: ``<style_directory()>/<safe name>.json``.
    """
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(name).strip()).strip("._")
    if not safe:
        safe = "physplot_style"
    return style_directory() / f"{safe}.json"


def list_style_modules() -> list[dict]:
    """List every template that the **Template** dropdown can offer.

    Scans :func:`style_directories` in priority order and reads each ``*.json`` file
    directly inside each folder (sub-folders are not searched), in file-name order.
    Missing folders are ignored. A file is skipped when a file with the same *file name*
    was already taken from an earlier folder, and it is skipped silently when it cannot
    be read or parsed as JSON, so a broken file simply does not appear. The top-level
    JSON value must be an object and its ``"name"``, if present, a string; otherwise
    listing fails with an exception instead of skipping the file.

    The display name is the file's ``"name"`` value, or the file stem when that is
    missing or empty. Display names are not de-duplicated, so two files with the same
    ``"name"`` both appear.

    The main window (``MainWindow.style_module_entries``) puts a ``{"name": "None",
    "path": None}`` entry in front of this list, and Simple Mode refills the dropdown from
    it each time it is refreshed: by **Reload**, by **File > Reload Config Modules**, and
    by every panel refresh of the main window.

    :returns: One ``{"name": str, "path": str}`` dict per template, sorted
        case-insensitively by ``"name"``.
    """
    entries = []
    seen = set()
    for directory in style_directories():
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.json")):
            if path.name in seen:
                continue
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                continue
            seen.add(path.name)
            entries.append(
                {
                    "name": payload.get("name") or path.stem,
                    "path": str(path),
                }
            )
    return sorted(entries, key=lambda entry: entry["name"].lower())


def save_style_module(figure, name: str, path: str | Path | None = None) -> Path:
    """Capture the styling of *figure* and write it as a template JSON file.

    Builds the payload with :func:`extract_style_module` and writes it as UTF-8 JSON
    indented by two spaces. Missing parent folders are created, and an existing file is
    overwritten without warning. **Figure Editor > PhysPlot > Save as Template** calls
    this function with *path* left as ``None``.

    :param figure: Matplotlib ``Figure`` whose appearance is captured; it is only read.
    :param name: Display name stored in the file's ``"name"`` field and shown in the
        **Template** dropdown. Also used to derive the file name when *path* is omitted.
    :param path: Explicit output file. When ``None`` or empty, the path from
        :func:`style_path_from_name` for *name* is used.
    :returns: Path of the written file.
    """
    output = Path(path) if path else style_path_from_name(name)
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = extract_style_module(figure, name)
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return output


def load_style_module(path: str | Path) -> dict:
    """Read a template JSON file and return its contents.

    Nothing is validated: ``schema_version`` is not checked and missing keys are
    accepted (:func:`apply_style_module` treats every key as optional).

    :param path: Template file.
    :returns: The decoded JSON, normally a dict with ``schema_version``, ``name``,
        ``figure`` and ``axes``.
    :raises OSError: If the file cannot be read (for example because it was deleted).
    :raises json.JSONDecodeError: If the file is not valid JSON.
    """
    return json.loads(Path(path).read_text(encoding="utf-8"))


def apply_style_module(figure, path_or_payload: str | Path | dict | None) -> None:
    """Apply a saved template to *figure* in place.

    Does nothing when *path_or_payload* is ``None`` or otherwise empty, which is what the
    **None** entry of the **Template** dropdown passes. A string or ``Path`` is read with
    :func:`load_style_module`; a dict is used as it is. Then:

    1. the ``"figure"`` settings are applied (:func:`_apply_figure_style`);
    2. the *n*-th entry of ``"axes"`` is applied to the *n*-th axes of
       ``figure.get_axes()`` (:func:`_apply_axes_style`); axes without a matching entry
       and entries without a matching axes are left alone;
    3. ``figure.tight_layout()`` is attempted, and any error from it is ignored.

    Plot data and the text of the axes title and axis labels are kept; the module
    docstring lists exactly which properties change. The GUI calls this function after
    the plotter module (and the optional LSQ fit overlay) has drawn the figure and before
    the figure is opened in the Figure Editor or shown in a plot window.

    Invalid property values in the template raise whatever error Matplotlib raises. In
    the GUI, these errors and the ones listed below are reported as "Plot failed".

    :param figure: Matplotlib ``Figure`` to restyle.
    :param path_or_payload: Template file path, an already loaded template dict, or
        ``None``/empty for "no template".
    :raises OSError: If a template path cannot be read.
    :raises json.JSONDecodeError: If a template file is not valid JSON.
    """
    if not path_or_payload:
        return
    payload = load_style_module(path_or_payload) if isinstance(path_or_payload, (str, Path)) else path_or_payload
    _apply_figure_style(figure, payload.get("figure", {}))
    axes_payloads = payload.get("axes", [])
    for index, axes in enumerate(figure.get_axes()):
        if index < len(axes_payloads):
            _apply_axes_style(axes, axes_payloads[index])
    try:
        figure.tight_layout()
    except Exception:
        pass


def extract_style_module(figure, name: str) -> dict:
    """Return the template payload that describes the current styling of *figure*.

    This is the dict that :func:`save_style_module` writes to disk (the module docstring
    shows its layout): ``schema_version`` (``STYLE_SCHEMA_VERSION``), ``name``, the
    figure-level settings from :func:`_extract_figure_style`, and one entry per axes
    from :func:`_extract_axes_style`, in ``figure.get_axes()`` order.

    :param figure: Matplotlib ``Figure`` to inspect; it is not modified.
    :param name: Display name to store in the payload.
    :returns: Template dict with keys ``schema_version``, ``name``, ``figure`` and
        ``axes``.
    """
    return {
        "schema_version": STYLE_SCHEMA_VERSION,
        "name": name,
        "figure": _extract_figure_style(figure),
        "axes": [_extract_axes_style(axes) for axes in figure.get_axes()],
    }


def _extract_figure_style(figure) -> dict:
    """Return the figure-level part of a template.

    Records the figure face colour and edge colour (as hex strings), the DPI, the size in
    inches as ``[width, height]``, and the suptitle text, read from Matplotlib's private
    ``Figure._suptitle`` (``""`` when there is none). The suptitle's font settings are
    not recorded.

    :param figure: Matplotlib ``Figure`` to inspect.
    :returns: Dict with keys ``facecolor``, ``edgecolor``, ``dpi``, ``size_inches`` and
        ``suptitle``.
    """
    return {
        "facecolor": _color(figure.get_facecolor()),
        "edgecolor": _color(figure.get_edgecolor()),
        "dpi": figure.get_dpi(),
        "size_inches": list(figure.get_size_inches()),
        "suptitle": figure._suptitle.get_text() if getattr(figure, "_suptitle", None) is not None else "",
    }


def _extract_axes_style(axes) -> dict:
    """Return the template entry for one axes.

    Records the axes face colour; the font styling (not the text) of the axes title and
    of the x and y axis labels via :func:`_text_style`; the x and y scale names; the grid
    via :func:`_grid_style`; the visibility, colour, line width and line style of every
    spine; the tick-label size and colour of each axis via :func:`_tick_style`; the style
    of every line in ``axes.lines`` and every collection in ``axes.collections``, in
    drawing order and without PhysPlot's placeholders (:func:`_is_template_artist`); and
    the legend.

    The legend entry holds ``visible`` (``False`` when there is no legend or it is
    hidden), ``frame_on``, ``fontsize`` (from the first entry, see
    :func:`_legend_fontsize`), the ``title`` text, ``title_style`` (font styling as for
    the axes title), and ``loc`` (Matplotlib's internal location code, or ``"best"`` when
    there is no legend).

    :param axes: Matplotlib ``Axes`` to inspect.
    :returns: Dict with keys ``facecolor``, ``title``, ``x_label``, ``y_label``,
        ``x_scale``, ``y_scale``, ``grid``, ``spines``, ``ticks``, ``lines``,
        ``collections`` and ``legend``.
    """
    legend = axes.get_legend()
    return {
        "facecolor": _color(axes.get_facecolor()),
        "title": _text_style(axes.title),
        "x_label": _text_style(axes.xaxis.label),
        "y_label": _text_style(axes.yaxis.label),
        "x_scale": axes.get_xscale(),
        "y_scale": axes.get_yscale(),
        "grid": _grid_style(axes),
        "spines": {
            name: {
                "visible": spine.get_visible(),
                "color": _color(spine.get_edgecolor()),
                "linewidth": spine.get_linewidth(),
                "linestyle": spine.get_linestyle(),
            }
            for name, spine in axes.spines.items()
        },
        "ticks": {
            "x": _tick_style(axes, "x"),
            "y": _tick_style(axes, "y"),
        },
        "lines": [_line_style(line) for line in axes.lines if not _is_template_artist(line)],
        "collections": [_collection_style(collection) for collection in axes.collections if not _is_template_artist(collection)],
        "legend": {
            "visible": legend is not None and legend.get_visible(),
            "frame_on": legend.get_frame_on() if legend is not None else True,
            "fontsize": _legend_fontsize(legend),
            "title": legend.get_title().get_text() if legend is not None else "",
            "title_style": _text_style(legend.get_title()) if legend is not None else {},
            "loc": getattr(legend, "_loc", "best") if legend is not None else "best",
        },
    }


def _apply_figure_style(figure, style: dict) -> None:
    """Apply the figure-level part of a template.

    Sets the face colour, edge colour, DPI and size in inches for each key that is
    present. The suptitle is set with ``figure.suptitle`` only when the stored text is
    non-empty; an empty or missing suptitle leaves any existing suptitle in place.

    :param figure: Matplotlib ``Figure`` to modify.
    :param style: The template's ``"figure"`` dict; missing keys are skipped.
    """
    if "facecolor" in style:
        figure.set_facecolor(style["facecolor"])
    if "edgecolor" in style:
        figure.set_edgecolor(style["edgecolor"])
    if "dpi" in style:
        figure.set_dpi(style["dpi"])
    if "size_inches" in style:
        figure.set_size_inches(style["size_inches"])
    if style.get("suptitle"):
        figure.suptitle(style["suptitle"])


def _apply_axes_style(axes, style: dict) -> None:
    """Apply one template axes entry to *axes*.

    Applies, in this order: the face colour; the x and y scales; the font styling of the
    title and axis labels (the new plot's text is kept); the grid
    (:func:`_apply_grid_style`); the spines that exist on *axes* (visibility, colour,
    line width, line style); tick-label size and colour (:func:`_apply_tick_style`); the
    line and collection styles, paired by position with ``axes.lines`` and
    ``axes.collections`` (surplus items on either side are ignored); and finally the
    legend (:func:`_apply_legend_style`).

    The scales are always set, to the stored value or, when the key is missing, to the
    current one. Setting a scale makes Matplotlib reset that axis's tick locator and
    formatter to the scale's defaults.

    :param axes: Matplotlib ``Axes`` to modify.
    :param style: One entry of the template's ``"axes"`` list; other missing keys are
        skipped.
    """
    if "facecolor" in style:
        axes.set_facecolor(style["facecolor"])
    axes.set_xscale(style.get("x_scale", axes.get_xscale()))
    axes.set_yscale(style.get("y_scale", axes.get_yscale()))
    _apply_text_style(axes.title, style.get("title", {}), preserve_text=True)
    _apply_text_style(axes.xaxis.label, style.get("x_label", {}), preserve_text=True)
    _apply_text_style(axes.yaxis.label, style.get("y_label", {}), preserve_text=True)
    _apply_grid_style(axes, style.get("grid", {}))
    for name, spine_style in style.get("spines", {}).items():
        if name in axes.spines:
            spine = axes.spines[name]
            spine.set_visible(spine_style.get("visible", spine.get_visible()))
            if "color" in spine_style:
                spine.set_edgecolor(spine_style["color"])
            if "linewidth" in spine_style:
                spine.set_linewidth(spine_style["linewidth"])
            if "linestyle" in spine_style:
                spine.set_linestyle(spine_style["linestyle"])
    _apply_tick_style(axes, "x", style.get("ticks", {}).get("x", {}))
    _apply_tick_style(axes, "y", style.get("ticks", {}).get("y", {}))
    for line, line_style in zip(axes.lines, style.get("lines", [])):
        _apply_line_style(line, line_style)
    for collection, collection_style in zip(axes.collections, style.get("collections", [])):
        _apply_collection_style(collection, collection_style)
    _apply_legend_style(axes, style.get("legend", {}))


def _text_style(text) -> dict:
    """Return the font styling of a Matplotlib ``Text`` artist, without its string.

    :param text: ``Text`` artist such as ``axes.title``, an axis label, or a legend
        title.
    :returns: Dict with ``color`` (hex), ``fontsize``, ``fontfamily`` (list of family
        names), ``fontstyle``, ``fontweight``, ``ha`` and ``va`` (horizontal and
        vertical alignment).
    """
    return {
        "color": _color(text.get_color()),
        "fontsize": text.get_fontsize(),
        "fontfamily": list(text.get_fontfamily()),
        "fontstyle": text.get_fontstyle(),
        "fontweight": text.get_fontweight(),
        "ha": text.get_ha(),
        "va": text.get_va(),
    }


def _apply_text_style(text, style: dict, preserve_text: bool = False) -> None:
    """Apply font styling from :func:`_text_style` to a ``Text`` artist.

    Each of ``color``, ``fontsize``, ``fontfamily``, ``fontstyle``, ``fontweight``,
    ``ha`` and ``va`` is set only when it is present in *style*.

    :param text: ``Text`` artist to modify.
    :param style: Font-style dict; may be empty.
    :param preserve_text: When ``True``, the artist's current string is written back
        after styling, so the new plot's title or label text is kept.
    """
    existing = text.get_text()
    if "color" in style:
        text.set_color(style["color"])
    if "fontsize" in style:
        text.set_fontsize(style["fontsize"])
    if "fontfamily" in style:
        text.set_fontfamily(style["fontfamily"])
    if "fontstyle" in style:
        text.set_fontstyle(style["fontstyle"])
    if "fontweight" in style:
        text.set_fontweight(style["fontweight"])
    if "ha" in style:
        text.set_ha(style["ha"])
    if "va" in style:
        text.set_va(style["va"])
    if preserve_text:
        text.set_text(existing)


def _line_style(line) -> dict:
    """Return the style of one ``Line2D``.

    :param line: Line artist, for example a data line, a fit curve, or an error-bar cap.
    :returns: Dict with ``color``, ``linestyle``, ``linewidth``, ``marker``,
        ``markersize``, ``markeredgecolor``, ``markerfacecolor`` (colours as hex) and
        ``alpha`` (``None`` when not set).
    """
    return {
        "color": _color(line.get_color()),
        "linestyle": line.get_linestyle(),
        "linewidth": line.get_linewidth(),
        "marker": line.get_marker(),
        "markersize": line.get_markersize(),
        "markeredgecolor": _color(line.get_markeredgecolor()),
        "markerfacecolor": _color(line.get_markerfacecolor()),
        "alpha": line.get_alpha(),
    }


def _apply_line_style(line, style: dict) -> None:
    """Apply a :func:`_line_style` dict to a ``Line2D``, setting only the keys present.

    :param line: Line artist to modify.
    :param style: Line-style dict from a template.
    """
    for setter, key in (
        (line.set_color, "color"),
        (line.set_linestyle, "linestyle"),
        (line.set_linewidth, "linewidth"),
        (line.set_marker, "marker"),
        (line.set_markersize, "markersize"),
        (line.set_markeredgecolor, "markeredgecolor"),
        (line.set_markerfacecolor, "markerfacecolor"),
        (line.set_alpha, "alpha"),
    ):
        if key in style:
            setter(style[key])


def _collection_style(collection) -> dict:
    """Return the style of one collection (scatter points, error-bar segments, fills).

    Only the *first* face colour, edge colour and line width are recorded, so per-point
    colours are not preserved. Marker shapes and sizes are not recorded.

    :param collection: Matplotlib ``Collection`` to inspect.
    :returns: Dict with ``facecolor`` and ``edgecolor`` (hex, or ``None`` when the
        collection has no such colours), ``linewidth`` (float or ``None``) and
        ``alpha``.
    """
    return {
        "facecolor": _first_color(collection.get_facecolors()),
        "edgecolor": _first_color(collection.get_edgecolors()),
        "linewidth": _first_value(collection.get_linewidths()),
        "alpha": collection.get_alpha(),
    }


def _apply_collection_style(collection, style: dict) -> None:
    """Apply a :func:`_collection_style` dict to a collection.

    The face and edge colours are applied only when non-empty, the line width only when
    it is not ``None``, and ``alpha`` whenever the key is present (a stored ``None``
    removes any alpha).

    :param collection: Matplotlib ``Collection`` to modify.
    :param style: Collection-style dict from a template.
    """
    if style.get("facecolor"):
        collection.set_facecolor(style["facecolor"])
    if style.get("edgecolor"):
        collection.set_edgecolor(style["edgecolor"])
    if style.get("linewidth") is not None:
        collection.set_linewidth(style["linewidth"])
    if "alpha" in style:
        collection.set_alpha(style["alpha"])


def _grid_style(axes) -> dict:
    """Return the major-grid style of *axes*.

    The grid counts as visible if any x or y major gridline is visible. Colour, line
    style, line width and alpha are taken from the first visible gridline, or from the
    first gridline when none is visible. Without any gridlines the defaults
    ``"#b0b0b0"``, ``"-"``, ``0.8`` and ``None`` are recorded.

    :param axes: Matplotlib ``Axes`` to inspect.
    :returns: Dict with ``visible``, ``color``, ``linestyle``, ``linewidth`` and
        ``alpha``.
    """
    gridlines = axes.get_xgridlines() + axes.get_ygridlines()
    visible = any(line.get_visible() for line in gridlines)
    sample = next((line for line in gridlines if line.get_visible()), gridlines[0] if gridlines else None)
    return {
        "visible": visible,
        "color": _color(sample.get_color()) if sample is not None else "#b0b0b0",
        "linestyle": sample.get_linestyle() if sample is not None else "-",
        "linewidth": sample.get_linewidth() if sample is not None else 0.8,
        "alpha": sample.get_alpha() if sample is not None else None,
    }


def _apply_grid_style(axes, style: dict) -> None:
    """Apply a :func:`_grid_style` dict to *axes*.

    An empty dict changes nothing. When ``visible`` is false or missing, the grid is
    switched off; otherwise it is switched on for both axes with the stored colour, line
    style, line width and alpha (falling back to ``"#b0b0b0"``, ``"-"`` and ``0.8``). A
    grid on only the x or only the y axis is therefore not reproduced.

    :param axes: Matplotlib ``Axes`` to modify.
    :param style: Grid dict from a template.
    """
    if not style:
        return
    if not style.get("visible", False):
        axes.grid(False)
        return
    axes.grid(
        True,
        color=style.get("color", "#b0b0b0"),
        linestyle=style.get("linestyle", "-"),
        linewidth=style.get("linewidth", 0.8),
        alpha=style.get("alpha"),
    )


def _tick_style(axes, axis: str) -> dict:
    """Return the tick-label styling of one axis.

    Reads the font size and colour of the first tick label; both are ``None`` when the
    axis has no tick labels. Tick positions, direction, length and label format are not
    recorded.

    :param axes: Matplotlib ``Axes`` to inspect.
    :param axis: ``"x"``, or ``"y"`` (any other value is treated as ``"y"``).
    :returns: Dict with ``labelsize`` and ``labelcolor``.
    """
    labels = axes.get_xticklabels() if axis == "x" else axes.get_yticklabels()
    sample = labels[0] if labels else None
    return {
        "labelsize": sample.get_fontsize() if sample is not None else None,
        "labelcolor": _color(sample.get_color()) if sample is not None else None,
    }


def _apply_tick_style(axes, axis: str, style: dict) -> None:
    """Apply a :func:`_tick_style` dict to one axis with ``Axes.tick_params``.

    The label size is applied when it is not ``None`` and the label colour when it is
    non-empty; when neither is available nothing changes.

    :param axes: Matplotlib ``Axes`` to modify.
    :param axis: ``"x"`` or ``"y"``.
    :param style: Tick-style dict from a template; may be empty.
    """
    if not style:
        return
    kwargs = {}
    if style.get("labelsize") is not None:
        kwargs["labelsize"] = style["labelsize"]
    if style.get("labelcolor"):
        kwargs["labelcolor"] = style["labelcolor"]
    if kwargs:
        axes.tick_params(axis=axis, **kwargs)


def _apply_legend_style(axes, style: dict) -> None:
    """Rebuild the legend of *axes* from a template's legend settings.

    Nothing happens when the stored legend was not visible or *style* is empty; the
    plot's existing legend, if any, is left as it is. Otherwise a new legend replaces
    any existing one. It is built from the labelled artists of *axes*
    (``Axes.get_legend_handles_labels``), or as an empty legend when there are none,
    with the stored location, frame setting and title. The stored font size is then
    applied to every entry, the stored title font styling to the title, and finally the
    title text is set.

    :param axes: Matplotlib ``Axes`` to modify.
    :param style: Legend dict produced by :func:`_extract_axes_style`.
    """
    if not style.get("visible"):
        return
    handles, labels = axes.get_legend_handles_labels()
    title = style.get("title", "")
    if handles:
        legend = axes.legend(handles, labels, loc=style.get("loc", "best"), frameon=style.get("frame_on", True), title=title)
    else:
        legend = axes.legend([], [], loc=style.get("loc", "best"), frameon=style.get("frame_on", True), title=title)
    fontsize = style.get("fontsize")
    if fontsize is not None:
        for text in legend.get_texts():
            text.set_fontsize(fontsize)
    _apply_text_style(legend.get_title(), style.get("title_style", {}), preserve_text=False)
    legend.get_title().set_text(title)


def _legend_fontsize(legend):
    """Return the font size of the first legend entry.

    :param legend: Matplotlib ``Legend``, or ``None``.
    :returns: Font size in points, or ``None`` when there is no legend or it has no
        entries.
    """
    if legend is None or not legend.get_texts():
        return None
    return legend.get_texts()[0].get_fontsize()


def _color(value):
    """Convert a Matplotlib colour to a ``#rrggbbaa`` hex string.

    Matplotlib is imported here, on first use. If the value cannot be converted,
    ``str(value)`` is returned instead.

    :param value: Any Matplotlib colour specification (name, hex string, RGB or RGBA
        tuple, ...).
    :returns: Hex colour including alpha, or the string form of *value*.
    """
    try:
        from matplotlib.colors import to_hex

        return to_hex(value, keep_alpha=True)
    except Exception:
        return str(value)


def _first_color(values):
    """Return the first colour of a colour array as a hex string.

    :param values: Array of colours, as returned by ``get_facecolors()`` or
        ``get_edgecolors()``.
    :returns: Hex string from :func:`_color`, or ``None`` when the array is empty or
        cannot be read.
    """
    try:
        if len(values) == 0:
            return None
        return _color(values[0])
    except Exception:
        return None


def _first_value(values):
    """Return the first value of a sequence as a ``float``.

    :param values: Sequence such as ``collection.get_linewidths()``.
    :returns: The first value, or ``None`` when the sequence is empty or the value
        cannot be converted.
    """
    try:
        if len(values) == 0:
            return None
        return float(values[0])
    except Exception:
        return None


def _is_template_artist(artist) -> bool:
    """Return whether *artist* is one of PhysPlot's hidden Figure Editor placeholders.

    Before opening the Figure Editor, the main window adds invisible placeholder artists
    whose labels start with ``_physplot_template`` (``_physplot_template_line``,
    ``_physplot_template_scatter`` and ``_physplot_template_annotation``).
    :func:`_extract_axes_style` uses this check to leave placeholder lines and scatters
    out of a template.

    :param artist: Any Matplotlib artist.
    :returns: ``True`` if its label starts with ``_physplot_template``; ``False``
        otherwise, including when the label cannot be read.
    """
    try:
        return str(artist.get_label()).startswith("_physplot_template")
    except Exception:
        return False
