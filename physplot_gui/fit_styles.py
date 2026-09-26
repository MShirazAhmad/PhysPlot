"""Discover, load, and save reusable LSQ fit-line style presets for Simple Mode.

A *fit-style preset* is a small JSON file holding the appearance options of the
least-squares (LSQ) fit line that the Plotter Module can draw over a plot: its legend
label, line style, line width, and whether the legend is redrawn. Presets only fill in
the **Fit Line** fields of Simple Mode; they contain no fit function, parameter names,
or initial guesses. This module has no Qt dependency.

The user-facing description is in the *GUI Walkthrough* page (section "Generating,
Editing, and Templating a Plot") and in the *UI Reference* page (Simple Mode, panel
"3. Plotter Module", **Fit Style** and **Fit Line**).

.. rubric:: Where presets are stored

Presets are ``*.json`` files. They are read from these folders, in this order (see
:func:`fit_style_directories`):

1. ``Documents/PhysPlot/config/figureforge_fit_styles/`` -- the per-user, editable
   folder (in the ``Documents`` folder under ``%USERPROFILE%`` on Windows; the
   ``PHYSPLOT_USER_DIR`` environment variable moves the whole ``PhysPlot`` user folder).
   **File > Open Config Folder** opens its parent ``config`` folder.
2. ``config/figureforge_fit_styles/`` inside the PhysPlot installation -- the bundled
   defaults (``DEFAULT_FIT_STYLE_DIR``). PhysPlot ships ``Default LSQ Fit.json``, listed
   as "Default LSQ Fit".

Only the first file with a given *file name* is used, so a per-user file named like a
bundled one replaces it in the dropdown. New presets are written to
:func:`fit_style_directory`: the per-user folder when it can be created and written to,
otherwise the bundled folder. Setting the ``PHYSPLOT_FIT_STYLE_DIR`` environment variable
(``FIT_STYLE_DIR_ENV``) replaces both folders with one folder that is both searched and
written to.

.. rubric:: File format

::

    {
      "schema_version": 1,
      "name": "Default LSQ Fit",
      "line_style": "--",
      "line_width": 2.0,
      "label": "",
      "show_legend": true
    }

``schema_version``
    ``FIT_STYLE_SCHEMA_VERSION`` (currently 1); written but never checked.

``name``
    Label shown in the **Fit Style** dropdown. The file stem is used when it is missing
    or empty.

``line_style``
    Matplotlib line style of the fit curve. The Simple Mode line-style menu offers
    ``"--"`` (dashed), ``"-"`` (solid), ``"-."`` (dash-dot) and ``":"`` (dotted); a
    preset value outside this list is ignored when the preset is chosen.

``line_width``
    Line width of the fit curve in points.

``label``
    Legend label of the fit curve. When the label is empty, PhysPlot generates one of the
    form ``LSQ fit: <expression> (a=..., b=...)`` from the fitted parameters.

``show_legend``
    When true, the legend is redrawn after the fit line is added, so it includes the
    fit; when false, the legend is not redrawn.

Other keys are ignored by the GUI and dropped by :func:`normalize_fit_style_payload`.

.. rubric:: Using presets in the PhysPlot window

- **Fit Style** dropdown (Simple Mode, panel "3. Plotter Module", right-hand fit
  column): the first entry is **Default**, followed by the presets from
  :func:`list_fit_style_presets`, sorted by name. Each item remembers its file path and
  the full contents of the preset.
- Choosing a preset copies its values into the **Fit Line** row: ``label`` into the
  label box, ``line_style`` into the line-style menu (only if it is one of the four
  values above), ``line_width`` into the width box, and ``show_legend`` into the
  **Legend** checkbox. Keys missing from the file fall back to ``""``, ``"--"``,
  ``2.0`` and ``True``, so a preset without ``label`` clears the label box.
- Choosing **Default** changes nothing: the fields keep their current values (at start
  up an empty label, ``--``, width ``2`` and **Legend** ticked).
- The fields can still be edited by hand after a preset is chosen. Choosing a preset
  does not tick **LSQ fit**; the fit line is only drawn when that box is ticked.
- **Reload** (next to the dropdown, tooltip "Re-scan config/figureforge_fit_styles")
  re-scans the preset folders and keeps the current selection when its file is still
  listed; otherwise **Default** is selected. **File > Reload Config Modules**
  (Ctrl+Shift+R) does the same. Reloading does not copy values into the **Fit Line**
  fields again: after editing a preset file, reload, then select another entry and the
  preset again.
- On **Generate Plot** with **LSQ fit** ticked, the current field values (not the preset
  name) are sent to the backend as the plot's ``lsq_fit`` settings and are recorded in
  the protocol's ``PlotModuleStep``, so replays and bulk runs draw the same fit line
  without needing the preset file. An unreadable width is sent as ``2.0``.
- The GUI has no button that saves a preset. Create one by placing a JSON file in the
  per-user folder, or from Python with :func:`save_fit_style_preset`.

The Figure Editor's **Figure Editor > Fitting > Add Fit Function** dialog
(``config/figureforge_plugins/physplot_fit_function.py``) has the same four options
(**Curve label**, **Line style**, **Line width**, **Show legend**), but it does not read
these presets; its defaults are fixed in the plugin.

.. rubric:: Using presets from Python

::

    from physplot_gui.fit_styles import list_fit_style_presets, save_fit_style_preset

    save_fit_style_preset({"line_style": ":", "line_width": 1.5}, "Thin Dotted")
    names = [preset["name"] for preset in list_fit_style_presets()]

.. rubric:: Module constants

``FIT_STYLE_SCHEMA_VERSION``
    Value written to ``schema_version`` (currently 1).

``FIT_STYLE_DIR_ENV``
    Name of the override environment variable, ``"PHYSPLOT_FIT_STYLE_DIR"``.

``DEFAULT_FIT_STYLE_DIR``
    The bundled ``config/figureforge_fit_styles`` folder, resolved at import time. The
    functions in this module do not use it; their search order comes from
    ``physplot.user_paths.plugin_search_dirs``.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

from physplot.user_paths import bundled_plugin_dir, plugin_search_dirs, writable_plugin_dir


FIT_STYLE_SCHEMA_VERSION = 1
FIT_STYLE_DIR_ENV = "PHYSPLOT_FIT_STYLE_DIR"
DEFAULT_FIT_STYLE_DIR = bundled_plugin_dir("figureforge_fit_styles")


def fit_style_directory() -> Path:
    """Return the folder new fit-style presets are written to.

    If ``PHYSPLOT_FIT_STYLE_DIR`` is set, that folder is returned (with ``~`` expanded)
    without being created; :func:`save_fit_style_preset` creates it on the first save.
    Otherwise the result is ``writable_plugin_dir("figureforge_fit_styles")``: the
    per-user ``Documents/PhysPlot/config/figureforge_fit_styles`` folder, which is
    created if possible, or the bundled ``config/figureforge_fit_styles`` folder when the
    per-user folder cannot be created or written to.

    :returns: Folder for new preset files, used by :func:`fit_style_path_from_name`.
    """
    configured = os.environ.get(FIT_STYLE_DIR_ENV)
    if configured:
        return Path(configured).expanduser()
    return writable_plugin_dir("figureforge_fit_styles")


def fit_style_directories() -> list[Path]:
    """Return every folder searched for presets, editable folder first.

    Without ``PHYSPLOT_FIT_STYLE_DIR`` this is the per-user
    ``Documents/PhysPlot/config/figureforge_fit_styles`` folder followed by the bundled
    ``config/figureforge_fit_styles`` folder (there are no legacy locations for presets).
    With the variable set, only that folder (with ``~`` expanded) is returned, so the
    bundled "Default LSQ Fit" preset is not listed. Folders are not checked for existence
    here; :func:`list_fit_style_presets` skips missing ones.

    :returns: Folders in priority order. When two folders hold a file with the same
        name, the file in the earlier folder wins.
    """
    configured = os.environ.get(FIT_STYLE_DIR_ENV)
    if configured:
        return [Path(configured).expanduser()]
    return plugin_search_dirs("figureforge_fit_styles")


def fit_style_path_from_name(name: str) -> Path:
    """Return the JSON file path that a preset called *name* is saved to.

    The name is stripped of surrounding whitespace, every run of characters other than
    ASCII letters, digits, ``_``, ``.`` and ``-`` is replaced by a single ``_``, and
    leading or trailing ``.`` and ``_`` characters are removed. An empty result becomes
    ``physplot_fit_style``. The file is placed in :func:`fit_style_directory`. For
    example, ``"Thin Dotted"`` gives ``Thin_Dotted.json``. Different names can map to the
    same file, and whether the file already exists is not checked.

    :param name: Preset display name. Non-string values are converted with ``str()``.
    :returns: ``<fit_style_directory()>/<safe name>.json``.
    """
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(name).strip()).strip("._")
    if not safe:
        safe = "physplot_fit_style"
    return fit_style_directory() / f"{safe}.json"


def list_fit_style_presets() -> list[dict]:
    """List every preset that the **Fit Style** dropdown can offer.

    Scans :func:`fit_style_directories` in priority order and reads each ``*.json`` file
    directly inside each folder (sub-folders are not searched), in file-name order.
    Missing folders are ignored. A file is skipped when a file with the same *file name*
    was already taken from an earlier folder, and it is skipped silently when it cannot
    be read or parsed as JSON. The top-level JSON value must be an object and its
    ``"name"``, if present, a string; otherwise listing fails with an exception instead
    of skipping the file.

    The main window (``MainWindow.fit_style_entries``) puts a ``{"name": "Default",
    "path": None, "style": None}`` entry in front of this list. Simple Mode stores each
    entry's ``path`` and ``style`` on its dropdown item and copies ``style`` into the
    **Fit Line** fields when the item is chosen. The list is rebuilt when the dropdown
    is created, by **Reload**, and by **File > Reload Config Modules**.

    :returns: One ``{"name": str, "path": str, "style": dict}`` dict per preset, sorted
        case-insensitively by name. ``"name"`` is the file's ``"name"`` value, or the
        file stem when that is missing or empty; ``"style"`` is the whole decoded file,
        not normalised.
    """
    presets = []
    seen = set()
    for directory in fit_style_directories():
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
            presets.append({"name": payload.get("name") or path.stem, "path": str(path), "style": payload})
    return sorted(presets, key=lambda preset: preset["name"].lower())


def save_fit_style_preset(config: dict, name: str, path: str | Path | None = None) -> Path:
    """Normalise *config* into a preset and write it as a JSON file.

    The payload comes from :func:`normalize_fit_style_payload`, so only the known fields
    are written and missing ones get their defaults. The file is UTF-8 JSON indented by
    two spaces; missing parent folders are created and an existing file is overwritten
    without warning. No GUI control calls this function at present; the saved preset
    appears in the **Fit Style** dropdown after **Reload** or **File > Reload Config
    Modules**.

    :param config: Dict with any of ``label``, ``line_style``, ``line_width``,
        ``show_legend`` and ``name``, for example the ``lsq_fit`` settings that Simple
        Mode builds for **Generate Plot**.
    :param name: Display name to store. It is also used for the file name when *path* is
        omitted. When it is empty, the stored name falls back to ``config["name"]`` or
        ``"Fit Style"``.
    :param path: Explicit output file. When ``None`` or empty, the path from
        :func:`fit_style_path_from_name` for *name* is used.
    :returns: Path of the written file.
    """
    output = Path(path) if path else fit_style_path_from_name(name)
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = normalize_fit_style_payload(config, name)
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return output


def load_fit_style_preset(path: str | Path) -> dict:
    """Read a preset JSON file and return its contents unchanged.

    Nothing is validated or normalised; pass the result to
    :func:`normalize_fit_style_payload` for that. The GUI does not call this function:
    the **Fit Style** dropdown uses the contents already read by
    :func:`list_fit_style_presets`.

    :param path: Preset file.
    :returns: The decoded JSON, normally a dict with the fields listed in the module
        docstring.
    :raises OSError: If the file cannot be read.
    :raises json.JSONDecodeError: If the file is not valid JSON.
    """
    return json.loads(Path(path).read_text(encoding="utf-8"))


def normalize_fit_style_payload(config: dict, name: str | None = None) -> dict:
    """Return a clean preset dict built from *config*.

    The result has exactly the keys ``schema_version`` (``FIT_STYLE_SCHEMA_VERSION``),
    ``name``, ``line_style``, ``line_width``, ``label`` and ``show_legend``; any other
    keys in *config* are dropped. Defaults: ``name`` is *name*, else ``config["name"]``,
    else ``"Fit Style"``; ``line_style`` is ``"--"``; ``line_width`` is ``2.0``;
    ``label`` is ``""``; ``show_legend`` is ``True``. ``show_legend`` is converted with
    ``bool()``; the other values are copied as given, without validation.

    :param config: Source dict, for example a loaded preset or Simple Mode's ``lsq_fit``
        settings.
    :param name: Optional display name that takes precedence over ``config["name"]``.
    :returns: The normalised preset dict, as written by :func:`save_fit_style_preset`.
    """
    return {
        "schema_version": FIT_STYLE_SCHEMA_VERSION,
        "name": name or config.get("name") or "Fit Style",
        "line_style": config.get("line_style", "--"),
        "line_width": config.get("line_width", 2.0),
        "label": config.get("label", ""),
        "show_legend": bool(config.get("show_legend", True)),
    }
