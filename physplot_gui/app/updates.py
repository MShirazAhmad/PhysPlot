"""Check GitHub for PhysPlot updates and install them with the one-command installer.

PhysPlot follows one of three branches, its *update channel*:

* ``main``: **Stable**, tested releases (recommended);
* ``indevelopment``: **Development**, the next release, updated often;
* ``bleedingedge``: **Bleeding edge**, the newest features first, may break.

The installers (``scripts/install_macos.sh`` and ``scripts/install_windows.ps1``) write
``install.json`` next to PhysPlot's Python environment, naming the branch (``ref``) and
commit they installed. :func:`check_for_update` compares that commit with the newest one
on the channel's branch on GitHub; :func:`launch_installer` re-runs the installer for the
channel in its own Terminal / PowerShell window, which reopens PhysPlot when it is done.

A source checkout (no ``install.json``) is compared by its ``git`` commit; it is updated
with ``git pull``, not by the installer.
"""

from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys
import tempfile
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path

REPO = "MShirazAhmad/PhysPlot"

#: Update channels in menu order: (branch, menu label, description).
CHANNELS = [
    ("main", "Stable", "Tested releases (recommended)."),
    ("indevelopment", "Development", "The next release; updated often."),
    ("bleedingedge", "Bleeding edge", "Newest features first; may break."),
]
CHANNEL_LABELS = {ref: label for ref, label, _ in CHANNELS}
DEFAULT_CHANNEL = "main"
#: How often the automatic check runs, in seconds (once a day).
CHECK_INTERVAL = 24 * 60 * 60


@dataclass
class UpdateInfo:
    """Result of :func:`check_for_update`."""

    channel: str
    installed_commit: str | None
    latest_commit: str
    latest_date: str
    latest_message: str
    installed_by_installer: bool

    @property
    def available(self) -> bool:
        """True when GitHub has a different (newer) commit than the installed one."""
        return bool(self.latest_commit) and (
            not self.installed_commit or not self.latest_commit.startswith(self.installed_commit[:7])
        )


def install_dir() -> Path:
    """Folder the installer created (it holds ``venv`` and ``install.json``)."""
    return Path(sys.prefix).resolve().parent


def install_record() -> dict | None:
    """Return the installer's ``install.json`` (``ref``, ``commit``, ``installed_at``) or ``None``."""
    path = install_dir() / "install.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def source_checkout_commit() -> str | None:
    """Return the ``git`` commit of a source checkout PhysPlot runs from, or ``None``."""
    root = Path(__file__).resolve().parents[2]
    if not (root / ".git").exists():
        return None
    try:
        return subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True, timeout=5, check=True
        ).stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def installed_channel() -> str:
    """The branch PhysPlot was installed from (``main`` when unknown)."""
    record = install_record() or {}
    ref = record.get("ref")
    return ref if ref in CHANNEL_LABELS else DEFAULT_CHANNEL


def latest_commit(channel: str, timeout: float = 10.0) -> dict:
    """Return ``{"sha", "date", "message"}`` of the newest commit on ``channel`` (GitHub API)."""
    request = urllib.request.Request(
        f"https://api.github.com/repos/{REPO}/commits/{channel}",
        headers={"Accept": "application/vnd.github+json", "User-Agent": "PhysPlot-update-check"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = json.load(response)
    commit = payload.get("commit", {})
    return {
        "sha": payload.get("sha", ""),
        "date": commit.get("committer", {}).get("date", ""),
        "message": commit.get("message", "").strip(),
    }


def check_for_update(channel: str | None = None, fetch=latest_commit) -> UpdateInfo:
    """Compare the installed commit with the newest commit on ``channel``.

    :param channel: Branch to follow; defaults to the one PhysPlot was installed from.
    :param fetch: Function returning the newest commit (replaced in tests).
    :raises OSError: When GitHub cannot be reached.
    """
    record = install_record()
    if record and record.get("local_source"):
        record = None  # installed from a local checkout: compare and update it with git
    channel = channel or installed_channel()
    installed = (record or {}).get("commit") or source_checkout_commit()
    if record and record.get("ref") != channel:
        installed = None  # switching channel: always offer the other branch
    latest = fetch(channel)
    return UpdateInfo(
        channel=channel,
        installed_commit=installed,
        latest_commit=latest["sha"],
        latest_date=latest["date"],
        latest_message=latest["message"],
        installed_by_installer=record is not None,
    )


def check_due(last_check: float | None, now: float | None = None) -> bool:
    """True when the automatic check has not run in the last :data:`CHECK_INTERVAL`."""
    now = time.time() if now is None else now
    return not last_check or now - float(last_check) >= CHECK_INTERVAL


def installer_command(channel: str, platform: str | None = None) -> list[str]:
    """Return the command that re-runs the installer for ``channel`` in its own window.

    The installer downloads the branch, updates the Python environment and reopens
    PhysPlot (``PHYSPLOT_RELAUNCH=1``) when it is done.
    """
    platform = platform or sys.platform
    raw = f"https://raw.githubusercontent.com/{REPO}/{channel}/scripts"
    if platform == "win32":
        script = (
            f"$env:PHYSPLOT_REF='{channel}'; $env:PHYSPLOT_RELAUNCH='1'; "
            f"irm {raw}/install_windows.ps1 | iex"
        )
        return ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-NoExit", "-Command", script]
    command = (
        f"export PHYSPLOT_REF={shlex.quote(channel)} PHYSPLOT_RELAUNCH=1; "
        f"curl -fsSL {raw}/install_macos.sh | bash"
    )
    return ["bash", "-c", command]


def launch_installer(channel: str) -> None:
    """Start the installer for ``channel`` in a new Terminal / PowerShell window.

    The caller quits PhysPlot straight after, so its files can be replaced.
    """
    command = installer_command(channel)
    if sys.platform == "win32":
        subprocess.Popen(command, creationflags=getattr(subprocess, "CREATE_NEW_CONSOLE", 0))
    elif sys.platform == "darwin":
        # A .command file opens in Terminal without extra permissions and shows progress.
        script = Path(tempfile.gettempdir()) / "physplot_update.command"
        script.write_text("#!/bin/bash\nsleep 2\n" + command[-1] + "\n", encoding="utf-8")
        os.chmod(script, 0o755)
        subprocess.Popen(["open", str(script)])
    else:
        subprocess.Popen(command, start_new_session=True)
