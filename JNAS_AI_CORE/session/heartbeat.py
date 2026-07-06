"""Session heartbeat management."""

from __future__ import annotations

from datetime import datetime

from .models import utc_now


class Heartbeat:
    """Track session liveness."""

    def __init__(self) -> None:
        self.last_seen = utc_now()

    def beat(self) -> datetime:
        """Update and return the heartbeat timestamp."""
        self.last_seen = utc_now()
        return self.last_seen
