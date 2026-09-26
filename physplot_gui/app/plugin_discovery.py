"""Discovery helpers for editable GUI plugin folders.

PhysPlot can be extended without touching its code by dropping small Python files into the
editable ``config/`` folders of the per-user PhysPlot directory (normally
``Documents/PhysPlot/config/``; *File > Open Config Folder* opens it). This module finds
those files for the GUI:

* :func:`discover_functions`: transformation plugins in ``config/transformations/``, shown
  in the function list of the **Transformation** panel.
* :func:`discover_fileloaders`: file-loader plugins in ``config/data_importers/``, shown in
  the loader list of the **Data Importer** panel.
* :func:`discover_loader_plotters`: the plotters a loader plugin allows, added to the
  **Plotter Module** list while data loaded with that plugin is active.

Folders are searched in the order given by :func:`physplot.user_paths.plugin_search_dirs`:
the per-user ``config/<folder>`` first, then the bundled ``config/<folder>`` of the
installation, then the legacy root-level folders (``fileloader/``, ``functions/``). When
the same file name appears in more than one folder, only the first one found is used, so a
user file overrides a bundled file of the same name. The main window runs discovery when
it builds its lists and again on *File > Reload Config Modules* (``Ctrl+Shift+R``).
"""

from __future__ import annotations

import ast
import importlib.util
import sys
from pathlib import Path

from physplot.core.transformations import discover_plugin_transforms
from physplot.user_paths import plugin_search_dirs


def discover_functions() -> list[dict]:
    """Find simple transform plugins in ``config/transformations/``.

    Discovery lives in the backend so recorded sequences resolve plugins the
    same way headlessly. Entries carry ``name`` (the file stem recorded in the
    sequence), ``display_name``, ``path`` and ``module``.

    This simply returns :func:`physplot.core.transformations.discover_plugin_transforms`.
    A plugin must define a callable ``transform(values)``; its optional ``DISPLAY_NAME``
    becomes the ``display_name`` shown in the GUI (otherwise the file stem with
    underscores replaced by spaces, in title case). Plugins that fail to import, lack
    ``transform`` or use the name of a built-in transformation are skipped with a message
    on standard error. The main window adds these entries after the built-in functions in
    the **Transformation** panel.

    :returns: One dict per usable plugin, sorted by file stem.
    """
    return discover_plugin_transforms()


def discover_fileloaders() -> list[dict]:
    """Find personal file-loader plugins in ``config/data_importers/``.

    A loader plugin must expose ``load_data(file_path)``. Optional
    ``COLUMN_NAMES`` and ``DEFAULT_COLUMN_ROLES`` are picked up later by the GUI.

    The legacy ``fileloader/`` folders are searched too (see the module documentation for
    the order). Each candidate file is imported as module ``physplot_user_loader_<stem>``.
    A file that fails to import with ``ImportError``, ``OSError``, ``SyntaxError`` or
    ``ValueError`` is reported on standard error and skipped, as is a module without a
    ``load_data`` attribute. The name shown in the loader list is the module's ``title``
    attribute, or else a module-level ``title = "..."`` string found in the source, or else
    the file stem with underscores replaced by spaces, in title case.

    A file called ``default_loader.py`` is listed first; the rest follow in alphabetical
    order of their file stems.

    :returns: One dict per loader with the keys ``display_name``, ``path`` (the plugin
        file) and ``module`` (the imported module).
    """
    entries = []
    for path in _plugin_files(plugin_search_dirs("data_importers")):
        module = _load_module(path, f"physplot_user_loader_{path.stem}")
        if module is None:
            continue
        if not hasattr(module, "load_data"):
            continue
        display_name = getattr(module, "title", None) or _loader_title_from_source(path)
        entries.append({"display_name": display_name or path.stem.replace("_", " ").title(), "path": path, "module": module})
    return entries


def discover_loader_plotters(module) -> list[dict]:
    """Return plotters explicitly allowed by a file-loader plugin.

    Loader modules can define ``PLOTTER_MODULES``/``ALLOWED_PLOTTERS`` as a list
    of backend plotter ids, callables, or dictionaries such as:

    ``{"plotter_id": "paper", "name": "Publication Plot", "function": plot}``

    The attributes ``PLOTTER_MODULES``, ``ALLOWED_PLOTTER_MODULES``, ``ALLOWED_PLOTTERS``
    and ``PLOTTERS`` are checked in that order and the first non-empty one is used. It may
    also be a function, which is called without arguments to get the list. Each item is
    converted by :func:`_normalize_plotter_entry`; items of an unsupported type, and
    dictionaries without an id, are dropped.

    The main window calls this for the loader plugin that loaded the current data and adds
    the results to the **Plotter Module** list under the category ``Loader``: an entry
    naming a backend plotter uses that plotter's id (and is not added again if the plotter
    is already listed), and an entry with its own function is listed as
    ``loader:<plotter_id>`` and called directly to draw the plot.

    :param module: An imported loader plugin module, as found by
        :func:`discover_fileloaders`.
    :returns: A list of normalized plotter entries (possibly empty).
    """
    raw_entries = (
        getattr(module, "PLOTTER_MODULES", None)
        or getattr(module, "ALLOWED_PLOTTER_MODULES", None)
        or getattr(module, "ALLOWED_PLOTTERS", None)
        or getattr(module, "PLOTTERS", None)
        or []
    )
    if callable(raw_entries):
        raw_entries = raw_entries()
    entries = []
    for raw_entry in raw_entries:
        entry = _normalize_plotter_entry(module, raw_entry)
        if entry is not None:
            entries.append(entry)
    return entries


def _plugin_files(folders: list[Path]) -> list[Path]:
    """Return the plugin source files found in ``folders``, one per file name.

    Missing folders are skipped. In each folder every ``*.py`` file is considered, except
    hidden files (names starting with ``.``), ``__init__.py`` and files that do not look
    like text (see :func:`_looks_like_python_source`). The first file found for each file
    name wins, so earlier folders override later ones.

    :param folders: Folders to search, highest priority first.
    :returns: The files, with ``default_loader.py`` first and the rest sorted by stem.
    """
    paths_by_name = {}
    for folder in folders:
        if not folder.exists():
            continue
        for path in sorted(folder.glob("*.py")):
            if path.name.startswith(".") or path.name == "__init__.py" or not _looks_like_python_source(path):
                continue
            paths_by_name.setdefault(path.name, path)
    return sorted(paths_by_name.values(), key=lambda path: (path.stem != "default_loader", path.stem))


def _load_module(path: Path, module_name: str):
    """Import a plugin file as a fresh module under ``module_name``.

    The module is executed but not added to ``sys.modules``. If running it raises
    ``ImportError``, ``OSError``, ``SyntaxError`` or ``ValueError``, a ``Skipping plugin``
    message is printed to standard error and ``None`` is returned; other exceptions
    propagate.

    :param path: The plugin file.
    :param module_name: Name to give the module.
    :returns: The imported module, or ``None`` if it failed to load as described above.
    :raises ImportError: If no import spec can be created for ``path``.
    """
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load plugin from {path}")
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except (ImportError, OSError, SyntaxError, ValueError) as exc:
        print(f"Skipping plugin {path}: {exc}", file=sys.stderr)
        return None
    return module


def _looks_like_python_source(path: Path) -> bool:
    """Return whether a file looks like text rather than binary data.

    Only the first 4096 bytes are read; the file counts as source when they contain no
    NUL byte. Unreadable files count as not source.

    :param path: File to check.
    :returns: ``True`` for a readable file without NUL bytes at its start.
    """
    try:
        sample = path.read_bytes()[:4096]
    except OSError:
        return False
    return b"\x00" not in sample


def _normalize_plotter_entry(module, raw_entry) -> dict | None:
    """Normalize loader-declared plotter forms into one GUI-friendly shape.

    Accepted forms:

    * **A string** is a backend plotter id. Result: ``plotter_id`` and
      ``backend_plotter_id`` set to it, ``name`` the id with underscores replaced by spaces
      in title case, and an empty ``plot_types`` list.
    * **A callable** is a custom plot function. Result: ``plotter_id`` is its
      ``__name__`` (``custom_plotter`` if it has none), ``name`` that id in title case,
      ``callable`` the function, and ``plot_types`` ``["publication_ready"]``.
    * **A dictionary.** The id comes from ``plotter_id``, ``id`` or ``name`` (the entry is
      dropped if none is set). The function comes from ``function``, ``callable`` or
      ``plot``; a string there is looked up as an attribute of ``module``. The result has
      ``plotter_id``, ``name`` (the given name or the id in title case), ``plot_types``
      (from ``plot_types`` or ``protocols``, default ``["publication_ready"]``) and
      ``config`` (a copy of ``config``, default empty). If a callable function was found
      it is stored as ``callable``; otherwise ``backend_plotter_id`` is set to the given
      ``backend_plotter_id`` or the id.

    Anything else is dropped.

    :param module: The loader plugin module, used to resolve function names.
    :param raw_entry: One item of the plugin's plotter list.
    :returns: The normalized entry, or ``None`` if it is dropped.
    """
    if isinstance(raw_entry, str):
        return {
            "plotter_id": raw_entry,
            "name": raw_entry.replace("_", " ").title(),
            "backend_plotter_id": raw_entry,
            "plot_types": [],
        }
    if callable(raw_entry):
        plotter_id = getattr(raw_entry, "__name__", "custom_plotter")
        return {
            "plotter_id": plotter_id,
            "name": plotter_id.replace("_", " ").title(),
            "callable": raw_entry,
            "plot_types": ["publication_ready"],
        }
    if not isinstance(raw_entry, dict):
        return None
    plotter_id = raw_entry.get("plotter_id") or raw_entry.get("id") or raw_entry.get("name")
    if not plotter_id:
        return None
    function = raw_entry.get("function") or raw_entry.get("callable") or raw_entry.get("plot")
    if isinstance(function, str):
        function = getattr(module, function, None)
    entry = {
        "plotter_id": str(plotter_id),
        "name": raw_entry.get("name") or str(plotter_id).replace("_", " ").title(),
        "plot_types": list(raw_entry.get("plot_types") or raw_entry.get("protocols") or ["publication_ready"]),
        "config": dict(raw_entry.get("config") or {}),
    }
    if callable(function):
        entry["callable"] = function
    else:
        entry["backend_plotter_id"] = raw_entry.get("backend_plotter_id") or str(plotter_id)
    return entry


def _loader_title_from_source(path: Path) -> str | None:
    """Read a loader's display title from its source without running it.

    The file is parsed and the first top-level assignment ``title = "<text>"`` with a
    plain string value is used.

    :param path: The loader plugin file.
    :returns: The title string, or ``None`` if there is none or the file cannot be parsed.
    """
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return None
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == "title" for target in node.targets):
            continue
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            return node.value.value
    return None
