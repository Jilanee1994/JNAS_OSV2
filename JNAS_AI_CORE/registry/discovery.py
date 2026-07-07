"""Package discovery for registry-compatible tools."""

from __future__ import annotations

import importlib
import logging
import pkgutil
from types import ModuleType
from typing import Iterable

from .exceptions import ToolDiscoveryError
from .interfaces import BaseTool


class ToolDiscovery:
    """Discover tools from registered packages."""

    def __init__(self, logger: logging.Logger | None = None) -> None:
        self.logger = logger or logging.getLogger(__name__)

    def discover(self, package_names: Iterable[str]) -> list[BaseTool]:
        """Discover tools from packages without registry code changes."""
        tools = []
        for package_name in package_names:
            tools.extend(self._discover_package(package_name))
        return tools

    def _discover_package(self, package_name: str) -> list[BaseTool]:
        try:
            package = importlib.import_module(package_name)
        except ImportError as exc:
            raise ToolDiscoveryError(f"Unable to import tool package: {package_name}") from exc

        modules = [package]
        package_path = getattr(package, "__path__", None)
        if package_path is not None:
            prefix = f"{package.__name__}."
            for module_info in pkgutil.iter_modules(package_path, prefix):
                modules.append(importlib.import_module(module_info.name))

        discovered = []
        for module in modules:
            discovered.extend(self._tools_from_module(module))
        return discovered

    def _tools_from_module(self, module: ModuleType) -> list[BaseTool]:
        factory = getattr(module, "get_tools", None)
        if callable(factory):
            result = factory()
            return list(result)

        tool = getattr(module, "TOOL", None)
        if tool is not None:
            return [tool]

        tool_class = getattr(module, "Tool", None)
        if isinstance(tool_class, type):
            return [tool_class()]

        return []
