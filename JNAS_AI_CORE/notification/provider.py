"""Notification provider interfaces."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class NotificationMessage:
    """A notification emitted by the AI OS."""

    event_type: str
    title: str
    body: str
    priority: str = "normal"


class NotificationProvider(Protocol):
    """Notification provider interface."""

    name: str

    def send(self, message: NotificationMessage) -> bool:
        """Send a notification."""


class LogNotificationProvider:
    """Default local notification provider that logs messages."""

    name = "log"

    def send(self, message: NotificationMessage) -> bool:
        """Write the notification to stdout-compatible logging."""
        import logging

        logging.getLogger("JNAS_AI_CORE.notification").info("%s: %s", message.title, message.body)
        return True
