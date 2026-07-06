"""Production-ready session manager for JNAS AI Core."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

try:
    from JNAS_AI_CORE.events import Event, EventBus
    from JNAS_AI_CORE.metrics import MetricsCollector
except ImportError:
    Event = None
    EventBus = None
    MetricsCollector = None

from .checkpoint import Checkpoint
from .heartbeat import Heartbeat
from .logger import get_session_logger
from .persistence import SessionPersistence
from .session import Session
from .status import SessionStatus
from .validator import SessionValidator


class SessionManager:
    """Create, resume, stop, archive, and track persistent sessions."""

    def __init__(
        self,
        persistence: SessionPersistence | None = None,
        validator: SessionValidator | None = None,
        event_bus: Any | None = None,
        metrics_collector: Any | None = None,
    ) -> None:
        self.persistence = persistence or SessionPersistence()
        self.validator = validator or SessionValidator()
        self.event_bus = event_bus
        self.metrics_collector = metrics_collector
        self.logger = get_session_logger()
        self.heartbeat = Heartbeat()

    def create_session(
        self,
        project_name: str,
        worker_name: str,
        remaining_tasks: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Session:
        """Create and persist a new running session."""
        session = Session(
            project_name=project_name,
            worker_name=worker_name,
            status=SessionStatus.RUNNING,
            remaining_tasks=list(remaining_tasks or []),
            metadata=metadata or {},
        )
        session.add_timeline("SessionCreated", f"Session created for {project_name}.")
        return self._save(session)

    def resume_session(self, session_id: str) -> Session:
        """Resume an existing session after disconnect or crash."""
        session = self.persistence.load(session_id)
        if session.status != SessionStatus.ARCHIVED:
            session.status = SessionStatus.RUNNING
        session.add_timeline("SessionResumed", "Session resumed.")
        return self._save(session)

    def stop_session(self, session_id: str) -> Session:
        """Stop a session without archiving it."""
        session = self.persistence.load(session_id)
        session.status = SessionStatus.STOPPED
        session.execution_time = self._elapsed_seconds(session)
        session.add_timeline("SessionStopped", "Session stopped.")
        return self._save(session)

    def archive_session(self, session_id: str) -> Session:
        """Archive a completed or stopped session."""
        session = self.persistence.load(session_id)
        session.status = SessionStatus.ARCHIVED
        session.execution_time = self._elapsed_seconds(session)
        session.add_timeline("SessionArchived", "Session archived.")
        return self._save(session)

    def session_history(self) -> list[Session]:
        """Return all known sessions."""
        return self.persistence.list_sessions()

    def beat(self, session_id: str) -> Session:
        """Update heartbeat and last-update timestamp."""
        session = self.persistence.load(session_id)
        self.heartbeat.beat()
        session.touch()
        session.add_timeline("Heartbeat", "Heartbeat received.")
        return self._save(session)

    def update_progress(
        self,
        session_id: str,
        current_task: str,
        completed_tasks: list[str],
        remaining_tasks: list[str],
        eta: str = "",
    ) -> Session:
        """Update task progress for a session."""
        session = self.persistence.load(session_id)
        session.current_task = current_task
        session.completed_tasks = list(completed_tasks)
        session.remaining_tasks = list(remaining_tasks)
        total = len(completed_tasks) + len(remaining_tasks)
        session.progress.update(len(completed_tasks), total, eta)
        session.add_timeline("ProgressUpdated", f"Progress updated to {session.progress.percent}%.")
        return self._save(session)

    def add_checkpoint(
        self,
        session_id: str,
        name: str,
        data: dict[str, Any],
    ) -> Session:
        """Add a checkpoint to a session."""
        session = self.persistence.load(session_id)
        session.checkpoints.append(Checkpoint(name=name, data=data))
        session.add_timeline("CheckpointCreated", f"Checkpoint created: {name}.")
        return self._save(session)

    def recover_crashed_sessions(self) -> list[Session]:
        """Mark running sessions as stopped for crash recovery."""
        recovered = []
        for session in self.persistence.list_sessions():
            if session.status == SessionStatus.RUNNING:
                session.status = SessionStatus.STOPPED
                session.warnings.append("Recovered after possible crash or disconnect.")
                session.add_timeline("CrashRecovered", "Session recovered after possible crash.")
                recovered.append(self._save(session))
        return recovered

    def record_warning(self, session_id: str, warning: str) -> Session:
        """Record a warning."""
        session = self.persistence.load(session_id)
        session.warnings.append(warning)
        session.add_timeline("Warning", warning)
        return self._save(session)

    def record_error(self, session_id: str, error: str) -> Session:
        """Record an error."""
        session = self.persistence.load(session_id)
        session.errors.append(error)
        session.add_timeline("Error", error)
        return self._save(session)

    def record_self_healing_attempt(self, session_id: str) -> Session:
        """Increment self-healing attempt count."""
        session = self.persistence.load(session_id)
        session.self_healing_attempts += 1
        session.add_timeline("SelfHealingAttempt", "Self-healing attempt recorded.")
        return self._save(session)

    def get_status(self, session_id: str) -> dict[str, Any]:
        """Return display-ready session status."""
        session = self.persistence.load(session_id)
        return {
            "Project": session.project_name,
            "Status": session.status,
            "Worker": session.worker_name,
            "Progress": f"{session.progress.percent:g}%",
            "Current Task": session.current_task,
            "Started": session.start_time.isoformat(),
            "Last Update": session.last_update.isoformat(),
            "ETA": session.progress.eta,
        }

    def _save(self, session: Session) -> Session:
        self.validator.validate(session)
        self.persistence.save(session)
        self._publish("SessionUpdated", {"session_id": session.session_id, "status": session.status})
        return session

    def _publish(self, event_type: str, payload: dict[str, Any]) -> None:
        if self.event_bus is not None and Event is not None:
            self.event_bus.publish(Event(event_type, payload))
        if self.metrics_collector is not None:
            self.metrics_collector.record_usage("memory", "session")

    def _elapsed_seconds(self, session: Session) -> float:
        return max(0.0, time.time() - session.start_time.timestamp())
