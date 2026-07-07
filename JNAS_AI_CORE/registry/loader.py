"""Tool package loading helpers."""

from __future__ import annotations

import logging
from typing import Iterable

from .discovery import ToolDiscovery
from .interfaces import BaseTool


class ToolLoader:
    """Loads registry-compatible tools from package names."""

    def __init__(
        self,
        discovery: ToolDiscovery | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self.logger = logger or logging.getLogger(__name__)
        self.discovery = discovery or ToolDiscovery(logger=self.logger)

    def load(self, package_names: Iterable[str]) -> list[BaseTool]:
        """Load tools from packages."""
        return self.discovery.discover(package_names)
