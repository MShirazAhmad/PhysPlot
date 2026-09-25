"""Reusable LSQ fit-style presets for Simple Mode and FigureForge workflows.

Presets are JSON files discovered from ``config/figureforge_fit_styles``. The
per-user ``Documents/PhysPlot/config/figureforge_fit_styles`` folder is
searched first and wins on name clashes; bundled presets provide defaults.
Saved presets go into the per-user folder and can be reloaded from the GUI.
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
    """Return the folder new fit-style presets are written to."""
    configured = os.environ.get(FIT_STYLE_DIR_ENV)
    if configured:
        return Path(configured).expanduser()
    return writable_plugin_dir("figureforge_fit_styles")


def fit_style_directories() -> list[Path]:
    """Return every folder searched for presets, editable folder first."""
    configured = os.environ.get(FIT_STYLE_DIR_ENV)
    if configured:
        return [Path(configured).expanduser()]
    return plugin_search_dirs("figureforge_fit_styles")


def fit_style_path_from_name(name: str) -> Path:
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(name).strip()).strip("._")
    if not safe:
        safe = "physplot_fit_style"
    return fit_style_directory() / f"{safe}.json"


def list_fit_style_presets() -> list[dict]:
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
    output = Path(path) if path else fit_style_path_from_name(name)
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = normalize_fit_style_payload(config, name)
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return output


def load_fit_style_preset(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def normalize_fit_style_payload(config: dict, name: str | None = None) -> dict:
    return {
        "schema_version": FIT_STYLE_SCHEMA_VERSION,
        "name": name or config.get("name") or "Fit Style",
        "line_style": config.get("line_style", "--"),
        "line_width": config.get("line_width", 2.0),
        "label": config.get("label", ""),
        "show_legend": bool(config.get("show_legend", True)),
    }
