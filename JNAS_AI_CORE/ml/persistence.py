"""Model persistence for workspace model versions."""

from __future__ import annotations

import json
import pickle
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from .exceptions import ModelNotFoundError, ModelPersistenceError


class ModelPersistence:
    """Save and load versioned model artifacts."""

    def __init__(self, storage_dir: Path) -> None:
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save(
        self,
        model_name: str,
        model: Any,
        metadata: dict[str, Any],
        metrics: Any,
        artifacts: dict[str, Any] | None = None,
    ) -> Path:
        """Save a model version with metadata and metrics."""
        version = metadata.get("version") or datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        model_dir = self.storage_dir / model_name / str(version)
        model_dir.mkdir(parents=True, exist_ok=True)
        metadata = dict(metadata)
        metadata.setdefault("model_id", str(uuid4()))
        metadata["version"] = str(version)
        self._write_json(model_dir / "metadata.json", metadata)
        self._write_json(model_dir / "metrics.json", self._to_json(metrics))
        try:
            with (model_dir / "model.pkl").open("wb") as handle:
                pickle.dump({"model": model, "artifacts": artifacts or {}}, handle)
        except OSError as exc:
            raise ModelPersistenceError(f"Failed to save model: {model_dir}") from exc
        return model_dir

    def load(self, model_name: str, version: str | None = None) -> dict[str, Any]:
        """Load a model version."""
        model_dir = self._resolve_model_dir(model_name, version)
        try:
            with (model_dir / "model.pkl").open("rb") as handle:
                payload = pickle.load(handle)
            metadata = json.loads((model_dir / "metadata.json").read_text(encoding="utf-8"))
            metrics = json.loads((model_dir / "metrics.json").read_text(encoding="utf-8"))
        except (OSError, pickle.PickleError, json.JSONDecodeError) as exc:
            raise ModelPersistenceError(f"Failed to load model: {model_dir}") from exc
        return {"model": payload["model"], "artifacts": payload.get("artifacts", {}), "metadata": metadata, "metrics": metrics}

    def list_versions(self, model_name: str) -> list[str]:
        """List available versions for a model name."""
        model_root = self.storage_dir / model_name
        if not model_root.exists():
            return []
        return sorted(path.name for path in model_root.iterdir() if path.is_dir())

    def _resolve_model_dir(self, model_name: str, version: str | None) -> Path:
        versions = self.list_versions(model_name)
        if not versions:
            raise ModelNotFoundError(f"No versions found for model: {model_name}")
        selected = version or versions[-1]
        model_dir = self.storage_dir / model_name / selected
        if not model_dir.exists():
            raise ModelNotFoundError(f"Model version not found: {model_name}/{selected}")
        return model_dir

    def _write_json(self, path: Path, data: Any) -> None:
        path.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8")

    def _to_json(self, value: Any) -> Any:
        if is_dataclass(value):
            return asdict(value)
        return value
