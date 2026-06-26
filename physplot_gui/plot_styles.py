"""Reusable figure templates shared by PhysPlot and the Figure Editor."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path


STYLE_SCHEMA_VERSION = 1
DEFAULT_STYLE_DIR = Path.cwd() / "styling"


def style_directory() -> Path:
    return Path(os.environ.get("PHYSPLOT_STYLE_DIR", DEFAULT_STYLE_DIR)).expanduser()


def style_path_from_name(name: str) -> Path:
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(name).strip()).strip("._")
    if not safe:
        safe = "physplot_style"
    return style_directory() / f"{safe}.json"


def list_style_modules() -> list[dict]:
    directory = style_directory()
    if not directory.exists():
        return []
    entries = []
    for path in sorted(directory.glob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        entries.append(
            {
                "name": payload.get("name") or path.stem,
                "path": str(path),
            }
        )
    return entries


def save_style_module(figure, name: str, path: str | Path | None = None) -> Path:
    output = Path(path) if path else style_path_from_name(name)
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = extract_style_module(figure, name)
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return output


def load_style_module(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def apply_style_module(figure, path_or_payload: str | Path | dict | None) -> None:
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
    return {
        "schema_version": STYLE_SCHEMA_VERSION,
        "name": name,
        "figure": _extract_figure_style(figure),
        "axes": [_extract_axes_style(axes) for axes in figure.get_axes()],
    }


def _extract_figure_style(figure) -> dict:
    return {
        "facecolor": _color(figure.get_facecolor()),
        "edgecolor": _color(figure.get_edgecolor()),
        "dpi": figure.get_dpi(),
        "size_inches": list(figure.get_size_inches()),
        "suptitle": figure._suptitle.get_text() if getattr(figure, "_suptitle", None) is not None else "",
    }


def _extract_axes_style(axes) -> dict:
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
    return {
        "facecolor": _first_color(collection.get_facecolors()),
        "edgecolor": _first_color(collection.get_edgecolors()),
        "linewidth": _first_value(collection.get_linewidths()),
        "alpha": collection.get_alpha(),
    }


def _apply_collection_style(collection, style: dict) -> None:
    if style.get("facecolor"):
        collection.set_facecolor(style["facecolor"])
    if style.get("edgecolor"):
        collection.set_edgecolor(style["edgecolor"])
    if style.get("linewidth") is not None:
        collection.set_linewidth(style["linewidth"])
    if "alpha" in style:
        collection.set_alpha(style["alpha"])


def _grid_style(axes) -> dict:
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
    labels = axes.get_xticklabels() if axis == "x" else axes.get_yticklabels()
    sample = labels[0] if labels else None
    return {
        "labelsize": sample.get_fontsize() if sample is not None else None,
        "labelcolor": _color(sample.get_color()) if sample is not None else None,
    }


def _apply_tick_style(axes, axis: str, style: dict) -> None:
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
    if legend is None or not legend.get_texts():
        return None
    return legend.get_texts()[0].get_fontsize()


def _color(value):
    try:
        from matplotlib.colors import to_hex

        return to_hex(value, keep_alpha=True)
    except Exception:
        return str(value)


def _first_color(values):
    try:
        if len(values) == 0:
            return None
        return _color(values[0])
    except Exception:
        return None


def _first_value(values):
    try:
        if len(values) == 0:
            return None
        return float(values[0])
    except Exception:
        return None


def _is_template_artist(artist) -> bool:
    try:
        return str(artist.get_label()).startswith("_physplot_template")
    except Exception:
        return False
