"""Persistent scheduler storage."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any

from .job import ScheduledJob


class ScheduleStore:
    """Store scheduled jobs as JSON."""

    def __init__(self, path: Path = Path("JNAS_AI_CORE/workspace/scheduler/jobs.json")) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, jobs: list[ScheduledJob]) -> None:
        """Save jobs."""
        self.path.write_text(json.dumps([self._to_dict(job) for job in jobs], indent=4), encoding="utf-8")

    def load(self) -> list[ScheduledJob]:
        """Load jobs."""
        if not self.path.exists():
            return []
        return [self._from_dict(item) for item in json.loads(self.path.read_text(encoding="utf-8"))]

    def _to_dict(self, job: ScheduledJob) -> dict[str, Any]:
        data = asdict(job)
        data["run_at"] = job.run_at.isoformat()
        data["last_run"] = job.last_run.isoformat() if job.last_run else None
        return data

    def _from_dict(self, data: dict[str, Any]) -> ScheduledJob:
        return ScheduledJob(
            name=data["name"],
            task_type=data["task_type"],
            payload=dict(data.get("payload", {})),
            run_at=datetime.fromisoformat(data["run_at"]),
            interval_seconds=data.get("interval_seconds"),
            cron=data.get("cron"),
            enabled=bool(data.get("enabled", True)),
            job_id=data["job_id"],
            last_run=datetime.fromisoformat(data["last_run"]) if data.get("last_run") else None,
            missed_runs=int(data.get("missed_runs", 0)),
        )
