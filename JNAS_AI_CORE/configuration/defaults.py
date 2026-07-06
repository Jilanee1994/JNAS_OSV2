"""Default configuration values."""

from __future__ import annotations


DEFAULT_CONFIG = {
    "retry": {"max_retries": 5, "backoff": 2},
    "logging": {"level": "INFO"},
    "executor": {"mode": "sequential"},
    "planner": {"strategy": "development"},
    "session": {
        "storage_dir": "JNAS_AI_CORE/workspace/sessions",
        "retention_days": 30,
        "heartbeat_interval": 30,
        "lock_timeout": 10,
        "lock_poll_interval": 0.1,
    },
}
