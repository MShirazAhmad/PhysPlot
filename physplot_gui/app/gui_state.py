"""Shared GUI state that survives mode switches.

The main window owns exactly one :class:`GuiState`. Simple mode, Advanced mode, the central
table and the status bar all read from it, so switching modes never loses data, roles,
file names or the recorded protocol. The state wraps the backend :class:`physplot.PhysPlot`
object, which holds the current dataset (data, column roles and metadata) and the list of
recorded workflow steps; the GUI adds the file names, the current mode and the display
rows for the transformation pipeline and the protocol sequence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

from physplot import PhysPlot


@dataclass
class GuiState:
    """Hold everything the GUI needs to remember between actions and mode switches.

    :ivar pp: The backend :class:`physplot.PhysPlot` object. ``pp.dataset`` is the current
        dataset and ``pp.workflow`` the recorded, replayable protocol steps. A new
        ``PhysPlot`` is created for each state.
    :ivar current_file: Path of the last imported data file, or ``None`` (for example for
        a new or hand-typed table). Shown as ``File:`` in the status bar.
    :ivar workflow_file: Path of the last saved or loaded protocol sequence, or ``None``.
        Shown as ``Workflow:`` in the status bar in Advanced mode.
    :ivar mode: The active GUI mode, ``"Simple"`` (default) or ``"Advanced"``.
    :ivar transformations: Display rows of the applied transformation pipeline, one dict
        per transformation with ``input``, ``function``, ``params`` and ``output`` keys;
        passed to the mode panels' ``refresh_pipeline``.
    :ivar timeline: Rows of the Build Protocol sequence table, one dict per recorded
        action with keys such as ``action``, ``details``, ``target``,
        ``workflow_index``/``workflow_indices`` (positions in ``pp.workflow``) and
        ``code``; passed to the Advanced panel's ``refresh_timeline``.
    """
    pp: PhysPlot = field(default_factory=PhysPlot)
    current_file: Path | None = None
    workflow_file: Path | None = None
    mode: str = "Simple"
    transformations: list[dict] = field(default_factory=list)
    timeline: list[dict] = field(default_factory=list)

    @property
    def dataframe(self) -> pd.DataFrame:
        """Return the current dataset's DataFrame, or an empty one when no data is loaded.

        This is the backend frame itself, not a copy.
        """
        if self.pp.dataset is None:
            return pd.DataFrame()
        return self.pp.dataset.dataframe

    @property
    def roles(self) -> dict[str, str]:
        """Return a copy of the dataset's column-to-role mapping (empty with no dataset).

        The main window passes it to the central table's role dropdowns.
        """
        if self.pp.dataset is None:
            return {}
        return dict(self.pp.dataset.column_roles)

    @property
    def row_count(self) -> int:
        """Return the rows up to the last one holding a value (shown as ``Rows:``).

        Trailing blank rows are not counted, so the blank start-up table reports 0.
        """
        return self._filled_extent()[0]

    @property
    def column_count(self) -> int:
        """Return the columns up to the last one holding a value (shown as ``Columns:``).

        Trailing blank columns are not counted, so the blank start-up table reports 0.
        """
        return self._filled_extent()[1]

    def _filled_extent(self) -> tuple[int, int]:
        """Return ``(rows, columns)`` up to the last cell that is neither missing nor blank.

        Only text columns are checked for blank strings, so numeric data costs one
        ``notna`` pass.
        """
        df = self.dataframe
        if df.empty:
            return 0, 0
        filled = df.notna()
        text_columns = df.select_dtypes(include=["object", "string"]).columns
        if len(text_columns):
            filled[text_columns] &= df[text_columns].astype(str).apply(lambda column: column.str.strip().ne(""))
        mask = filled.to_numpy()
        rows = np.flatnonzero(mask.any(axis=1))
        columns = np.flatnonzero(mask.any(axis=0))
        return (int(rows[-1]) + 1 if rows.size else 0, int(columns[-1]) + 1 if columns.size else 0)

    def load_dataframe(self, df: pd.DataFrame, name: str = "manual") -> None:
        """Replace the current dataset with ``df`` through the backend DataFrame loader.

        The new dataset starts with fresh metadata and every role ``Ignore``. No workflow
        step is recorded. The main window uses this for the blank start-up table, for a
        new table, and for data read by a loader plugin.

        :param df: Data for the new dataset.
        :param name: Dataset name (default ``"manual"``).
        """
        self.pp.load(df, loader="dataframe", dataset_name=name)

    def set_role(self, column: str, role: str) -> None:
        """Assign ``role`` to ``column`` on the current dataset.

        Does nothing when no dataset is loaded. The backend clears the single-use roles
        (``X``, ``Y``, ``X Error``, ``Y Error``, ``Fit Weight``) from any other column. No
        workflow step is recorded here; the main window records the ``SetRoleStep``.

        :param column: Column name (or other column reference the backend accepts).
        :param role: Role name from the role dropdown.
        """
        if self.pp.dataset is None:
            return
        self.pp.dataset.set_role(column, role)

    def refresh_dataset_values(self, df: pd.DataFrame) -> None:
        """Replace the dataset's values with ``df`` while keeping roles and metadata.

        Called by ``MainWindow.sync_table_to_backend`` after every edit in the central
        table, with the table's trimmed contents, so the backend always holds what the user
        sees. With no dataset loaded it simply loads ``df`` (see :meth:`load_dataframe`).
        Otherwise the dataset is reloaded from ``df`` under its current name, and then:

        * the dataset-level metadata dict of the old dataset is merged back over the new
          one (old keys win);
        * the old ``source_path``, ``loader_id`` and ``loader_name`` are restored, so the
          dataset still reports the file and loader it originally came from;
        * each old column role is restored for every column still present in ``df``;
        * each old per-column metadata entry is merged back over the new one for every
          column still present in ``df``.

        Columns that are new in ``df`` get default metadata and the role ``Ignore``;
        roles and metadata of columns no longer present are dropped. No workflow step is
        recorded, since the individual edits are recorded by the main window.

        :param df: The new values, normally ``CentralTable.to_dataframe()``.
        """
        if self.pp.dataset is None:
            self.load_dataframe(df)
            return
        old_roles = dict(self.pp.dataset.column_roles)
        old_metadata_root = dict(self.pp.dataset.metadata)
        old_source_path = self.pp.dataset.source_path
        old_loader_id = self.pp.dataset.loader_id
        old_loader_name = self.pp.dataset.loader_name
        old_metadata = {
            column: dict(self.pp.dataset.column_metadata.get(column, {}))
            for column in df.columns
            if column in self.pp.dataset.column_metadata
        }
        self.pp.load(df, loader="dataframe", dataset_name=self.pp.dataset.name)
        self.pp.dataset.metadata.update(old_metadata_root)
        self.pp.dataset.source_path = old_source_path
        self.pp.dataset.loader_id = old_loader_id
        self.pp.dataset.loader_name = old_loader_name
        for column, role in old_roles.items():
            if column in self.pp.dataset.dataframe.columns:
                self.pp.dataset.column_roles[column] = role
        for column, metadata in old_metadata.items():
            if column in self.pp.dataset.column_metadata:
                self.pp.dataset.column_metadata[column].update(metadata)
