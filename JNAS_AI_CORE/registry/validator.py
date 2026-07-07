"""Validation for registry tools and metadata."""

from __future__ import annotations

from typing import Any

from .exceptions import ToolValidationError
from .interfaces import BaseTool
from .metadata import ToolMetadata


class ToolRegistryValidator:
    """Validate tool metadata and interface implementation."""

    _REQUIRED_METHODS = ("initialize", "execute", "validate", "shutdown")

    def validate_tool(self, tool: BaseTool) -> bool:
        """Validate a tool object before registration."""
        metadata = getattr(tool, "metadata", None)
        if not isinstance(metadata, ToolMetadata):
            raise ToolValidationError("Tool must expose ToolMetadata as 'metadata'.")
        self.validate_metadata(metadata)
        self.validate_interface(tool)
        return True

    def validate_metadata(self, metadata: ToolMetadata) -> bool:
        """Validate required metadata fields."""
        required_strings = {
            "tool_id": metadata.tool_id,
            "name": metadata.name,
            "description": metadata.description,
            "version": metadata.version,
            "author": metadata.author,
            "category": metadata.category,
        }
        for field_name, value in required_strings.items():
            if not value or not str(value).strip():
                raise ToolValidationError(f"Tool metadata field is required: {field_name}")
        if not metadata.supported_tasks:
            raise ToolValidationError("Tool metadata requires supported_tasks.")
        if not metadata.input_types:
            raise ToolValidationError("Tool metadata requires input_types.")
        if not metadata.output_types:
            raise ToolValidationError("Tool metadata requires output_types.")
        if metadata.priority < 0:
            raise ToolValidationError("Tool metadata priority must be non-negative.")
        return True

    def validate_interface(self, tool: Any) -> bool:
        """Validate required callable methods exist."""
        for method_name in self._REQUIRED_METHODS:
            method = getattr(tool, method_name, None)
            if not callable(method):
                raise ToolValidationError(f"Tool missing method: {method_name}()")
        return True

    def validate_registry(self, tools: dict[str, BaseTool]) -> bool:
        """Validate all tools in a registry."""
        seen = set()
        for tool_id, tool in tools.items():
            self.validate_tool(tool)
            if tool_id in seen:
                raise ToolValidationError(f"Duplicate tool ID: {tool_id}")
            if tool.metadata.tool_id != tool_id:
                raise ToolValidationError(
                    f"Registry key {tool_id} does not match metadata ID {tool.metadata.tool_id}."
                )
            seen.add(tool_id)
        return True
