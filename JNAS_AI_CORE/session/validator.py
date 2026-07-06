"""Session validation."""

from __future__ import annotations

from typing import Any

from .exceptions import SessionSchemaError, SessionValidationError
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

    def validate_json(self, data: dict[str, Any]) -> bool:
        """Validate persisted session JSON before it is deserialized."""
        required = {
            "session_id": str,
            "project_name": str,
            "worker_name": str,
            "status": str,
            "progress": dict,
            "start_time": str,
            "last_update": str,
            "completed_tasks": list,
            "remaining_tasks": list,
            "warnings": list,
            "errors": list,
            "self_healing_attempts": int,
            "memory_usage": dict,
            "execution_time": (int, float),
            "checkpoints": list,
            "timeline": list,
            "metadata": dict,
        }
        for field_name, expected_type in required.items():
            if field_name not in data:
                raise SessionSchemaError(f"Missing session field: {field_name}")
            if not isinstance(data[field_name], expected_type):
                raise SessionSchemaError(f"Invalid type for session field: {field_name}")
        return True
