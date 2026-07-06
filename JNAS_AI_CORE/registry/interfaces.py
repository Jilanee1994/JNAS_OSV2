"""Tool interfaces."""

from __future__ import annotations

from typing import Any, Protocol

from .metadata import ToolMetadata


class BaseTool(Protocol):
    """Protocol implemented by registry-compatible tools."""

    metadata: ToolMetadata

    def initialize(self) -> None:
        """Prepare the tool for execution."""

    def execute(self, payload: Any) -> Any:
        """Execute the tool with a payload."""

    def validate(self) -> bool:
        """Validate tool readiness."""

    def shutdown(self) -> None:
        """Release tool resources."""
