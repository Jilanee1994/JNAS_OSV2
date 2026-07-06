"""Lightweight configuration schema."""

from __future__ import annotations


CONFIG_SCHEMA = {
    "retry.max_retries": int,
    "retry.backoff": (int, float),
    "logging.level": str,
    "executor.mode": str,
    "planner.strategy": str,
    "session.storage_dir": str,
    "session.retention_days": int,
    "session.heartbeat_interval": (int, float),
    "session.lock_timeout": (int, float),
    "session.lock_poll_interval": (int, float),
}
