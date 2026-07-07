"""Notification center for AI OS events."""

from __future__ import annotations

import threading
from collections import defaultdict

from .provider import LogNotificationProvider, NotificationMessage, NotificationProvider


class NotificationCenter:
    """Route notifications to configured providers."""

    SUPPORTED_EVENTS = {
        "BuildComplete", "GitPush", "TaskFailed", "TaskFinished",
        "DailyReport", "HealthAlert",
    }

    def __init__(self, providers: list[NotificationProvider] | None = None) -> None:
        self.providers = providers or [LogNotificationProvider()]
        self._subscriptions: dict[str, list[str]] = defaultdict(list)
        self._lock = threading.RLock()

    def subscribe(self, event_type: str, provider_name: str) -> None:
        """Subscribe a provider to an event type."""
        with self._lock:
            if provider_name not in self._subscriptions[event_type]:
                self._subscriptions[event_type].append(provider_name)

    def notify(self, message: NotificationMessage) -> dict[str, bool]:
        """Send a notification to matching providers."""
        with self._lock:
            provider_names = self._subscriptions.get(message.event_type) or [provider.name for provider in self.providers]
            providers = [provider for provider in self.providers if provider.name in provider_names]
        return {provider.name: provider.send(message) for provider in providers}
