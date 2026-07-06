"""JSON persistence for sessions."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any

from .checkpoint import Checkpoint
from .exceptions import SessionNotFound
from .models import TimelineEvent
from .progress import Progress
from .session import Session


class SessionPersistence:
    """Persist sessions as JSON files."""

    def __init__(self, storage_dir: Path | None = None) -> None:
        package_root = Path(__file__).resolve().parents[1]
        self.storage_dir = storage_dir or package_root / "workspace" / "sessions"
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save(self, session: Session) -> Path:
        """Save a session to disk."""
        path = self.path_for(session.session_id)
        path.write_text(json.dumps(self.to_dict(session), indent=4, ensure_ascii=False), encoding="utf-8")
        return path

    def load(self, session_id: str) -> Session:
        """Load a session by ID."""
        path = self.path_for(session_id)
        if not path.exists():
            raise SessionNotFound(f"Session not found: {session_id}")
        return self.from_dict(json.loads(path.read_text(encoding="utf-8")))

    def list_sessions(self) -> list[Session]:
        """Load all sessions."""
        return [self.from_dict(json.loads(path.read_text(encoding="utf-8"))) for path in sorted(self.storage_dir.glob("*.json"))]

    def path_for(self, session_id: str) -> Path:
        """Return session JSON path."""
        return self.storage_dir / f"{session_id}.json"

    def to_dict(self, session: Session) -> dict[str, Any]:
        """Convert session to JSON-compatible dictionary."""
        data = asdict(session)
        for key in ("start_time", "last_update"):
            data[key] = getattr(session, key).isoformat()
        for checkpoint in data["checkpoints"]:
            checkpoint["created_at"] = checkpoint["created_at"].isoformat()
        for event in data["timeline"]:
            event["timestamp"] = event["timestamp"].isoformat()
        return data

    def from_dict(self, data: dict[str, Any]) -> Session:
        """Create a session from persisted data."""
        session = Session(
            project_name=data["project_name"],
            worker_name=data["worker_name"],
            current_task=data.get("current_task", ""),
            session_id=data["session_id"],
            status=data.get("status", "created"),
            progress=Progress(**data.get("progress", {})),
            start_time=datetime.fromisoformat(data["start_time"]),
            last_update=datetime.fromisoformat(data["last_update"]),
            completed_tasks=list(data.get("completed_tasks", [])),
            remaining_tasks=list(data.get("remaining_tasks", [])),
            warnings=list(data.get("warnings", [])),
            errors=list(data.get("errors", [])),
            self_healing_attempts=int(data.get("self_healing_attempts", 0)),
            memory_usage=dict(data.get("memory_usage", {})),
            execution_time=float(data.get("execution_time", 0.0)),
            metadata=dict(data.get("metadata", {})),
        )
        session.checkpoints = [
            Checkpoint(
                name=item["name"],
                data=dict(item.get("data", {})),
                checkpoint_id=item["checkpoint_id"],
                created_at=datetime.fromisoformat(item["created_at"]),
            )
            for item in data.get("checkpoints", [])
        ]
        session.timeline = [
            TimelineEvent(
                event_type=item["event_type"],
                message=item["message"],
                timestamp=datetime.fromisoformat(item["timestamp"]),
                metadata=dict(item.get("metadata", {})),
            )
            for item in data.get("timeline", [])
        ]
        return session
