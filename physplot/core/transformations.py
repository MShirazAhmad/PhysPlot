"""Built-in column transformations."""

from __future__ import annotations

import numpy as np
import pandas as pd

MODULE_ID = "physplot.core.transformations"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-05-30-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"


def normalize_max(series: pd.Series) -> pd.Series:
    maximum = series.abs().max()
    if maximum == 0 or pd.isna(maximum):
        return series.astype(float)
    return series / maximum


def multiply(series: pd.Series, factor=1) -> pd.Series:
    return series * factor


def add(series: pd.Series, value=0) -> pd.Series:
    return series + value


def subtract(series: pd.Series, value=0) -> pd.Series:
    return series - value


def divide(series: pd.Series, divisor=1) -> pd.Series:
    return series / divisor


def log(series: pd.Series) -> pd.Series:
    return np.log(series)


def log10(series: pd.Series) -> pd.Series:
    return np.log10(series)


def baseline_subtract(series: pd.Series, baseline=None) -> pd.Series:
    if baseline is None:
        baseline = series.iloc[0] if len(series) else 0
    return series - baseline


TRANSFORMS = {
    "normalize_max": normalize_max,
    "multiply": multiply,
    "add": add,
    "subtract": subtract,
    "divide": divide,
    "log": log,
    "log10": log10,
    "baseline_subtract": baseline_subtract,
}


def list_transforms() -> list[str]:
    return list(TRANSFORMS)


def get_transform(name: str):
    try:
        return TRANSFORMS[name]
    except KeyError as exc:
        raise ValueError(f"Unknown transformation '{name}'.") from exc
