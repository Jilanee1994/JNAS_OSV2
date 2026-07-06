"""Tests for Event Bus."""

from __future__ import annotations

import asyncio

from JNAS_AI_CORE.events import Event, EventBus


def test_publish_subscribe_unsubscribe() -> None:
    bus = EventBus()
    seen = []
    handler = lambda event: seen.append(event.event_type)

    bus.subscribe("TaskStarted", handler)
    bus.publish(Event("TaskStarted"))
    bus.unsubscribe("TaskStarted", handler)
    bus.publish(Event("TaskStarted"))

    assert seen == ["TaskStarted"]


def test_async_publish() -> None:
    bus = EventBus()
    seen = []

    async def handler(event):
        seen.append(event.event_type)

    bus.subscribe("TaskFinished", handler)
    asyncio.run(bus.publish_async(Event("TaskFinished")))

    assert seen == ["TaskFinished"]
