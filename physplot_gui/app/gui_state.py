"""Shared GUI state that survives mode switches."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from physplot import PhysPlot


@dataclass
class GuiState:
    pp: PhysPlot = field(default_factory=PhysPlot)
    current_file: Path | None = None
    workflow_file: Path | None = None
    mode: str = "Simple"
    transformations: list[dict] = field(default_factory=list)
    timeline: list[dict] = field(default_factory=list)

    @property
    def dataframe(self) -> pd.DataFrame:
        if self.pp.dataset is None:
            return pd.DataFrame()
        return self.pp.dataset.dataframe

    @property
    def roles(self) -> dict[str, str]:
        if self.pp.dataset is None:
            return {}
        return dict(self.pp.dataset.column_roles)

    @property
    def row_count(self) -> int:
        return len(self.dataframe.index)

    @property
    def column_count(self) -> int:
        return len(self.dataframe.columns)

    def load_dataframe(self, df: pd.DataFrame, name: str = "manual") -> None:
        self.pp.load(df, loader="dataframe", dataset_name=name)

    def set_role(self, column: str, role: str) -> None:
        if self.pp.dataset is None:
            return
        self.pp.dataset.set_role(column, role)

    def refresh_dataset_values(self, df: pd.DataFrame) -> None:
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
