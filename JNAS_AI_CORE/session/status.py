"""Session status constants."""

from __future__ import annotations


class SessionStatus:
    """Supported session lifecycle states."""

    CREATED = "created"
    RUNNING = "running"
    STOPPED = "stopped"
    ARCHIVED = "archived"
    COMPLETED = "completed"
    FAILED = "failed"
