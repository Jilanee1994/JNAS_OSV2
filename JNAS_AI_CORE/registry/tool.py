"""Registered tool wrapper."""

from __future__ import annotations

from dataclasses import dataclass

from .interfaces import BaseTool
from .metadata import ToolMetadata


@dataclass
class RegisteredTool:
    """A validated tool and its metadata."""

    tool: BaseTool
    metadata: ToolMetadata

    @property
    def tool_id(self) -> str:
        """Return the unique tool ID."""
        return self.metadata.tool_id
