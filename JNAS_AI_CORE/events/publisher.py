"""Event publishing helper."""

from __future__ import annotations

from .event import Event
from .event_bus import EventBus


class EventPublisher:
    """Small publisher wrapper around EventBus."""

    def __init__(self, event_bus: EventBus) -> None:
        self.event_bus = event_bus

    def publish(self, event_type: str, payload: dict | None = None) -> None:
        """Publish an event by type."""
        self.event_bus.publish(Event(event_type, payload or {}))
