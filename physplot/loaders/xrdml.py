"""Loader for Malvern Panalytical ``.xrdml`` XRD measurement files.

``Intensity`` is the raw counts summed over the file's scans, which is what
the vendor's CSV export writes for repeated ("reps") scans; with more than
one scan, ``Intensity 1`` ... ``Intensity N`` hold each scan. Attenuation
factors are recorded in metadata but not applied, also matching that export.
The scanned axis (normally ``2Theta``) becomes the first column.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import pandas as pd

MODULE_ID = "physplot.loaders.xrdml"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-09-25-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"


def read_xrdml(path: Path) -> tuple[pd.DataFrame, dict]:
    """Return the scan table and measurement metadata of an ``.xrdml`` file."""
    path = Path(path)
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        raise ValueError(f"'{path.name}' is not a readable XRDML file: {exc}") from exc
    scans = [element for element in root.iter() if _tag(element) == "scan"]
    if not scans:
        raise ValueError(f"'{path.name}' contains no XRD scans.")
    axis, positions, counts, factors = None, None, [], []
    for index, scan in enumerate(scans, start=1):
        data_points = _child(scan, "dataPoints")
        values = _child(data_points, "intensities") if data_points is not None else None
        if values is None and data_points is not None:
            values = _child(data_points, "counts")
        if values is None or not (values.text or "").split():
            raise ValueError(f"Scan {index} in '{path.name}' has no intensities.")
        scan_counts = np.array(values.text.split(), dtype=float)
        scan_axis, scan_positions = _scanned_axis(data_points, scan.get("scanAxis"), scan_counts.size)
        if axis is None:
            axis, positions = scan_axis, scan_positions
        elif scan_axis != axis or scan_positions.shape != positions.shape or not np.allclose(scan_positions, positions):
            raise ValueError(f"Scan {index} in '{path.name}' does not share the {axis} range of scan 1.")
        counts.append(scan_counts)
        factor = _child(data_points, "commonBeamAttenuationFactor")
        factors.append(float(factor.text) if factor is not None and factor.text else 1.0)

    table = {axis: positions, "Intensity": np.sum(counts, axis=0)}
    if len(counts) > 1:
        table.update({f"Intensity {index}": scan_counts for index, scan_counts in enumerate(counts, start=1)})
    frame = pd.DataFrame(table)
    return frame, _metadata(root, scans, axis, positions, factors)


def _scanned_axis(data_points, scan_axis: str | None, count: int) -> tuple[str, np.ndarray]:
    """Pick the axis that moves during the scan: 2Theta when it does, else the first that does."""
    moving = {}
    for positions in (element for element in data_points if _tag(element) == "positions"):
        values = _position_values(positions, count)
        if values is not None and values.size and np.ptp(values) > 0:
            moving[positions.get("axis") or f"Axis {len(moving) + 1}"] = values
    if not moving:
        raise ValueError(f"No moving axis found for scan axis '{scan_axis}'.")
    axis = "2Theta" if "2Theta" in moving else next(iter(moving))
    return axis, moving[axis]


def _position_values(positions, count: int) -> np.ndarray | None:
    listed = _child(positions, "listPositions")
    if listed is not None and listed.text:
        return np.array(listed.text.split(), dtype=float)
    start, end = _child(positions, "startPosition"), _child(positions, "endPosition")
    if start is not None and end is not None:
        return np.linspace(float(start.text), float(end.text), count)
    return None


def _metadata(root, scans, axis: str, positions: np.ndarray, factors: list[float]) -> dict:
    measurement = next((element for element in root.iter() if _tag(element) == "xrdMeasurement"), root)
    wavelength = _child(measurement, "usedWavelength")
    tube = next((element for element in root.iter() if _tag(element) == "xRayTube"), None)
    counting_time = next((element for element in scans[0].iter() if _tag(element) == "commonCountingTime"), None)
    namespace = root.tag[1:].split("}")[0] if root.tag.startswith("{") else ""
    metadata = {
        "schema": namespace.rsplit("/", 1)[-1] if namespace else None,
        "sample_name": _text(root, "name", within="sample"),
        "sample_id": _text(root, "id", within="sample"),
        "measurement_type": measurement.get("measurementType"),
        "scan_axis": scans[0].get("scanAxis"),
        "scan_mode": scans[0].get("mode"),
        "scans": len(scans),
        "axis": axis,
        "start": float(positions[0]),
        "end": float(positions[-1]),
        "step": float(np.mean(np.diff(positions))) if positions.size > 1 else None,
        "points": int(positions.size),
        "counting_time_s": float(counting_time.text) if counting_time is not None and counting_time.text else None,
        "beam_attenuation_factors": factors,
        "anode": _text(tube, "anodeMaterial") if tube is not None else None,
        "tube_kV": _number(_text(tube, "tension")) if tube is not None else None,
        "tube_mA": _number(_text(tube, "current")) if tube is not None else None,
        "start_time": _text(scans[0], "startTimeStamp"),
    }
    if wavelength is not None:
        metadata["wavelength_intended"] = wavelength.get("intended")
        for name in ("kAlpha1", "kAlpha2", "kBeta", "ratioKAlpha2KAlpha1"):
            element = _child(wavelength, name)
            if element is not None and element.text:
                metadata[f"wavelength_{name}"] = float(element.text)
    return {key: value for key, value in metadata.items() if value is not None}


def _number(text: str | None) -> float | None:
    try:
        return float(text) if text is not None else None
    except ValueError:
        return None


def _tag(element) -> str:
    return element.tag.rsplit("}", 1)[-1] if isinstance(element.tag, str) else ""


def _child(element, name: str):
    if element is None:
        return None
    return next((child for child in element if _tag(child) == name), None)


def _text(element, name: str, within: str | None = None) -> str | None:
    if within is not None:
        element = next((child for child in element.iter() if _tag(child) == within), None)
        if element is None:
            return None
    found = next((child for child in element.iter() if _tag(child) == name), None)
    return found.text.strip() if found is not None and found.text and found.text.strip() else None
