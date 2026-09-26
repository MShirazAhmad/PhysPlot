"""Copy the wiki's UI Reference, Sequence Walkthrough and Video Tutorials pages into the Sphinx docs.

The GitHub wiki pages in ``wiki/`` are the source. After editing one of them, run::

    python scripts/sync_wiki_to_docs.py

This rewrites ``docs/ui/*.md`` (MyST Markdown for Read the Docs):

- links between mirrored wiki pages become links between the docs pages;
- links to other wiki pages point at the closest docs page, or at the GitHub wiki;
- images are referenced from ``wiki/images/`` so they are not stored twice.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WIKI = ROOT / "wiki"
OUT = ROOT / "docs" / "ui"
WIKI_URL = "https://github.com/MShirazAhmad/PhysPlot/wiki/"

# Mirrored wiki page -> docs/ui file name (without .md), in table-of-contents order.
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
# Pages listed in the UI Reference table of contents (the walkthrough and videos sit in the main one).
UI_TOCTREE = [name for page, name in PAGES.items()
              if page not in {"UI-Reference", "Sequence-Walkthrough", "Video-Tutorials"}]

LINK = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)\s]+)\)")
IMAGE = re.compile(r"!\[([^\]]*)\]\(images/([^)\s]+)\)")


def rewrite_link(match: re.Match) -> str:
    text, target = match.groups()
    if target.startswith(("http://", "https://", "mailto:", "#")):
        return match.group(0)
    page, _, anchor = target.partition("#")
    if page in PAGES:
        new = f"{PAGES[page]}.md" + (f"#{anchor}" if anchor else "")
    elif page in OTHER_DOCS:
        new = OTHER_DOCS[page]
    else:
        new = WIKI_URL + target
    return f"[{text}]({new})"


def convert(page: str) -> str:
    source = (WIKI / f"{page}.md").read_text(encoding="utf-8")
    lines = []
    in_code = False
    for line in source.splitlines():
        if line.lstrip().startswith("```"):
            in_code = not in_code
        if not in_code:
            line = IMAGE.sub(r"![\1](../../wiki/images/\2)", line)
            line = LINK.sub(rewrite_link, line)
        lines.append(line)
    text = "\n".join(lines).rstrip() + "\n"
    header = f"<!-- Generated from wiki/{page}.md by scripts/sync_wiki_to_docs.py. Edit the wiki page. -->\n\n"
    if page == "UI-Reference":
        toctree = "\n".join(["", "```{toctree}", ":maxdepth: 1", "", *UI_TOCTREE, "```", ""])
        text += toctree
    return header + text


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for page, name in PAGES.items():
        (OUT / f"{name}.md").write_text(convert(page), encoding="utf-8")
        print(f"docs/ui/{name}.md  <-  wiki/{page}.md")


if __name__ == "__main__":
    main()
