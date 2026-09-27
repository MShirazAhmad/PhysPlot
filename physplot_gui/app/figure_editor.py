"""Install the Figure Editor plugins into FigureForge and explain editors that fail to start.

The Figure Editor is FigureForge, which
:meth:`~physplot_gui.app.main_window.MainWindow._open_figureforge_editor` starts in its own
Python process. FigureForge imports every ``*.py`` file in its own ``plugins`` package
folder while the package itself is imported, before any window exists, so PhysPlot copies
its plugins into that folder each time a Figure Editor opens:

* :func:`install_plugins` copies the ``*.py`` files of the bundled
  ``config/figureforge_plugins`` folder and then of the per-user
  ``Documents/PhysPlot/config/figureforge_plugins`` folder (a per-user file replaces a
  bundled file of the same name). It lists the copied files in :data:`MANIFEST_NAME` in the
  same folder and, the next time, deletes the copies whose source file has since been
  renamed or deleted, so they stop loading. Files PhysPlot did not copy (FigureForge's own,
  or ones made with FigureForge's *New Plugin*) are never deleted.
* :func:`reserved_plugin_names` lists the module names FigureForge itself uses in that
  folder (``__init__``, ``add_legend``, the ``utils`` package, ...). A plugin file with one of
  those names would overwrite or hide part of FigureForge, so :func:`install_plugins` does
  not copy it and :func:`skipped_plugins_message` tells the user to rename it.
* :class:`EditorProcess` keeps a started editor with its temporary files: the pickled
  figure, the log that receives its standard error (a file, so a chatty plugin cannot fill a
  pipe and freeze the editor) and the file the editor creates once its window is shown.
* :func:`describe_start_failure` turns the error output of an editor that exited before its
  window opened into a short message that names the plugin file at fault.

A broken plugin stops FigureForge from starting at all: the import error ends the editor
process a second or two after it was started, with the traceback on its standard error.
"""

from __future__ import annotations

import glob
import json
import os
import re
import shutil
import time
from dataclasses import dataclass, field
from importlib.metadata import PackageNotFoundError, files as package_files
from pathlib import Path, PurePosixPath
from typing import Iterable


#: File in FigureForge's ``plugins`` folder that lists the plugin files PhysPlot copied there.
MANIFEST_NAME = ".physplot_plugins.json"

#: The modules in FigureForge 0.3's ``plugins`` folder, used in addition to the files the
#: installed FigureForge lists in its package metadata.
FIGUREFORGE_PLUGIN_MODULES = frozenset(
    {
        "__init__",
        "add_annotation",
        "add_legend",
        "add_minor_data_ticks",
        "reduce_tick_limits",
        "set_spine_bounds",
        "toggle_spines",
        "utils",
    }
)

#: Command that repairs a FigureForge whose own plugin file was overwritten.
REINSTALL_COMMAND = "python -m pip install --force-reinstall --no-deps FigureForge"

_TRACEBACK_FILE = re.compile(r'^\s*File "(?P<path>[^"]+)", line \d+', re.MULTILINE)


@dataclass
class PluginInstall:
    """What :func:`install_plugins` did.

    :ivar plugin_dir: FigureForge's ``plugins`` folder.
    :ivar installed: Copied file name -> the source file it was copied from.
    :ivar skipped: Source files not copied because their names are reserved by FigureForge.
    :ivar removed: File names of stale copies that were deleted.
    """

    plugin_dir: Path
    installed: dict[str, Path] = field(default_factory=dict)
    skipped: list[Path] = field(default_factory=list)
    removed: list[str] = field(default_factory=list)


@dataclass
class EditorProcess:
    """A Figure Editor process started by PhysPlot, with its temporary files.

    :ivar process: The editor's ``subprocess.Popen``.
    :ivar figure_path: The pickled figure the editor opens; the editor deletes it when it ends.
    :ivar log_path: The file that receives the editor's standard error.
    :ivar ready_path: The file the editor creates once its window is shown.
    :ivar install: The plugin installation made just before the editor started.
    :ivar started: ``time.monotonic()`` when the editor was started.
    :ivar watching: ``True`` while PhysPlot still checks the editor for a start-up failure.
    """

    process: object
    figure_path: Path
    log_path: Path
    ready_path: Path
    install: PluginInstall | None = None
    started: float = field(default_factory=time.monotonic)
    watching: bool = True

    def remove_files(self) -> None:
        """Delete the temporary files that still exist."""
        for path in (self.figure_path, self.log_path, self.ready_path):
            try:
                path.unlink()
            except OSError:
                pass


def reserved_plugin_names(plugin_dir: Path) -> set[str]:
    """Return the module names in FigureForge's ``plugins`` folder that belong to FigureForge.

    The names are the files of ``FigureForge/plugins`` that the installed FigureForge lists in
    its package metadata (``add_legend.py`` gives ``add_legend``, ``utils/...`` gives
    ``utils``), :data:`FIGUREFORGE_PLUGIN_MODULES`, and every sub-folder of ``plugin_dir``
    other than ``__pycache__``. FigureForge imports each plugin as
    ``FigureForge.plugins.<name>``, so a plugin file with one of these names would overwrite a
    FigureForge file or hide one of its packages.

    :param plugin_dir: FigureForge's ``plugins`` folder.
    :returns: The reserved module names, without ``.py``.
    """
    names = set(FIGUREFORGE_PLUGIN_MODULES)
    try:
        record = package_files("FigureForge") or []
    except PackageNotFoundError:
        record = []
    for entry in record:
        parts = PurePosixPath(str(entry).replace("\\", "/")).parts
        if len(parts) < 3 or parts[:2] != ("FigureForge", "plugins") or parts[2] == "__pycache__":
            continue
        if len(parts) > 3:
            names.add(parts[2])
        elif parts[2].endswith(".py"):
            names.add(parts[2][:-3])
    if plugin_dir.is_dir():
        names.update(child.name for child in plugin_dir.iterdir() if child.is_dir() and child.name != "__pycache__")
    return names


def install_plugins(source_dirs: Iterable[Path], plugin_dir: Path) -> PluginInstall:
    """Copy the Figure Editor plugins into FigureForge and delete stale copies.

    Every ``*.py`` file of ``source_dirs`` is copied into ``plugin_dir`` (created when
    missing), overwriting a file of the same name; the folders are copied in the given order,
    so a file in a later folder replaces one of the same name in an earlier folder. A file
    whose name, ignoring case, is in :func:`reserved_plugin_names` is not copied but listed in
    :attr:`PluginInstall.skipped`.

    The copied file names and their sources are written to :data:`MANIFEST_NAME` in
    ``plugin_dir``. Files listed there by the previous call but not copied this time are
    deleted first, with their cached ``__pycache__/<name>.*.pyc`` files. Files the manifest
    does not list, and reserved names, are never deleted. An unreadable manifest counts as
    empty.

    :param source_dirs: Existing plugin folders, bundled folder first.
    :param plugin_dir: FigureForge's ``plugins`` folder.
    :returns: What was copied, skipped and deleted.
    """
    plugin_dir.mkdir(parents=True, exist_ok=True)
    reserved = {name.casefold() for name in reserved_plugin_names(plugin_dir)}
    result = PluginInstall(plugin_dir)
    for source_dir in source_dirs:
        for source in sorted(source_dir.glob("*.py")):
            if source.stem.casefold() in reserved:
                result.skipped.append(source)
            else:
                result.installed[source.name] = source
    # Delete before copying: on a case-insensitive disk a stale "Plot.py" is the same file
    # as a new "plot.py".
    for name in sorted(_read_manifest(plugin_dir) - set(result.installed)):
        if Path(name).stem.casefold() not in reserved and _remove_copy(plugin_dir, name):
            result.removed.append(name)
    for name, source in result.installed.items():
        shutil.copy2(source, plugin_dir / name)
    _write_manifest(plugin_dir, result.installed)
    return result


def skipped_plugins_message(skipped: Iterable[Path]) -> str:
    """Explain why plugin files were not copied into the Figure Editor.

    :param skipped: The source files in :attr:`PluginInstall.skipped`.
    :returns: A message that names each file and asks the user to rename it.
    """
    skipped = list(skipped)
    listed = "\n".join(f"  {path.name}  (in {path.parent})" for path in skipped)
    return (
        "These Figure Editor plugins were not loaded, because the Figure Editor uses the same "
        f"file names for its own files and copying them would break it:\n\n{listed}\n\n"
        f"Rename each file, for example to my_{skipped[0].stem.strip('_')}.py, and generate the plot again."
    )


def read_log(path: Path, limit: int = 64_000) -> str:
    """Return the end of an editor's error-output log.

    :param path: The log file; a missing file gives ``""``.
    :param limit: Largest number of bytes read, from the end of the file.
    :returns: The text, decoded as UTF-8 with undecodable bytes replaced.
    """
    try:
        with open(path, "rb") as handle:
            handle.seek(0, os.SEEK_END)
            size = handle.tell()
            handle.seek(max(0, size - limit))
            data = handle.read()
    except OSError:
        return ""
    text = data.decode("utf-8", errors="replace")
    return f"...\n{text}" if size > limit else text


def describe_start_failure(output: str, returncode: int, install: PluginInstall | None) -> str:
    """Summarise why a Figure Editor process exited before its window opened.

    The last non-empty line of ``output`` (normally the exception) is quoted. When the
    traceback's innermost frame in FigureForge's ``plugins`` folder is a plugin PhysPlot
    copied, the message names its source file and says to fix or remove it; for a file
    PhysPlot did not copy it says to delete that file, and for one of FigureForge's own
    files it gives :data:`REINSTALL_COMMAND`.

    :param output: The editor's error output (see :func:`read_log`).
    :param returncode: The editor's exit code.
    :param install: The plugin installation made before the editor started, if known.
    :returns: The message for the "Figure Editor failed" dialog.
    """
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    error = lines[-1] if lines else f"Figure Editor exited with code {returncode}."
    culprit = _failing_plugin(output, install.plugin_dir) if install else None
    if culprit is None:
        return f"The Figure Editor closed before its window opened:\n\n{error}"
    source = install.installed.get(culprit.name)
    if source is not None:
        return (
            f"The Figure Editor plugin {source.name} stopped the Figure Editor from opening:\n\n"
            f"{error}\n\nFix or remove {source}, then generate the plot again."
        )
    if culprit.stem.casefold() in {name.casefold() for name in reserved_plugin_names(install.plugin_dir)}:
        return (
            f"The Figure Editor's own file {culprit.name} is damaged:\n\n{error}\n\n"
            f"Reinstall the Figure Editor in PhysPlot's Python: {REINSTALL_COMMAND}"
        )
    return (
        f"{culprit.name} in the Figure Editor's plugins folder stopped the Figure Editor from "
        f"opening:\n\n{error}\n\nPhysPlot did not copy this file there (an older PhysPlot or the "
        f"Figure Editor's New Plugin command did). Delete {culprit}, then generate the plot again."
    )


def _failing_plugin(output: str, plugin_dir: Path) -> Path | None:
    """Return the innermost traceback file directly inside ``plugin_dir``, other than
    FigureForge's ``__init__.py`` (which imports every plugin), or ``None``."""
    folder = os.path.normcase(os.path.realpath(plugin_dir))
    for match in reversed(list(_TRACEBACK_FILE.finditer(output))):
        path = Path(match.group("path"))
        if path.name != "__init__.py" and os.path.normcase(os.path.realpath(path.parent)) == folder:
            return plugin_dir / path.name
    return None


def _read_manifest(plugin_dir: Path) -> set[str]:
    """Return the plain ``*.py`` file names :data:`MANIFEST_NAME` lists (empty if unreadable)."""
    try:
        installed = json.loads((plugin_dir / MANIFEST_NAME).read_text(encoding="utf-8")).get("installed", {})
    except (OSError, ValueError, AttributeError):
        return set()
    return {name for name in installed if isinstance(name, str) and name.endswith(".py") and name == Path(name).name}


def _write_manifest(plugin_dir: Path, installed: dict[str, Path]) -> None:
    """Write :data:`MANIFEST_NAME` listing ``installed`` (file name -> source file)."""
    manifest = {
        "comment": "Written by PhysPlot: the plugin files it copied here. "
        "PhysPlot deletes a copy when its source file is gone.",
        "installed": {name: str(source) for name, source in sorted(installed.items())},
    }
    (plugin_dir / MANIFEST_NAME).write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def _remove_copy(plugin_dir: Path, name: str) -> bool:
    """Delete ``plugin_dir / name`` and its cached ``.pyc`` files; ``True`` if the file was deleted."""
    try:
        (plugin_dir / name).unlink()
    except OSError:
        return False
    for cached in (plugin_dir / "__pycache__").glob(f"{glob.escape(Path(name).stem)}.*.pyc"):
        try:
            cached.unlink()
        except OSError:
            pass
    return True
