"""XRD baseline-removal transform for PhysPlot.

Input data structure:
    ``values`` is a one-dimensional NumPy-compatible sequence containing XRD
    intensity values from a selected table column.

Return type:
    Returns a NumPy array containing ``values - estimated_baseline``. Small
    negative values are preserved so noise is not artificially clipped.

Optional main/runtime behavior:
    This file is loaded by the Functions menu and is not intended to be run
    directly. SciPy is used for asymmetric least-squares baseline estimation
    when available; otherwise a moving quantile fallback is used.
"""

import numpy as np


DISPLAY_NAME = "XRD: Baseline Remove"
DEFAULT_LABEL = "XRD baseline removed"


def _moving_quantile_baseline(values, window_size):
    """_moving_quantile_baseline(values, window_size) -> numpy.ndarray

    Estimate a fallback baseline using a moving lower quantile.

    Parameters:
        values (numpy.ndarray): One-dimensional numeric intensity array.
        window_size (int): Odd-size window used around each point.

    Returns:
        numpy.ndarray: Estimated baseline with the same shape as ``values``.
    """
    pad = window_size // 2
    padded = np.pad(values, pad, mode="edge")
    baseline = np.empty_like(values, dtype=float)
    for index in range(values.size):
        baseline[index] = np.quantile(padded[index:index + window_size], 0.1)
    return baseline


def transform(values):
    """transform(values) -> numpy.ndarray

    Subtract a smooth estimated background from XRD intensity values.

    Parameters:
        values (Sequence[float]): One-dimensional XRD intensity column.

    Returns:
        numpy.ndarray: Baseline-corrected intensity values.
    """
    values = np.asarray(values, dtype=float)
    if values.size < 3:
        return values - np.nanmin(values)

    finite_mask = np.isfinite(values)
    if not finite_mask.any():
        return np.zeros_like(values, dtype=float)
    if not finite_mask.all():
        cleaned = values.copy()
        x = np.arange(values.size)
        cleaned[~finite_mask] = np.interp(x[~finite_mask], x[finite_mask], values[finite_mask])
        values = cleaned

    try:
        from scipy import sparse
        from scipy.sparse.linalg import spsolve

        smoothness = 1e7
        asymmetry = 0.001
        iterations = 20
        length = values.size
        difference = sparse.diags(
            [1.0, -2.0, 1.0],
            [0, 1, 2],
            shape=(length - 2, length),
            format="csc",
        )
        weights = np.ones(length)

        for _ in range(iterations):
            weight_matrix = sparse.spdiags(weights, 0, length, length, format="csc")
            system = weight_matrix + smoothness * difference.T @ difference
            baseline = spsolve(system, weights * values)
            weights = asymmetry * (values > baseline) + (1 - asymmetry) * (values <= baseline)
    except Exception:
        window_size = max(5, min(values.size // 10 * 2 + 1, 101))
        baseline = _moving_quantile_baseline(values, window_size)

    return values - baseline
