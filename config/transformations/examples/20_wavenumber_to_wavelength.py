"""Convert wavenumber in cm^-1 to wavelength in nm (wavelength = 1e7 / wavenumber).

Input: one table column of wavenumbers in cm^-1, for example the X column of an
FTIR or Raman spectrum. Output: wavelength in nm, one value per row.
Blank cells, zero and negative wavenumbers give NaN (an empty cell).
"""

import numpy as np

DISPLAY_NAME = "cm^-1 to nm"
DEFAULT_LABEL = "Wavelength (nm)"

NM_PER_CM = 1.0e7


def transform(values):
    """Return the wavelength in nm for each wavenumber in cm^-1."""
    wavenumber = np.asarray(values, dtype=float)
    positive = wavenumber > 0  # NaN compares as False, so blank cells stay NaN
    if not positive.any():
        raise ValueError(
            "cm^-1 to nm: the input column has no positive wavenumbers. "
            "Choose the column that holds wavenumbers in cm^-1."
        )
    wavelength = np.full(wavenumber.shape, np.nan)
    wavelength[positive] = NM_PER_CM / wavenumber[positive]
    return wavelength
