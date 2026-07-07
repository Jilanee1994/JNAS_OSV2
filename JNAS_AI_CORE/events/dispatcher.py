"""Event dispatching."""

from __future__ import annotations

import inspect
from collections.abc import Callable

from .event import Event


class EventDispatcher:
    """Dispatch events to sync or async-ready subscribers."""

    async def dispatch_async(self, event: Event, subscribers: list[Callable[[Event], object]]) -> None:
        """Dispatch an event, awaiting coroutine handlers when needed."""
        for subscriber in subscribers:
            result = subscriber(event)
            if inspect.isawaitable(result):
                await result

    def dispatch(self, event: Event, subscribers: list[Callable[[Event], object]]) -> None:
        """Dispatch an event synchronously to non-coroutine handlers."""
        for subscriber in subscribers:
            result = subscriber(event)
            if inspect.isawaitable(result):
                raise RuntimeError("Async subscriber requires dispatch_async().")
