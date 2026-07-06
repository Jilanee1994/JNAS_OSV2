"""Logging helpers for the execution engine."""

from __future__ import annotations

import logging


def get_executor_logger(name: str = "JNAS_AI_CORE.executor") -> logging.Logger:
    """Return a configured executor logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        )
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger
