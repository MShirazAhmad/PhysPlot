"""PhysPlot data loaders."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from physplot.core.dataset import Dataset
from physplot.core.metadata import infer_suggested_role, parse_column_label

MODULE_ID = "physplot.loaders.base"
MODULE_VERSION = "1.0.0"
MODULE_REVISION = "2026-05-30-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"


class BaseLoader:
    loader_id = "base"
    name = "Base Loader"
    supported_extensions: tuple[str, ...] = ()
    file_format = "manual"

    def load(self, source, dataset_name: str | None = None) -> Dataset:
        path = Path(source)
        df = self.read_dataframe(path)
        return self.dataset_from_dataframe(df, dataset_name or path.stem, source_path=path)

    def read_dataframe(self, path: Path) -> pd.DataFrame:
        raise NotImplementedError

    def dataset_from_dataframe(
        self,
        df: pd.DataFrame,
        dataset_name: str,
        source_path: Path | None = None,
    ) -> Dataset:
        df = df.copy()
        df.columns = [str(column) for column in df.columns]
        column_metadata = build_column_metadata(df)
        metadata = {
            "loader_id": self.loader_id,
            "loader_name": self.name,
            "file_format": self.file_format,
            "dataset_type": "generic",
            "rows": len(df),
            "columns": len(df.columns),
        }
        return Dataset(
            name=dataset_name,
            dataframe=df,
            source_path=source_path,
            loader_name=self.name,
            loader_id=self.loader_id,
            column_metadata=column_metadata,
            metadata=metadata,
        )


class CSVLoader(BaseLoader):
    loader_id = "csv"
    name = "CSV Loader"
    supported_extensions = (".csv",)
    file_format = "csv"

    def read_dataframe(self, path: Path) -> pd.DataFrame:
        return pd.read_csv(path)


class TXTLoader(BaseLoader):
    loader_id = "txt"
    name = "TXT Loader"
    supported_extensions = (".txt", ".dat")
    file_format = "txt"

    def read_dataframe(self, path: Path) -> pd.DataFrame:
        try:
            return pd.read_csv(path, sep=None, engine="python")
        except Exception:
            return pd.read_csv(path, sep=r"\s+")


class ExcelLoader(BaseLoader):
    loader_id = "excel"
    name = "Excel Loader"
    supported_extensions = (".xls", ".xlsx")
    file_format = "excel"

    def read_dataframe(self, path: Path) -> pd.DataFrame:
        return pd.read_excel(path)


class NanoindentationLoader(BaseLoader):
    loader_id = "nanoindentation"
    name = "Nanoindentation Loader"
    supported_extensions = (".csv", ".txt", ".dat", ".xls", ".xlsx")
    file_format = "nanoindentation"

    def read_dataframe(self, path: Path) -> pd.DataFrame:
        suffix = path.suffix.lower()
        if suffix in {".xls", ".xlsx"}:
            return pd.read_excel(path)
        if suffix == ".csv":
            return pd.read_csv(path)
        try:
            return pd.read_csv(path, sep=None, engine="python")
        except Exception:
            return pd.read_csv(path, sep=r"\s+")

    def dataset_from_dataframe(
        self,
        df: pd.DataFrame,
        dataset_name: str,
        source_path: Path | None = None,
    ) -> Dataset:
        dataset = super().dataset_from_dataframe(df, dataset_name, source_path=source_path)
        dataset.metadata["dataset_type"] = "nanoindentation"
        dataset.metadata["instrument_family"] = "Agilent/KLA/Keysight"
        return dataset


class DataFrameLoader(BaseLoader):
    loader_id = "dataframe"
    name = "DataFrame Loader"
    supported_extensions = ()
    file_format = "dataframe"

    def load(self, source: pd.DataFrame, dataset_name: str | None = None) -> Dataset:
        if not isinstance(source, pd.DataFrame):
            raise TypeError("DataFrameLoader requires a pandas DataFrame.")
        return self.dataset_from_dataframe(source, dataset_name or "dataframe")


class AutoLoader(BaseLoader):
    loader_id = "auto"
    name = "Auto Loader"
    supported_extensions = ()
    file_format = "auto"

    def load(self, source: Any, dataset_name: str | None = None) -> Dataset:
        if isinstance(source, pd.DataFrame):
            dataset = DataFrameLoader().load(source, dataset_name=dataset_name)
            detected_id = dataset.loader_id
        else:
            path = Path(source)
            loader = loader_for_path(path)
            dataset = loader.load(path, dataset_name=dataset_name)
            detected_id = loader.loader_id
        dataset.metadata["detected_loader_id"] = detected_id
        dataset.metadata["loader_id"] = self.loader_id
        dataset.metadata["loader_name"] = self.name
        dataset.loader_id = self.loader_id
        dataset.loader_name = self.name
        return dataset


def build_column_metadata(df: pd.DataFrame) -> dict[str, dict]:
    metadata = {}
    for index, column in enumerate(df.columns, start=1):
        column_name = str(column)
        parsed = parse_column_label(column_name)
        unit = parsed["unit"]
        metadata[column_name] = {
            "title": parsed["title"],
            "source_label": parsed["source_label"],
            "column_number": index,
            "unit": unit,
            "dtype": str(df[column_name].dtype),
            "suggested_role": infer_suggested_role(parsed["title"], unit),
            "derived": False,
        }
    return metadata


def get_loader(loader: str | BaseLoader = "auto") -> BaseLoader:
    if isinstance(loader, BaseLoader):
        return loader
    loaders = loader_classes()
    try:
        return loaders[str(loader).lower()]()
    except KeyError as exc:
        raise ValueError(f"Unknown loader '{loader}'.") from exc


def loader_classes() -> dict[str, type[BaseLoader]]:
    return {
        "auto": AutoLoader,
        "csv": CSVLoader,
        "txt": TXTLoader,
        "excel": ExcelLoader,
        "nanoindentation": NanoindentationLoader,
        "dataframe": DataFrameLoader,
    }


def list_loaders() -> list[BaseLoader]:
    return [loader_cls() for loader_cls in loader_classes().values()]


def loader_for_path(path: Path) -> BaseLoader:
    suffix = path.suffix.lower()
    for loader_cls in (CSVLoader, TXTLoader, ExcelLoader):
        if suffix in loader_cls.supported_extensions:
            return loader_cls()
    raise ValueError(f"No loader available for extension '{suffix}'.")
