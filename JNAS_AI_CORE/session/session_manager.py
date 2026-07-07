"""Production-ready session manager for JNAS AI Core."""

from __future__ import annotations

import atexit
import signal
import threading
import time
from datetime import timedelta
from pathlib import Path
from typing import Any

try:
    from JNAS_AI_CORE.configuration import ConfigManager
    from JNAS_AI_CORE.events import Event as CoreEvent
    from JNAS_AI_CORE.events import EventBus
    from JNAS_AI_CORE.metrics import MetricsCollector
except ImportError:
    ConfigManager = None
    CoreEvent = None
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
        config_manager: Any | None = None,
        config: dict[str, Any] | None = None,
    ) -> None:
        self.config_manager = config_manager or (ConfigManager() if ConfigManager is not None else None)
        self.config = config or {}
        self.validator = validator or SessionValidator()
        self.persistence = persistence or self._create_persistence()
        self.event_bus = event_bus
        self.metrics_collector = metrics_collector
        self.logger = get_session_logger(str(self._config_get("logging.level", "INFO")))
        self.heartbeat = Heartbeat()
        self.heartbeat_interval = float(self._config_get("session.heartbeat_interval", 30))
        self.retention_days = int(self._config_get("session.retention_days", 30))
        self._heartbeat_threads: dict[str, threading.Thread] = {}
        self._heartbeat_stops: dict[str, threading.Event] = {}
        self._shutdown_sessions: set[str] = set()
        self._signal_handlers_registered = False

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
        self.logger.info("Created session %s for project %s", session.session_id, project_name)
        with self.persistence.lock(session.session_id):
            saved = self._save(session)
        self.start_auto_heartbeat(saved.session_id)
        self.enable_graceful_shutdown(saved.session_id)
        return saved

    def resume_session(self, session_id: str) -> Session:
        """Resume an existing session after disconnect or crash."""
        with self.persistence.lock(session_id):
            session = self.persistence.load(session_id)
            if session.status != SessionStatus.ARCHIVED:
                session.status = SessionStatus.RUNNING
            if session.checkpoints:
                session.current_task = session.checkpoints[-1].data.get("current_task", session.current_task)
            session.add_timeline("SessionResumed", "Session resumed.")
            self.logger.info("Resumed session %s", session_id)
            saved = self._save(session)
        self.start_auto_heartbeat(session_id)
        self.enable_graceful_shutdown(session_id)
        return saved

    def resume_interrupted_session(self) -> Session | None:
        """Resume the most recently interrupted session from its last checkpoint."""
        candidates = [
            session
            for session in self.persistence.list_sessions()
            if session.status in {SessionStatus.RUNNING, SessionStatus.STOPPED, SessionStatus.FAILED}
        ]
        if not candidates:
            self.logger.info("No interrupted session found for resume.")
            return None
        latest = max(candidates, key=lambda item: item.last_update)
        return self.resume_session(latest.session_id)

    def stop_session(self, session_id: str) -> Session:
        """Stop a session without archiving it."""
        self.stop_auto_heartbeat(session_id)
        self._shutdown_sessions.discard(session_id)
        with self.persistence.lock(session_id):
            session = self.persistence.load(session_id)
            session.status = SessionStatus.STOPPED
            session.execution_time = self._elapsed_seconds(session)
            session.add_timeline("SessionStopped", "Session stopped.")
            self.logger.info("Stopped session %s", session_id)
            return self._save(session)

    def archive_session(self, session_id: str) -> Session:
        """Archive a completed or stopped session."""
        self.stop_auto_heartbeat(session_id)
        self._shutdown_sessions.discard(session_id)
        with self.persistence.lock(session_id):
            session = self.persistence.load(session_id)
            session.status = SessionStatus.ARCHIVED
            session.execution_time = self._elapsed_seconds(session)
            session.add_timeline("SessionArchived", "Session archived.")
            self.logger.info("Archived session %s", session_id)
            return self._save(session)

    def session_history(self) -> list[Session]:
        """Return all known sessions."""
        return self.persistence.list_sessions()

    def beat(self, session_id: str) -> Session:
        """Update heartbeat and last-update timestamp."""
        with self.persistence.lock(session_id):
            session = self.persistence.load(session_id)
            self.heartbeat.beat()
            session.touch()
            session.add_timeline("Heartbeat", "Heartbeat received.")
            self.logger.info("Heartbeat updated for session %s", session_id)
            return self._save(session)

    def start_auto_heartbeat(self, session_id: str, interval: float | None = None) -> None:
        """Start automatic heartbeat updates for a session."""
        if session_id in self._heartbeat_threads and self._heartbeat_threads[session_id].is_alive():
            return
        stop_event = threading.Event()
        self._heartbeat_stops[session_id] = stop_event
        heartbeat_interval = float(interval or self.heartbeat_interval)

        def run() -> None:
            while not stop_event.wait(heartbeat_interval):
                try:
                    self.beat(session_id)
                except Exception as exc:
                    self.logger.warning("Automatic heartbeat failed for %s: %s", session_id, exc)

        thread = threading.Thread(target=run, name=f"session-heartbeat-{session_id}", daemon=True)
        self._heartbeat_threads[session_id] = thread
        thread.start()

    def stop_auto_heartbeat(self, session_id: str) -> None:
        """Stop automatic heartbeat updates for a session."""
        stop_event = self._heartbeat_stops.pop(session_id, None)
        if stop_event is not None:
            stop_event.set()
        thread = self._heartbeat_threads.pop(session_id, None)
        if thread is not None and thread.is_alive():
            thread.join(timeout=1.0)

    def update_progress(
        self,
        session_id: str,
        current_task: str,
        completed_tasks: list[str],
        remaining_tasks: list[str],
        eta: str = "",
    ) -> Session:
        """Update task progress for a session."""
        with self.persistence.lock(session_id):
            session = self.persistence.load(session_id)
            session.current_task = current_task
            session.completed_tasks = list(completed_tasks)
            session.remaining_tasks = list(remaining_tasks)
            total = len(completed_tasks) + len(remaining_tasks)
            session.progress.update(len(completed_tasks), total, eta)
            if not remaining_tasks and completed_tasks:
                session.status = SessionStatus.COMPLETED
                self.stop_auto_heartbeat(session_id)
            session.add_timeline("ProgressUpdated", f"Progress updated to {session.progress.percent}%.")
            self.logger.info("Progress updated for session %s to %s%%", session_id, session.progress.percent)
            return self._save(session)

    def add_checkpoint(
        self,
        session_id: str,
        name: str,
        data: dict[str, Any],
    ) -> Session:
        """Add a checkpoint to a session."""
        with self.persistence.lock(session_id):
            session = self.persistence.load(session_id)
            checkpoint_data = dict(data)
            checkpoint_data.setdefault("current_task", session.current_task)
            session.checkpoints.append(Checkpoint(name=name, data=checkpoint_data))
            session.add_timeline("CheckpointCreated", f"Checkpoint created: {name}.")
            self.logger.info("Checkpoint %s created for session %s", name, session_id)
            return self._save(session)

    def recover_crashed_sessions(self) -> list[Session]:
        """Mark running sessions as stopped for crash recovery."""
        recovered = []
        for session in self.persistence.list_sessions():
            if session.status == SessionStatus.RUNNING:
                with self.persistence.lock(session.session_id):
                    session.status = SessionStatus.STOPPED
                    session.warnings.append("Recovered after possible crash or disconnect.")
                    session.add_timeline("CrashRecovered", "Session recovered after possible crash.")
                    self.logger.warning("Recovered interrupted session %s", session.session_id)
                    recovered.append(self._save(session))
        return recovered

    def cleanup_sessions(self, retention_days: int | None = None) -> dict[str, list[str]]:
        """Archive completed sessions and delete old inactive sessions."""
        cutoff = time.time() - (retention_days if retention_days is not None else self.retention_days) * 86400
        archived: list[str] = []
        deleted: list[str] = []
        for session in self.persistence.list_sessions():
            with self.persistence.lock(session.session_id):
                current = self.persistence.load(session.session_id)
                if current.status == SessionStatus.COMPLETED:
                    current.status = SessionStatus.ARCHIVED
                    current.add_timeline("SessionArchived", "Completed session archived by cleanup.")
                    self._save(current)
                    archived.append(current.session_id)
                    self.logger.info("Cleanup archived completed session %s", current.session_id)
                if current.status in {SessionStatus.ARCHIVED, SessionStatus.STOPPED, SessionStatus.FAILED}:
                    if current.last_update.timestamp() < cutoff:
                        self.persistence.delete(current.session_id)
                        self._shutdown_sessions.discard(current.session_id)
                        deleted.append(current.session_id)
                        self.logger.info("Cleanup deleted expired session %s", current.session_id)
        return {"archived": archived, "deleted": deleted}

    def record_warning(self, session_id: str, warning: str) -> Session:
        """Record a warning."""
        with self.persistence.lock(session_id):
            session = self.persistence.load(session_id)
            session.warnings.append(warning)
            session.add_timeline("Warning", warning)
            self.logger.warning("Session %s warning: %s", session_id, warning)
            return self._save(session)

    def record_error(self, session_id: str, error: str) -> Session:
        """Record an error."""
        with self.persistence.lock(session_id):
            session = self.persistence.load(session_id)
            session.errors.append(error)
            session.add_timeline("Error", error)
            self.logger.error("Session %s error: %s", session_id, error)
            return self._save(session)

    def record_self_healing_attempt(self, session_id: str) -> Session:
        """Increment self-healing attempt count."""
        with self.persistence.lock(session_id):
            session = self.persistence.load(session_id)
            session.self_healing_attempts += 1
            session.add_timeline("SelfHealingAttempt", "Self-healing attempt recorded.")
            self.logger.info("Self-healing attempt recorded for session %s", session_id)
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

    def enable_graceful_shutdown(self, session_id: str) -> None:
        """Register a session for final checkpoint persistence on shutdown."""
        self._shutdown_sessions.add(session_id)
        if self._signal_handlers_registered:
            return
        self._signal_handlers_registered = True
        atexit.register(self.graceful_shutdown)
        try:
            signal.signal(signal.SIGINT, self._handle_shutdown_signal)
            signal.signal(signal.SIGTERM, self._handle_shutdown_signal)
        except ValueError:
            self.logger.warning("Signal handlers can only be registered from the main thread.")

    def graceful_shutdown(self) -> None:
        """Save final checkpoints and stop heartbeat workers."""
        for session_id in list(self._shutdown_sessions):
            try:
                if not self.persistence.path_for(session_id).exists():
                    self._shutdown_sessions.discard(session_id)
                    continue
                self.stop_auto_heartbeat(session_id)
                self._add_shutdown_checkpoint(session_id)
            except Exception as exc:
                self.logger.error("Graceful shutdown failed for %s: %s", session_id, exc)

    def _add_shutdown_checkpoint(self, session_id: str) -> None:
        """Save a shutdown checkpoint without emitting late-process log records."""
        with self.persistence.lock(session_id):
            session = self.persistence.load(session_id)
            session.checkpoints.append(
                Checkpoint(
                    name="shutdown",
                    data={"reason": "graceful_shutdown", "current_task": session.current_task},
                )
            )
            session.add_timeline("CheckpointCreated", "Checkpoint created: shutdown.")
            self._save(session)

    def _handle_shutdown_signal(self, signum: int, _frame: Any) -> None:
        self.logger.warning("Received shutdown signal %s", signum)
        self.graceful_shutdown()
        raise KeyboardInterrupt

    def _save(self, session: Session) -> Session:
        self.validator.validate(session)
        self.persistence.save(session)
        self._publish("SessionUpdated", {"session_id": session.session_id, "status": session.status})
        return session

    def _publish(self, event_type: str, payload: dict[str, Any]) -> None:
        if self.event_bus is not None and CoreEvent is not None:
            self.event_bus.publish(CoreEvent(event_type, payload))
        if self.metrics_collector is not None:
            self.metrics_collector.record_usage("memory", "session")

    def _elapsed_seconds(self, session: Session) -> float:
        return max(0.0, time.time() - session.start_time.timestamp())

    def _create_persistence(self) -> SessionPersistence:
        storage_dir = Path(str(self._config_get("session.storage_dir", "JNAS_AI_CORE/workspace/sessions")))
        lock_timeout = float(self._config_get("session.lock_timeout", 10))
        lock_poll_interval = float(self._config_get("session.lock_poll_interval", 0.1))
        return SessionPersistence(
            storage_dir=storage_dir,
            validator=self.validator,
            lock_timeout=lock_timeout,
            lock_poll_interval=lock_poll_interval,
        )

    def _config_get(self, dotted_key: str, default: Any = None) -> Any:
        current: Any = self.config
        for part in dotted_key.split("."):
            if not isinstance(current, dict) or part not in current:
                current = None
                break
            current = current[part]
        if current is not None:
            return current
        if self.config_manager is not None:
            return self.config_manager.get(dotted_key, default)
        return default
