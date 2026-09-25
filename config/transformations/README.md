# Transformations

Mathematical Transformation functions shown in Simple Mode. Each file defines
`transform(values)` operating on a NumPy array or pandas Series and returning
the transformed values. Optional `DISPLAY_NAME` sets the menu label. Files are
sorted by name, so keep the `NN_` prefix if ordering matters.

Applying one records a replayable `TransformColumnStep` whose `function_name`
is the file stem (for example `"02_square"`), so saved sequences, exported
`Sequence.py` files and bulk runs resolve it from this folder headlessly.
Renaming a file breaks sequences that reference the old name.
