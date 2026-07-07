"""Tests for the dynamic Tool Registry."""

from __future__ import annotations

import sys
import types

import pytest

from JNAS_AI_CORE.registry import (
    ToolMetadata,
    ToolNotFound,
    ToolRegistrationError,
    ToolRegistry,
)


class ExampleTool:
    def __init__(self, tool_id: str = "example.tool", enabled: bool = True) -> None:
        self.initialized = False
        self.shutdown_called = False
        self.metadata = ToolMetadata(
            tool_id=tool_id,
            name="Example Tool",
            description="Example registry tool.",
            version="1.0.0",
            author="JNAS",
            category="code",
            supported_tasks=["generate", "test"],
            input_types=["text"],
            output_types=["text"],
            enabled=enabled,
            priority=10,
        )

    def initialize(self) -> None:
        self.initialized = True

    def execute(self, payload):
        return payload

    def validate(self) -> bool:
        return True

    def shutdown(self) -> None:
        self.shutdown_called = True


def test_tool_registration() -> None:
    registry = ToolRegistry()
    tool = ExampleTool()

    registered = registry.register_tool(tool)

    assert registered.tool_id == "example.tool"
    assert tool.initialized is True


def test_duplicate_detection() -> None:
    registry = ToolRegistry()
    registry.register_tool(ExampleTool())

    with pytest.raises(ToolRegistrationError):
        registry.register_tool(ExampleTool())


def test_lookup() -> None:
    registry = ToolRegistry()
    tool = ExampleTool()
    registry.register_tool(tool)

    assert registry.get_tool("example.tool") is tool
    with pytest.raises(ToolNotFound):
        registry.get_tool("missing")


def test_discovery() -> None:
    module = types.ModuleType("dynamic_test_tools")
    module.get_tools = lambda: [ExampleTool("dynamic.tool")]
    sys.modules[module.__name__] = module
    registry = ToolRegistry()

    registered = registry.load_packages(["dynamic_test_tools"])

    assert registered[0].tool_id == "dynamic.tool"
    assert registry.get_tool("dynamic.tool").metadata.name == "Example Tool"


def test_validation() -> None:
    registry = ToolRegistry()
    registry.register_tool(ExampleTool())

    assert registry.validate_registry() is True


def test_enable_disable() -> None:
    registry = ToolRegistry()
    registry.register_tool(ExampleTool())

    registry.set_enabled("example.tool", False)

    assert registry.list_tools() == []
    assert len(registry.list_tools(include_disabled=True)) == 1


def test_category_search() -> None:
    registry = ToolRegistry()
    registry.register_tool(ExampleTool())

    results = registry.find_tools_by_category("code")

    assert [tool.tool_id for tool in results] == ["example.tool"]


def test_task_search() -> None:
    registry = ToolRegistry()
    registry.register_tool(ExampleTool())

    results = registry.find_tools_by_task("generate")

    assert [tool.tool_id for tool in results] == ["example.tool"]
