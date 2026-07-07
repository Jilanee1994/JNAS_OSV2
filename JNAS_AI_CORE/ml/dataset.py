"""Dataset loading utilities."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .exceptions import DatasetLoadError


@dataclass(frozen=True)
class Dataset:
    """Tabular dataset loaded from disk or memory."""

    rows: list[dict[str, Any]]
    target_column: str | None = None

    def features_and_target(self, target_column: str | None = None) -> tuple[list[dict[str, Any]], list[Any]]:
        """Split rows into feature dictionaries and target labels."""
        target = target_column or self.target_column
        if not target:
            raise DatasetLoadError("A target column is required for supervised training.")
        features: list[dict[str, Any]] = []
        labels: list[Any] = []
        for row in self.rows:
            if target not in row:
                raise DatasetLoadError(f"Target column not found: {target}")
            labels.append(row[target])
            features.append({key: value for key, value in row.items() if key != target})
        return features, labels


class DatasetLoader:
    """Load datasets from CSV, JSON, Parquet, and Excel files."""

    def load(self, path: Path, target_column: str | None = None) -> Dataset:
        """Load a dataset by file extension."""
        path = Path(path)
        if not path.exists():
            raise DatasetLoadError(f"Dataset not found: {path}")
        suffix = path.suffix.lower()
        if suffix == ".csv":
            return Dataset(self._load_csv(path), target_column)
        if suffix == ".json":
            return Dataset(self._load_json(path), target_column)
        if suffix in {".parquet", ".xlsx", ".xls"}:
            return Dataset(self._load_with_pandas(path), target_column)
        raise DatasetLoadError(f"Unsupported dataset format: {suffix}")

    def from_rows(self, rows: list[dict[str, Any]], target_column: str | None = None) -> Dataset:
        """Create a dataset from in-memory rows."""
        return Dataset(rows=list(rows), target_column=target_column)

    def _load_csv(self, path: Path) -> list[dict[str, Any]]:
        with path.open("r", encoding="utf-8", newline="") as handle:
            return [dict(row) for row in csv.DictReader(handle)]

    def _load_json(self, path: Path) -> list[dict[str, Any]]:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return [dict(row) for row in data]
        if isinstance(data, dict) and isinstance(data.get("rows"), list):
            return [dict(row) for row in data["rows"]]
        raise DatasetLoadError("JSON dataset must be a list of objects or contain a rows list.")

    def _load_with_pandas(self, path: Path) -> list[dict[str, Any]]:
        try:
            import pandas as pd
        except ImportError as exc:
            raise DatasetLoadError(f"Reading {path.suffix} requires pandas.") from exc
        if path.suffix.lower() == ".parquet":
            frame = pd.read_parquet(path)
        else:
            frame = pd.read_excel(path)
        return frame.to_dict(orient="records")
