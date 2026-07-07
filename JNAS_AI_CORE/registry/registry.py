"""Dynamic Tool Registry implementation."""

from __future__ import annotations

import logging
from collections import defaultdict
from typing import Iterable

from .exceptions import ToolNotFound, ToolRegistrationError
from .interfaces import BaseTool
from .loader import ToolLoader
from .metadata import ToolMetadata
from .tool import RegisteredTool
from .validator import ToolRegistryValidator


class ToolRegistry:
    """Registry for scalable tool registration, lookup, and discovery."""

    def __init__(
        self,
        loader: ToolLoader | None = None,
        validator: ToolRegistryValidator | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self.loader = loader or ToolLoader()
        self.validator = validator or ToolRegistryValidator()
        self.logger = logger or logging.getLogger(__name__)
        self._tools: dict[str, RegisteredTool] = {}
        self._category_index: dict[str, set[str]] = defaultdict(set)
        self._task_index: dict[str, set[str]] = defaultdict(set)
        self._packages: list[str] = []

    def register_tool(self, tool: BaseTool) -> RegisteredTool:
        """Register a validated tool."""
        self.validator.validate_tool(tool)
        metadata = tool.metadata
        if metadata.tool_id in self._tools:
            raise ToolRegistrationError(f"Duplicate tool ID: {metadata.tool_id}")

        tool.initialize()
        registered = RegisteredTool(tool=tool, metadata=metadata)
        self._tools[metadata.tool_id] = registered
        self._index_tool(metadata)
        self.logger.info("Registered tool %s.", metadata.tool_id)
        return registered

    def unregister_tool(self, tool_id: str) -> None:
        """Unregister a tool by ID."""
        registered = self._tools.pop(tool_id, None)
        if registered is None:
            raise ToolNotFound(f"Tool not found: {tool_id}")
        registered.tool.shutdown()
        self._remove_indexes(registered.metadata)
        self.logger.info("Unregistered tool %s.", tool_id)

    def get_tool(self, tool_id: str) -> BaseTool:
        """Return a registered tool by ID."""
        try:
            return self._tools[tool_id].tool
        except KeyError as exc:
            raise ToolNotFound(f"Tool not found: {tool_id}") from exc

    def list_tools(self, include_disabled: bool = False) -> list[RegisteredTool]:
        """List registered tools, sorted by priority and name."""
        tools = [
            tool
            for tool in self._tools.values()
            if include_disabled or tool.metadata.enabled
        ]
        return sorted(tools, key=lambda item: (item.metadata.priority, item.metadata.name))

    def find_tools_by_category(
        self,
        category: str,
        include_disabled: bool = False,
    ) -> list[RegisteredTool]:
        """Find tools by category."""
        return self._find_by_index(self._category_index, category, include_disabled)

    def find_tools_by_task(
        self,
        task: str,
        include_disabled: bool = False,
    ) -> list[RegisteredTool]:
        """Find tools that support a task."""
        return self._find_by_index(self._task_index, task, include_disabled)

    def validate_registry(self) -> bool:
        """Validate all registered tools."""
        return self.validator.validate_registry(
            {tool_id: registered.tool for tool_id, registered in self._tools.items()}
        )

    def reload_tools(self) -> None:
        """Reload tools from previously registered discovery packages."""
        current_ids = list(self._tools)
        for tool_id in current_ids:
            self.unregister_tool(tool_id)
        self.load_packages(self._packages)

    def load_packages(self, package_names: Iterable[str]) -> list[RegisteredTool]:
        """Discover and register tools from packages."""
        packages = list(package_names)
        for package in packages:
            if package not in self._packages:
                self._packages.append(package)
        registered = []
        for tool in self.loader.load(packages):
            registered.append(self.register_tool(tool))
        return registered

    def set_enabled(self, tool_id: str, enabled: bool) -> None:
        """Enable or disable a registered tool."""
        registered = self._tools.get(tool_id)
        if registered is None:
            raise ToolNotFound(f"Tool not found: {tool_id}")
        registered.metadata.enabled = enabled

    def _find_by_index(
        self,
        index: dict[str, set[str]],
        key: str,
        include_disabled: bool,
    ) -> list[RegisteredTool]:
        ids = index.get(key, set())
        tools = [self._tools[tool_id] for tool_id in ids if tool_id in self._tools]
        if not include_disabled:
            tools = [tool for tool in tools if tool.metadata.enabled]
        return sorted(tools, key=lambda item: (item.metadata.priority, item.metadata.name))

    def _index_tool(self, metadata: ToolMetadata) -> None:
        self._category_index[metadata.category].add(metadata.tool_id)
        for task in metadata.supported_tasks:
            self._task_index[task].add(metadata.tool_id)

    def _remove_indexes(self, metadata: ToolMetadata) -> None:
        self._category_index[metadata.category].discard(metadata.tool_id)
        for task in metadata.supported_tasks:
            self._task_index[task].discard(metadata.tool_id)
