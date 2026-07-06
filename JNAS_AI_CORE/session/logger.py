"""Session logger helper."""

from __future__ import annotations

import logging


def get_session_logger() -> logging.Logger:
    """Return session logger."""
    return logging.getLogger("JNAS_AI_CORE.session")
