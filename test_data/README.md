# PhysPlot sample data

Example files for trying PhysPlot and for the test suite. The Windows installer
copies this folder to `Documents\PhysPlot\test_data`. Files in the instrument
folders (`XRD/`, `EDS/`, `XPS/`, `OES/`, `Thermal/`, `FTIR/`) keep the exact layout of real instrument
exports, but their values are simulated and their metadata (operators, paths,
projects, dates) is replaced with placeholders.

| File | Instrument / format | Load with | What you get |
| --- | --- | --- | --- |
| `sample_linear.csv` | Plain CSV | Auto Loader | `Time`, `Voltage`, `Error`, `Group` |
| `sine_wave.csv` | Plain CSV | Auto Loader | `x`, `sin(x)`, `sin_error` |
| `sample_nanoindentation.csv` | Nanoindentation | Nanoindentation Loader | Load–displacement columns |
| `batch/` | Plain CSV (2 files) | Run Sequence bulk run | Same columns as `sample_linear.csv` |
| `XRD.csv` | XRD, two columns | Auto Loader | Angle, intensity |
| `OES.HRF` | Optical emission spectrum | OES HRF Loader | `Wavelength`, `Intensity` |
| `XRD/quick_scan.xrdml` | Panalytical XRDML 1.7, one scan | Auto Loader | `2Theta`, `Intensity` (238 points) |
| `XRD/repeated_scans.xrdml` | Panalytical XRDML 1.7, 3 scans | Auto Loader | `2Theta`, `Intensity` (sum of scans), `Intensity 1`–`3` |
| `XRD/schema1.5_scan.XRDML` | Panalytical XRDML 1.5 | Auto Loader | `2Theta`, `Intensity` (6155 points) |
| `XRD/smartlab_si_powder.ras` | Rigaku SmartLab `.ras`, Si powder with an attenuated peak | Auto Loader (Rigaku RAS Loader plugin) | `2Theta`, `Intensity` (attenuator-corrected) |
| `XRD/anneal_series/tio2_400C.ras`–`tio2_800C.ras` | Rigaku `.ras`, TiO₂ annealed at 400/600/800 °C (anatase → rutile) | Auto Loader; bulk run a sequence recorded on one of them | `2Theta`, `Intensity` |
| `Thermal/tga_calcium_oxalate.txt` | TA Instruments Universal Analysis TGA export (UTF-16) | TA Instruments TGA/DSC Loader | `Time (min)`, `Temperature (°C)`, `Weight (%)`, `Weight (mg)`, purge flows |
| `FTIR/polystyrene_film.jdx` | JCAMP-DX FTIR transmission spectrum | Auto Loader (JCAMP-DX Spectrum Loader plugin) | `Wavenumber (1/cm)`, `Transmittance` |
| `XRD/panalytical_export.csv` | Panalytical CSV export with a `[Measurement conditions]` header | Auto Loader | `Angle`, `Intensity` |
| `XRD/origin_peak_fit.csv` | Origin peak-fit table, tab-separated with row labels | Auto Loader | Fit parameters per peak |
| `EDS/edax_map.csv` | EDAX EDS map with metadata header | Auto Loader | `X/Y` row index and one column per map column |
| `EDS/smartquant_spot.csv` | EDAX eZAF SmartQuant table (quoted values) | Auto Loader | `Element`, `Weight %`, `Atomic %`, … |
| `EDS/eds_spectrum.msa` | EMSA/MAS EDS spectrum | Auto Loader | Energy, counts (4096 channels) |
| `XPS/phi_c1s_scan.csv` | PHI XPS C 1s scan stored as rows | Auto Loader | Binding energy, counts |
| `OES/spectrum_1.HRF`–`spectrum_3.HRF` | Optical emission spectra (N₂, CN, Hβ, Hα lines) | Auto Loader or OES HRF Loader; bulk run a sequence recorded on one of them | `Wavelength`, `Intensity` |

Try these:

- **XRD baseline removal:** open `XRD/quick_scan.xrdml`, then apply
  `XRD: Baseline Remove` to `Intensity` in Simple Mode.
- **Bulk run over a series:** import `XRD/anneal_series/tio2_400C.ras`, apply
  `XRD: Baseline Remove`, then in **Advanced → Run Sequence** set the input folder
  to `test_data/XRD/anneal_series`. All three `.ras` scans are processed (the
  Sequence Walkthrough on the wiki does this step by step).
