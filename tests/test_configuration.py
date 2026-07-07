"""Tests for configuration manager."""

from __future__ import annotations

from JNAS_AI_CORE.configuration import ConfigManager


def test_configuration_hierarchy(tmp_path, monkeypatch) -> None:
    project = tmp_path / "project.json"
    user = tmp_path / "user.yaml"
    project.write_text('{"retry": {"max_retries": 3}}', encoding="utf-8")
    user.write_text("planner:\n  strategy: research\n", encoding="utf-8")
    monkeypatch.setenv("JNAS_LOGGING__LEVEL", "DEBUG")

    config = ConfigManager().load(project, user)

    assert config["retry"]["max_retries"] == 3
    assert config["logging"]["level"] == "DEBUG"
    assert config["planner"]["strategy"] == "research"


def test_get_value() -> None:
    manager = ConfigManager()

    assert manager.get("executor.mode") == "sequential"
