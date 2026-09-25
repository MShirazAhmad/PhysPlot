"""User-editable PhysPlot folders."""

from __future__ import annotations

import os
import sys
from pathlib import Path


MODULE_ID = "physplot.user_paths"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-07-09-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"

USER_DIR_ENV = "PHYSPLOT_USER_DIR"
USER_FOLDER_NAME = "PhysPlot"

CONFIG_FOLDER_NAME = "config"
PLUGIN_CONFIG_FOLDERS = {
    "fileloader": ("data_importers", ("fileloader",)),
    "data_importers": ("data_importers", ("fileloader",)),
    "functions": ("transformations", ("functions",)),
    "transformations": ("transformations", ("functions",)),
    "curvefitting": ("fit_functions", ("curvefitting",)),
    "fit_functions": ("fit_functions", ("curvefitting",)),
    "styling": ("templates", ("styling",)),
    "templates": ("templates", ("styling",)),
    "figureforge_plugins": ("figureforge_plugins", ()),
    "figureforge_fit_styles": ("figureforge_fit_styles", ()),
    "pipelines": ("pipelines", ()),
    "sequences": ("sequences", ("workflows",)),
    "plotter_modules": ("plotter_modules", ()),
    "plot_types": ("plot_types", ()),
    "protocol_modules": ("protocol_modules", ()),
}


def project_root() -> Path:
    """Return the folder that holds the bundled ``config/`` tree.

    In a source checkout this is the repository root. In a PyInstaller build
    the bundled resources live next to the frozen package under ``_MEIPASS``.
    """
    frozen_root = getattr(sys, "_MEIPASS", None)
    if frozen_root:
        return Path(frozen_root)
    return Path(__file__).resolve().parent.parent


def config_folder_names() -> list[str]:
    """Return the canonical ``config/<name>`` folder names, in display order."""
    names = []
    for config_name, _ in PLUGIN_CONFIG_FOLDERS.values():
        if config_name not in names:
            names.append(config_name)
    return names


def user_physplot_dir() -> Path:
    """Return the editable per-user PhysPlot folder.

    On Windows this is normally ``%USERPROFILE%\\Documents\\PhysPlot``.
    ``PHYSPLOT_USER_DIR`` is mainly useful for tests and portable deployments.
    """
    configured = os.environ.get(USER_DIR_ENV)
    if configured:
        return Path(configured).expanduser()
    return _documents_dir() / USER_FOLDER_NAME


def user_plugin_dir(name: str) -> Path:
    config_name, _ = _plugin_config_entry(name)
    return user_physplot_dir() / CONFIG_FOLDER_NAME / config_name


def bundled_plugin_dir(name: str) -> Path:
    config_name, _ = _plugin_config_entry(name)
    return project_root() / CONFIG_FOLDER_NAME / config_name


def writable_plugin_dir(name: str) -> Path:
    """Return the folder new user files should be saved into.

    The per-user ``Documents/PhysPlot/config/<name>`` folder wins when it can be
    created; otherwise the bundled folder is used so source checkouts keep
    working without a Documents tree.
    """
    user_dir = user_plugin_dir(name)
    _mkdir_if_allowed(user_dir)
    if user_dir.is_dir() and os.access(user_dir, os.W_OK):
        return user_dir
    return bundled_plugin_dir(name)


def plugin_search_dirs(name: str) -> list[Path]:
    """Return editable user dir first, then bundled defaults.

    New reusable modules live under ``config/``. Legacy root-level folders are
    still searched last so older local installations keep loading.
    """
    config_name, legacy_names = _plugin_config_entry(name)
    root = user_physplot_dir()
    project = project_root()
    paths = [root / CONFIG_FOLDER_NAME / config_name, project / CONFIG_FOLDER_NAME / config_name]
    for legacy_name in legacy_names:
        paths.extend([root / legacy_name, project / legacy_name])
    return _unique_paths(paths)


def ensure_user_physplot_dirs() -> Path:
    root = user_physplot_dir()
    config_root = root / CONFIG_FOLDER_NAME
    for folder_name in PLUGIN_CONFIG_FOLDERS.values():
        _mkdir_if_allowed(config_root / folder_name[0])
    _mkdir_if_allowed(root / "test_data")
    return root


def _documents_dir() -> Path:
    if os.name == "nt":
        userprofile = os.environ.get("USERPROFILE")
        if userprofile:
            return Path(userprofile) / "Documents"
    return Path.home() / "Documents"


def _plugin_config_entry(name: str) -> tuple[str, tuple[str, ...]]:
    return PLUGIN_CONFIG_FOLDERS.get(name, (name, ()))


def _unique_paths(paths: list[Path]) -> list[Path]:
    seen = set()
    unique = []
    for path in paths:
        marker = str(path)
        if marker in seen:
            continue
        seen.add(marker)
        unique.append(path)
    return unique


def _mkdir_if_allowed(path: Path) -> None:
    try:
        path.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        pass
