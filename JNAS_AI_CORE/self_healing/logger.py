"""Logging helper for self-healing."""

from __future__ import annotations

import logging


def get_self_healing_logger(name: str = "JNAS_AI_CORE.self_healing") -> logging.Logger:
    """Return a configured self-healing logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        )
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger
