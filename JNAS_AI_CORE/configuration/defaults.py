"""Default configuration values."""

from __future__ import annotations


DEFAULT_CONFIG = {
    "retry": {"max_retries": 5, "backoff": 2},
    "logging": {"level": "INFO"},
    "executor": {"mode": "sequential"},
    "planner": {"strategy": "development"},
}
