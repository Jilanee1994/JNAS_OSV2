"""Thread-safe event bus."""

from __future__ import annotations

import threading
from collections import defaultdict
from collections.abc import Callable

from .dispatcher import EventDispatcher
from .event import Event


class EventBus:
    """Publish, subscribe, unsubscribe, and dispatch core events."""

    EVENT_TYPES = {
        "TaskStarted", "TaskFinished", "TaskFailed", "RecoveryStarted",
        "RecoveryFinished", "PatchApplied", "MemorySaved", "ToolRegistered",
        "ExecutionCompleted", "PlannerFinished",
    }

    def __init__(self, dispatcher: EventDispatcher | None = None) -> None:
        self.dispatcher = dispatcher or EventDispatcher()
        self._subscribers: dict[str, list[Callable[[Event], object]]] = defaultdict(list)
        self._lock = threading.RLock()

    def subscribe(self, event_type: str, subscriber: Callable[[Event], object]) -> None:
        """Subscribe to an event type."""
        with self._lock:
            if subscriber not in self._subscribers[event_type]:
                self._subscribers[event_type].append(subscriber)

    def unsubscribe(self, event_type: str, subscriber: Callable[[Event], object]) -> None:
        """Unsubscribe from an event type."""
        with self._lock:
            if subscriber in self._subscribers[event_type]:
                self._subscribers[event_type].remove(subscriber)

    def publish(self, event: Event) -> None:
        """Publish and dispatch an event synchronously."""
        self.dispatch(event)

    def dispatch(self, event: Event) -> None:
        """Dispatch an event to subscribers."""
        with self._lock:
            subscribers = list(self._subscribers.get(event.event_type, []))
        self.dispatcher.dispatch(event, subscribers)

    async def publish_async(self, event: Event) -> None:
        """Publish and dispatch an event asynchronously."""
        with self._lock:
            subscribers = list(self._subscribers.get(event.event_type, []))
        await self.dispatcher.dispatch_async(event, subscribers)
