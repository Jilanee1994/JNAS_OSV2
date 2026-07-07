"""JSON persistence for queued tasks."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any

from .models import QueuedTask


class QueuePersistence:
    """Persist queue state to disk as JSON."""

    def __init__(self, path: Path = Path("JNAS_AI_CORE/workspace/task_queue/queue.json")) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, tasks: list[QueuedTask]) -> None:
        """Save queue tasks."""
        data = [self._to_dict(task) for task in tasks]
        self.path.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8")

    def load(self) -> list[QueuedTask]:
        """Load queue tasks."""
        if not self.path.exists():
            return []
        data = json.loads(self.path.read_text(encoding="utf-8"))
        return [self._from_dict(item) for item in data]

    def _to_dict(self, task: QueuedTask) -> dict[str, Any]:
        data = asdict(task)
        for key in ("run_after", "created_at", "updated_at"):
            data[key] = getattr(task, key).isoformat()
        return data

    def _from_dict(self, data: dict[str, Any]) -> QueuedTask:
        return QueuedTask(
            task_type=data["task_type"],
            payload=dict(data.get("payload", {})),
            priority=int(data.get("priority", 100)),
            run_after=datetime.fromisoformat(data["run_after"]),
            task_id=data["task_id"],
            retries=int(data.get("retries", 0)),
            max_retries=int(data.get("max_retries", 3)),
            status=data.get("status", "pending"),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            error=data.get("error", ""),
        )
