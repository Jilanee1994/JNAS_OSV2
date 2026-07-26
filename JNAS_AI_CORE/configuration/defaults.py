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
    "code_generation": {
        "ollama_host": "http://127.0.0.1:11434",
        "model": "qwen2.5:7b",
        "timeout": 300,
        "max_retries": 3,
        "output_dir": "JNAS_AI_CORE/workspace/generated",
    },
    "ml": {
        "model_storage_dir": "JNAS_AI_CORE/workspace/models",
        "default_algorithm": "decision_tree",
        "test_size": 0.2,
        "random_state": 42,
    },
    "ai_os": {
        "queue_path": "JNAS_AI_CORE/workspace/task_queue/queue.json",
        "scheduler_path": "JNAS_AI_CORE/workspace/scheduler/jobs.json",
        "learning_path": "JNAS_AI_CORE/workspace/learning/history.json",
        "daily_report_path": "DAILY_REPORT.md",
    },
    "llm_router": {
         "providers": [
        {
            "name": "ollama",
            "endpoint": "http://127.0.0.1:11434/api/generate",
            "model": "qwen2.5:7b",
            "capabilities": ["general", "coding", "analysis"],
            "response_field": "response",
            "enabled": True,
        },
        {
            "name": "gemini",
            "endpoint": "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
            "model": "gemini-2.0-flash",
            "capabilities": ["general", "coding", "analysis"],
            "response_field": "text",
            "enabled": False,
        },
        {
            "name": "groq",
            "endpoint": "https://api.groq.com/openai/v1/chat/completions",
            "model": "llama-3.1-8b-instant",
            "capabilities": ["general", "coding", "analysis"],
            "response_field": "text",
            "enabled": False,
        },
        {
            "name": "openrouter",
            "endpoint": "https://openrouter.ai/api/v1/chat/completions",
            "model": "openai/gpt-4o-mini",
            "capabilities": ["general", "coding", "analysis"],
            "response_field": "text",
            "enabled": False,
        },
      ]
    },
    "builder_v3": {
        "workspace": "workspace/generated_projects",
        "max_retries": 3,
        "provider_priority": ["gemini", "groq", "openrouter", "ollama"],
    },
}
