"""Task routing for the JNAS AI Core orchestrator."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from .request import UserRequest


RoutePredicate = Callable[[UserRequest], bool]


@dataclass(frozen=True)
class RoutedTask:
    """A user request classified for execution by the orchestrator."""

    task_type: str
    request: UserRequest
    payload: dict[str, Any] = field(default_factory=dict)


class TaskRouter:
    """Classifies user requests into supported orchestrator task types."""

    CODE_GENERATION = "code_generation"
    BUILDER = "builder"
    CHAT = "chat"
    UNKNOWN = "unknown"

    def __init__(self) -> None:
        self._routes: list[tuple[str, RoutePredicate]] = []
        self.register_route(self.BUILDER, self._is_builder_request)
        self.register_route(self.CODE_GENERATION, self._is_code_generation_request)
        self.register_route(self.CHAT, self._is_chat_request)

    def register_route(self, task_type: str, predicate: RoutePredicate) -> None:
        """Register a route predicate for future extension."""
        if not task_type:
            raise ValueError("task_type must be a non-empty string.")
        self._routes.append((task_type, predicate))

    def route(self, request: UserRequest) -> RoutedTask:
        """Return a routed task for the supplied request."""
        for task_type, predicate in self._routes:
            if predicate(request):
                return RoutedTask(
                    task_type=task_type,
                    request=request,
                    payload=self._payload_for(task_type, request),
                )
        return RoutedTask(task_type=self.UNKNOWN, request=request)

    def _payload_for(self, task_type: str, request: UserRequest) -> dict[str, Any]:
        if task_type == self.BUILDER:
            return {"module_name": self._extract_module_name(request)}
        return {}

    def _is_builder_request(self, request: UserRequest) -> bool:
        if request.metadata.get("task_type") == self.BUILDER:
            return True

        text = request.user_input.lower()

        keywords = [
            "create worker",
            "build worker",
            "build telegram",
            "telegram worker",
            "make worker",
            "make ",
            "create analyzer",
            "pdf analyzer",
            "create module",
            "build module",
            "browser automation",
            "develop",
            "implement",
        ]

        return any(keyword in text for keyword in keywords)

    def _is_code_generation_request(self, request: UserRequest) -> bool:
        if request.metadata.get("task_type") == self.CODE_GENERATION:
            return True
        text = request.user_input.strip().lower()
        markers = ("generate code", "write code", "create code", "python code")
        return any(marker in text for marker in markers)

    def _is_chat_request(self, request: UserRequest) -> bool:
        if request.metadata.get("task_type") == self.CHAT:
            return True

        return True

    def _extract_module_name(self, request: UserRequest) -> str:
        metadata_module = request.metadata.get("module_name")

        if metadata_module:
            return str(metadata_module)

        text = request.user_input.lower()

        replacements = [
            "create a ",
            "create ",
            "build a ",
            "build ",
            "make a ",
            "make ",
            "worker",
            "module",
            "service",
            "application",
        ]

        for item in replacements:
            text = text.replace(item, "")

        name = "_".join(
            text.strip().split()
        )

        if not name:
            return "generated_module"

        return name

