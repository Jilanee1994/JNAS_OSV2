"""Tool metadata model."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ToolMetadata:
    """Describes a tool registered with the Tool Registry."""

    tool_id: str
    name: str
    description: str
    version: str
    author: str
    category: str
    supported_tasks: list[str]
    input_types: list[str]
    output_types: list[str]
    enabled: bool = True
    priority: int = 100
    extra: dict[str, str] = field(default_factory=dict)
