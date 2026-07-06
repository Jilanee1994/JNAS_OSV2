"""Central AI orchestrator for JNAS AI Core."""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any

from .interfaces import BaseWorker, WorkerResult
from .registry_adapter import RegistryAdapter
from .request import UserRequest
from .response import ExecutionResponse
from .router import RoutedTask, TaskRouter

try:
    from JNAS_AI_CORE.agent.code_agent import CodeAgent
    from JNAS_AI_CORE.Builder import BuilderEngine
    from JNAS_AI_CORE.llm.manager import LLMManager
except ImportError:
    from agent.code_agent import CodeAgent
    from Builder import BuilderEngine
    from llm.manager import LLMManager


class AIOrchestrator:
    """Coordinates existing JNAS AI Core components."""

    def __init__(
        self,
        code_agent: Any | None = None,
        llm_manager: Any | None = None,
        builder_engine: Any | None = None,
        router: TaskRouter | None = None,
        workers: dict[str, BaseWorker] | None = None,
        registry_adapter: RegistryAdapter | None = None,
        project_root: Path | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self.code_agent = code_agent
        self.llm_manager = llm_manager
        self.builder_engine = builder_engine
        self.router = router or TaskRouter()
        self.workers: dict[str, BaseWorker] = dict(workers or {})
        self.registry_adapter = registry_adapter
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.logger = logger or logging.getLogger(__name__)
        self.initialized = False

    def initialize(self) -> None:
        """Initialize missing dependencies using existing project classes."""
        if self.initialized:
            return

        self.llm_manager = self.llm_manager or LLMManager()
        self.code_agent = self.code_agent or CodeAgent()
        self.builder_engine = self.builder_engine or BuilderEngine(
            project_root=self.project_root,
            llm_manager=self.llm_manager,
        )
        self._register_default_workers()
        self.initialized = True
        self.logger.info("AIOrchestrator initialized.")

    def register_worker(self, worker: BaseWorker) -> None:
        """Register or replace a worker for a routed task type."""
        if not worker.task_type:
            raise ValueError("worker.task_type must be a non-empty string.")
        self.workers[worker.task_type] = worker

    def handle_request(
        self,
        user_input: str,
        metadata: dict[str, Any] | None = None,
    ) -> ExecutionResponse:
        """Normalize, route, and execute a user request."""
        self.initialize()
        request = UserRequest(user_input=user_input, metadata=metadata or {})
        task = self.route_task(request)
        return self.execute(task)

    def route_task(self, task: UserRequest | str) -> RoutedTask:
        """Route a raw string or normalized request to a supported task type."""
        request = task if isinstance(task, UserRequest) else UserRequest(user_input=task)
        routed_task = self.router.route(request)
        self.logger.debug(
            "Request %s routed to %s.",
            request.request_id,
            routed_task.task_type,
        )
        return routed_task

    def execute(self, task: RoutedTask) -> ExecutionResponse:
        """Execute a routed task through the appropriate existing component."""
        if not self.initialized:
            raise RuntimeError("AIOrchestrator must be initialized before execution.")

        started = time.perf_counter()
        try:
            return self._execute_routed_task(task, started)
        except Exception as exc:
            self.logger.exception("Task execution failed.")
            return self._response(
                success=False,
                message="Task execution failed.",
                started=started,
                errors=[str(exc)],
            )

    def shutdown(self) -> None:
        """Release orchestrator references to runtime components."""
        self.code_agent = None
        self.llm_manager = None
        self.builder_engine = None
        self.workers.clear()
        self.initialized = False
        self.logger.info("AIOrchestrator shut down.")

    def _execute_routed_task(
        self,
        task: RoutedTask,
        started: float,
    ) -> ExecutionResponse:
        worker = self._resolve_worker(task.task_type)
        if worker is None:
            return self._response(
                success=False,
                message="Unknown task type.",
                started=started,
                errors=[f"Unsupported task type: {task.task_type}"],
            )

        result = worker.execute(task)
        return self._response(
            success=result.success,
            message=result.message,
            started=started,
            result=result.result,
            errors=result.errors,
        )

    def _resolve_worker(self, task_type: str) -> BaseWorker | None:
        if self.registry_adapter is not None:
            worker = self.registry_adapter.resolve_worker(task_type)
            if worker is not None:
                return worker
        return self.workers.get(task_type)

    def _register_default_workers(self) -> None:
        if TaskRouter.CODE_GENERATION not in self.workers:
            self.register_worker(CodeAgentWorker(self.code_agent))
        if TaskRouter.BUILDER not in self.workers:
            self.register_worker(BuilderWorker(self.builder_engine))
        if TaskRouter.CHAT not in self.workers:
            self.register_worker(LLMWorker(self.llm_manager))

    def _response(
        self,
        success: bool,
        message: str,
        started: float,
        result: Any = None,
        errors: list[str] | None = None,
    ) -> ExecutionResponse:
        return ExecutionResponse(
            success=success,
            message=message,
            result=result,
            execution_time=time.perf_counter() - started,
            errors=errors or [],
        )


class CodeAgentWorker:
    """Worker adapter for the existing CodeAgent."""

    task_type = TaskRouter.CODE_GENERATION

    def __init__(self, code_agent: Any) -> None:
        self.code_agent = code_agent

    def execute(self, task: RoutedTask) -> WorkerResult:
        result = self.code_agent.generate_code(task.request.user_input)
        return WorkerResult(
            success=True,
            message="Code generation completed.",
            result=result,
        )


class BuilderWorker:
    """Worker adapter for the existing Builder Engine."""

    task_type = TaskRouter.BUILDER

    def __init__(self, builder_engine: Any) -> None:
        self.builder_engine = builder_engine

    def execute(self, task: RoutedTask) -> WorkerResult:
        module_name = task.payload.get("module_name")
        if not module_name:
            raise ValueError("Builder task requires a module_name payload.")
        result = self.builder_engine.build(module_name)
        return WorkerResult(
            success=True,
            message="Builder task completed.",
            result=result,
        )


class LLMWorker:
    """Worker adapter for the existing LLMManager."""

    task_type = TaskRouter.CHAT

    def __init__(self, llm_manager: Any) -> None:
        self.llm_manager = llm_manager

    def execute(self, task: RoutedTask) -> WorkerResult:
        result = self.llm_manager.generate(task.request.user_input)
        return WorkerResult(
            success=True,
            message="Chat response generated.",
            result=result,
        )
