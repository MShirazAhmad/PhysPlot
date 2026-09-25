"""Tolerant reader for delimited text tables exported by instruments.

Many instrument exports put metadata above the numeric table (Panalytical
XRD ``[Measurement conditions]`` blocks, EDAX EDS headers), use tabs in a
``.csv`` file, or store a spectrum as rows (PHI XPS). ``read_text_table``
keeps the plain pandas result when it already gives a usable table and
otherwise locates the numeric block itself.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Callable

import pandas as pd

MODULE_ID = "physplot.loaders.text_table"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-09-25-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"

DELIMITERS = (",", "\t", ";", None)  # None splits on any whitespace
MAX_HEADER_LINES = 200


def read_text_table(path: Path, read_plain: Callable[[Path], pd.DataFrame]) -> pd.DataFrame:
    """Read ``path`` with ``read_plain``, falling back to locating the numeric block.

    Skipped metadata lines are kept in ``DataFrame.attrs["header_lines"]``.
    """
    path = Path(path)
    raw = path.read_bytes()
    if not raw.strip():
        raise ValueError(f"'{path.name}' is empty.")
    if b"\x00" in raw[:8192]:
        raise ValueError(f"'{path.name}' is a binary file, not a text table; PhysPlot cannot read this format.")
    plain, plain_error = None, None
    try:
        plain = read_plain(path)
        if _numeric_column_count(plain) >= 2:
            return plain
    except Exception as exc:  # fall through to the tolerant reader
        plain_error = exc
    table = find_numeric_table(_decode(raw))
    if table is not None:
        return table
    if plain is not None:
        return plain
    raise ValueError(f"Could not find a numeric table in '{path.name}': {plain_error}") from plain_error


def find_numeric_table(text: str) -> pd.DataFrame | None:
    """Return the longest block of numeric rows in ``text`` as a DataFrame, or None."""
    lines = text.splitlines()
    best = None  # (rows, cols, delimiter, start, end, width)
    for delimiter in DELIMITERS:
        split = [_split(line, delimiter) for line in lines]
        for start, end, width in _numeric_blocks(split):
            rows, cols = end - start, width
            if rows <= 3 and cols >= 20:
                rows, cols = cols, rows  # a spectrum stored as rows
            if rows < 2 or cols < 2:
                continue
            # Earlier (explicit) delimiters win ties so "a b\tc" keeps "a b" together.
            if best is None or rows > best[0] or (rows == best[0] and delimiter == best[2] and cols > best[1]):
                best = (rows, cols, delimiter, start, end, width)
    if best is None:
        return None
    _, _, delimiter, start, end, width = best
    split = [_split(line, delimiter) for line in lines]
    body = split[start:end]
    transposed = len(body) <= 3 and width >= 20
    header = None
    if not transposed:
        # A header is less numeric than the data under it; it may be numeric-ish
        # itself ("X/Y, 1, 2, 3") and so sit inside the block.
        if len(body) > 2 and _numeric_count(body[0]) < min(_numeric_count(row) for row in body[1:]):
            header, body, start = body[0], body[1:], start + 1
        elif start > 0 and len(split[start - 1]) == width and (
            _numeric_count(split[start - 1]) < min(_numeric_count(row) for row in body)
        ):
            header = split[start - 1]
    frame = pd.DataFrame([row[:width] + [""] * (width - len(row)) for row in body])
    if transposed:
        frame = frame.T.reset_index(drop=True)
    frame.columns = _unique_names(header, frame.shape[1])
    for column in frame.columns:
        numeric = pd.to_numeric(frame[column], errors="coerce")
        filled = frame[column].astype(str).str.strip().ne("")
        if numeric[filled].notna().all():
            frame[column] = numeric
    header_index = start - 1 if header is not None else start
    frame.attrs["header_lines"] = [line.strip() for line in lines[:header_index] if line.strip()][:MAX_HEADER_LINES]
    return frame


def _numeric_blocks(split: list[list[str]]):
    """Yield (start, end, width) for runs of numeric rows of similar width.

    Rows may be a little ragged (e.g. fit statistics on the first row only);
    ``width`` is the widest row of the run.
    """
    start, first_width, width = None, None, None
    for index, fields in enumerate(split + [[]]):
        is_data = len(fields) >= 2 and _numeric_count(fields) >= max(2, (len(fields) + 1) // 2)
        if is_data and start is not None and abs(len(fields) - first_width) <= max(1, first_width // 2):
            width = max(width, len(fields))
            continue
        if start is not None:
            yield start, index, width
        start, first_width, width = (index, len(fields), len(fields)) if is_data else (None, None, None)


def _split(line: str, delimiter: str | None) -> list[str]:
    if delimiter is None:
        fields = line.split()
    else:  # csv handles quoted fields such as "7.74" or "Weight %"
        fields = [field.strip() for field in next(csv.reader([line], delimiter=delimiter), [])]
    while fields and fields[-1] == "":
        fields.pop()
    return fields


def _numeric_count(fields: list[str]) -> int:
    count = 0
    for field in fields:
        try:
            float(field)
        except ValueError:
            continue
        count += 1
    return count


def _numeric_column_count(frame: pd.DataFrame) -> int:
    count = 0
    for column in frame.columns:
        values = pd.to_numeric(frame[column], errors="coerce")
        if len(values) and values.notna().sum() >= max(1, 0.5 * len(values)):
            count += 1
    return count


def _unique_names(header: list[str] | None, width: int) -> list[str]:
    names, seen = [], {}
    for index in range(width):
        name = (header[index].strip().strip('"') if header and index < len(header) else "") or f"Column {index + 1}"
        if name in seen:
            seen[name] += 1
            name = f"{name}.{seen[name]}"
        else:
            seen[name] = 0
        names.append(name)
    return names


def _decode(raw: bytes) -> str:
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return raw.decode("cp1252", errors="replace")
