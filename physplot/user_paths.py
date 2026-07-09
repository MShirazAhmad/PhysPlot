"""User-editable PhysPlot folders."""

from __future__ import annotations

import os
from pathlib import Path


USER_DIR_ENV = "PHYSPLOT_USER_DIR"
USER_FOLDER_NAME = "PhysPlot"


def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


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
    return user_physplot_dir() / name


def bundled_plugin_dir(name: str) -> Path:
    return project_root() / name


def plugin_search_dirs(name: str) -> list[Path]:
    """Return editable user dir first, then bundled defaults."""
    return [user_plugin_dir(name), bundled_plugin_dir(name)]


def ensure_user_physplot_dirs() -> Path:
    root = user_physplot_dir()
    for folder_name in ("fileloader", "functions", "curvefitting", "test_data"):
        (root / folder_name).mkdir(parents=True, exist_ok=True)
    return root


def _documents_dir() -> Path:
    if os.name == "nt":
        userprofile = os.environ.get("USERPROFILE")
        if userprofile:
            return Path(userprofile) / "Documents"
    return Path.home() / "Documents"
