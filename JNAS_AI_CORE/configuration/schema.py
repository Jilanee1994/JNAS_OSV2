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
<<<<<<< HEAD
    "code_generation.ollama_host": str,
    "code_generation.model": str,
    "code_generation.timeout": int,
    "code_generation.max_retries": int,
    "code_generation.output_dir": str,
    "ml.model_storage_dir": str,
    "ml.default_algorithm": str,
    "ml.test_size": (int, float),
    "ml.random_state": int,
    "ai_os.queue_path": str,
    "ai_os.scheduler_path": str,
    "ai_os.learning_path": str,
    "ai_os.daily_report_path": str,
    "llm_router.providers": list,
=======
>>>>>>> d3aaca4f603cf5fe37898156986c9973ca77d20c
}
