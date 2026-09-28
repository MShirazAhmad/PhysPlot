"""Copy the wiki's UI Reference, Sequence Walkthrough, Video Tutorials and AI-module pages into the Sphinx docs.

The GitHub wiki pages in ``wiki/`` are the source. After editing one of them, run::

    python scripts/sync_wiki_to_docs.py

This rewrites ``docs/ui/*.md`` and ``docs/extensions/ai_assistant.md`` (MyST Markdown for
Read the Docs):

- links between mirrored wiki pages become links between the docs pages;
- links to other wiki pages point at the closest docs page, or at the GitHub wiki;
- images are referenced from ``wiki/images/`` so they are not stored twice;
- a line of YouTube thumbnail links (``[![Title](https://i.ytimg.com/vi/<id>/...)](https://youtu.be/<id>)``,
  which is how the wiki shows videos) becomes embedded players (the ``youtube``
  directive in ``docs/_ext/youtube.py``).
"""

from __future__ import annotations

import os
import re
from functools import partial
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WIKI = ROOT / "wiki"
OUT = ROOT / "docs" / "ui"
WIKI_URL = "https://github.com/MShirazAhmad/PhysPlot/wiki/"

# Mirrored wiki page -> docs/ui file name (without .md), in table-of-contents order.
# A name with a folder ("../extensions/...") is written there instead.
PAGES = {
    "UI-Reference": "index",
    "UI-Main-Window": "main_window",
    "UI-Data-Table": "data_table",
    "UI-Data-Importer": "data_importer",
    "UI-Mathematical-Transformation": "transformation",
    "UI-Plotter-Module": "plotter_module",
    "UI-Build-Protocol": "build_protocol",
    "UI-Run-Sequence": "run_sequence",
    "UI-Figure-Editor": "figure_editor",
    "UI-Dialogs-and-Messages": "dialogs_and_messages",
    "Sequence-Walkthrough": "sequence_walkthrough",
    "Video-Tutorials": "videos",
    "Build-Modules-with-AI": "../extensions/ai_assistant",
    "AI-Module-Examples": "../extensions/ai_examples",
}
# Wiki pages that are not mirrored -> the docs page that covers the same ground.
OTHER_DOCS = {
    "Home": "../index.rst",
    "Getting-Started": "../getting_started.rst",
    "GUI-Walkthrough": "../getting_started.rst",
    "Instrument-Data": "../user_guide/data_import.rst",
    "Replayable-Plugin-Transformations": "../user_guide/data_manipulation.rst",
    "Bulk-Runs-and-Headless": "../user_guide/protocol_sequences.rst",
    "Extending-PhysPlot": "../extensions/index.rst",
}
# Pages listed in the UI Reference table of contents (the walkthrough and videos sit in the main
# one, the AI-module page in the Extension Guides).
UI_TOCTREE = [name for page, name in PAGES.items()
              if page not in {"UI-Reference", "Sequence-Walkthrough", "Video-Tutorials", "Build-Modules-with-AI",
                               "AI-Module-Examples"}]

LINK = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)\s]+)\)")
IMAGE = re.compile(r"!\[([^\]]*)\]\(images/([^)\s]+)\)")
VIDEO = re.compile(r"\[!\[([^\]]*)\]\(https://i\.ytimg\.com/vi/([\w-]+)/\w+\.jpg\)\]\(https://youtu\.be/[\w-]+\)")


def video_embeds(line: str) -> list[str] | None:
    """Embedded players for a line that holds only YouTube thumbnail links, else None."""
    if not line.strip() or VIDEO.sub("", line).strip():
        return None
    indent = line[: len(line) - len(line.lstrip())]
    lines = []
    for title, video in VIDEO.findall(line):
        lines += [f"{indent}```{{youtube}} {video}", f"{indent}:title: {title}", f"{indent}```", ""]
    return lines[:-1]


def output_path(page: str) -> Path:
    return (OUT / f"{PAGES[page]}.md").resolve()


def relative(target: Path, folder: Path) -> str:
    return Path(os.path.relpath(target, folder)).as_posix()


def rewrite_link(match: re.Match, folder: Path) -> str:
    """Point a wiki link at the docs page written in ``folder``'s terms."""
    text, target = match.groups()
    if target.startswith(("http://", "https://", "mailto:", "#")):
        return match.group(0)
    page, _, anchor = target.partition("#")
    if page in PAGES:
        new = relative(output_path(page), folder) + (f"#{anchor}" if anchor else "")
    elif page in OTHER_DOCS:
        new = relative((OUT / OTHER_DOCS[page]).resolve(), folder)
    else:
        new = WIKI_URL + target
    return f"[{text}]({new})"


def convert(page: str) -> str:
    source = (WIKI / f"{page}.md").read_text(encoding="utf-8")
    folder = output_path(page).parent
    images = relative(WIKI / "images", folder)
    lines = []
    in_code = False
    for line in source.splitlines():
        if line.lstrip().startswith("```"):
            in_code = not in_code
        if not in_code and (embeds := video_embeds(line)) is not None:
            lines.extend(embeds)
            continue
        if not in_code:
            line = IMAGE.sub(rf"![\1]({images}/\2)", line)
            line = LINK.sub(partial(rewrite_link, folder=folder), line)
        lines.append(line)
    text = "\n".join(lines).rstrip() + "\n"
    header = f"<!-- Generated from wiki/{page}.md by scripts/sync_wiki_to_docs.py. Edit the wiki page. -->\n\n"
    if page == "UI-Reference":
        toctree = "\n".join(["", "```{toctree}", ":maxdepth: 1", "", *UI_TOCTREE, "```", ""])
        text += toctree
    return header + text


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for page in PAGES:
        path = output_path(page)
        path.write_text(convert(page), encoding="utf-8")
        print(f"{relative(path, ROOT)}  <-  wiki/{page}.md")


if __name__ == "__main__":
    main()
