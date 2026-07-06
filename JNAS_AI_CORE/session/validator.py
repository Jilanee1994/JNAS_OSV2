"""Session validation."""

from __future__ import annotations

from .exceptions import SessionValidationError
from .session import Session


class SessionValidator:
    """Validate session data."""

    def validate(self, session: Session) -> bool:
        """Validate required session fields."""
        if not session.session_id:
            raise SessionValidationError("session_id is required.")
        if not session.project_name:
            raise SessionValidationError("project_name is required.")
        if not session.worker_name:
            raise SessionValidationError("worker_name is required.")
        if not 0 <= session.progress.percent <= 100:
            raise SessionValidationError("progress percent must be between 0 and 100.")
        return True
