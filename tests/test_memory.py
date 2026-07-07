"""Tests for the JSON-backed memory manager."""

from __future__ import annotations

import pytest

from JNAS_AI_CORE.memory import MemoryManager, MemoryNotFound


def test_save_memory(tmp_path) -> None:
    manager = MemoryManager(storage_dir=tmp_path)

    entry = manager.save_memory("user.name", "JNAS")

    assert entry.key == "user.name"
    assert entry.value == "JNAS"
    assert len(list(tmp_path.glob("*.json"))) == 1


def test_load_memory(tmp_path) -> None:
    manager = MemoryManager(storage_dir=tmp_path)
    manager.save_memory("project", {"name": "JNAS"})

    entry = manager.load_memory("project")

    assert entry.value == {"name": "JNAS"}


def test_delete_memory(tmp_path) -> None:
    manager = MemoryManager(storage_dir=tmp_path)
    manager.save_memory("delete.me", "value")

    manager.delete_memory("delete.me")

    with pytest.raises(MemoryNotFound):
        manager.load_memory("delete.me")


def test_search_memory(tmp_path) -> None:
    manager = MemoryManager(storage_dir=tmp_path)
    manager.save_memory("alpha", "first customer", tags=["crm"])
    manager.save_memory("beta", "second record", tags=["sales"])

    results = manager.search_memory("customer")

    assert [entry.key for entry in results] == ["alpha"]


def test_list_memories(tmp_path) -> None:
    manager = MemoryManager(storage_dir=tmp_path)
    manager.save_memory("one", 1)
    manager.save_memory("two", 2)

    entries = manager.list_memories()

    assert {entry.key for entry in entries} == {"one", "two"}


def test_clear_memory(tmp_path) -> None:
    manager = MemoryManager(storage_dir=tmp_path)
    manager.save_memory("one", 1)
    manager.save_memory("two", 2)

    manager.clear_memory()

    assert manager.list_memories() == []


def test_missing_key_exception(tmp_path) -> None:
    manager = MemoryManager(storage_dir=tmp_path)

    with pytest.raises(MemoryNotFound):
        manager.load_memory("missing")
