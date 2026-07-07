"""Event logging helpers."""

from __future__ import annotations

import logging


def get_event_logger() -> logging.Logger:
    """Return the event logger."""
    return logging.getLogger("JNAS_AI_CORE.events")
