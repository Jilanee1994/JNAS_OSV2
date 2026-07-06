"""Event subscribers."""

from __future__ import annotations

from typing import Protocol

from .event import Event


class EventSubscriber(Protocol):
    """Subscriber protocol for event delivery."""

    def handle_event(self, event: Event) -> None:
        """Handle an event."""
