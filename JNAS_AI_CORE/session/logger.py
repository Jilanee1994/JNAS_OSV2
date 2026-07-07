"""Session logger helper."""

from __future__ import annotations

import logging


def get_session_logger(level: str | int = "INFO") -> logging.Logger:
    """Return a configured session logger."""
    logger = logging.getLogger("JNAS_AI_CORE.session")
    logger.setLevel(level if isinstance(level, int) else getattr(logging, level.upper(), logging.INFO))
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
        )
        logger.addHandler(handler)
    logger.propagate = False
    return logger
