"""Lightweight configuration schema."""

from __future__ import annotations


CONFIG_SCHEMA = {
    "retry.max_retries": int,
    "retry.backoff": (int, float),
    "logging.level": str,
    "executor.mode": str,
    "planner.strategy": str,
}
