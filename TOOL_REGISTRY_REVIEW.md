# Tool Registry Architecture Review

Repository: `JNAS_OSV2`
Project: `JNAS_AI_CORE`
Review date: 2026-07-06

## Current Architecture

`JNAS_AI_CORE` currently has a modular but early-stage AI core:

```text
AIOrchestrator
  -> TaskRouter
  -> BaseWorker / WorkerResult
  -> CodeAgent / BuilderEngine / LLMManager wrappers

Planner
  -> StrategyEngine
  -> ExecutionPlan / Task
  -> PlanValidator

Executor
  -> ExecutionPlan
  -> ExecutionValidator
  -> ExecutionPipeline
  -> TaskExecutor
  -> TaskWorker
  -> MemoryManager

MemoryManager
  -> MemoryStore
  -> MemorySerializer
  -> JSON files under workspace/memory

Tools
  -> FileTool
  -> ProjectScanner
  -> ProjectReader
```

The system already has useful extension points:

- `AIOrchestrator.register_worker()`
- `TaskRouter.register_route()`
- `Planner.StrategyEngine.register_strategy()`
- `Executor.register_execution_mode()`
- `TaskExecutor.register_worker()`
- `ExecutionPipeline` hooks

The missing piece is a shared registry layer that gives tools and future AI workers consistent metadata, validation, lookup, lifecycle, discovery, and indexing.

## Recommendations

| Priority | Recommendation | Why It Matters | Timing |
| --- | --- | --- | --- |
| High | Add a dedicated Tool Registry with metadata, validation, lifecycle methods, and indexed lookup. | Scaling to 500 tools requires O(1) lookup by ID and predictable discovery by task/category. Without this, routing will become scattered across orchestrator, executor, and tool modules. | BEFORE Tool Registry |
| High | Define a `BaseTool` protocol with `initialize()`, `execute()`, `validate()`, and `shutdown()`. | Tools need a stable contract independent of specific modules. This prevents each subsystem from inventing its own tool shape. | BEFORE Tool Registry |
| High | Require structured `ToolMetadata` for every tool. | Metadata enables discovery, enable/disable behavior, task matching, category grouping, priority sorting, and future UI/API exposure. | BEFORE Tool Registry |
| High | Prevent duplicate tool IDs at registration time. | Duplicate IDs become dangerous at scale because routing may silently select the wrong tool. | BEFORE Tool Registry |
| High | Keep registry separate from AI provider logic. | Tools should not imply Ollama, LLMManager, or any provider. AI decisions remain in Orchestrator/Planner; tool execution remains in Executor/workers. | BEFORE Tool Registry |
| High | Add package-based discovery instead of hardcoded imports. | New tools should be added by package/module registration, not by modifying registry source. | BEFORE Tool Registry |
| Medium | Add internal indexes for category and supported task lookup. | Linear scans across 500 tools are acceptable today but become noisy and slow as task matching grows. Indexes keep the API simple and scalable. | BEFORE Tool Registry |
| Medium | Support enable/disable state in metadata and search results. | Operators need to disable unsafe or experimental tools without deleting code. | BEFORE Tool Registry |
| Medium | Add a registry validator class rather than embedding all checks in `ToolRegistry`. | Keeps registration small and lets validation evolve independently. | BEFORE Tool Registry |
| Medium | Add lifecycle calls during registration/unregistration/reload. | Tools with external resources need predictable startup/shutdown behavior. | AFTER Tool Registry |
| Medium | Introduce optional tool permissions/capabilities later. | Filesystem, browser, git, docker, OCR, and communication tools need security boundaries before production exposure. | AFTER Tool Registry |
| Medium | Add registry-level audit logging. | Registration, unregistration, reload, and failed validation should be traceable in production. | BEFORE Tool Registry |
| Medium | Normalize errors with custom registry exceptions. | Callers need to distinguish duplicate registration, missing tools, bad metadata, bad implementation, and discovery failures. | BEFORE Tool Registry |
| Low | Add persistence for enabled/disabled tool state. | Useful for production operations, but not required for the first in-process registry. | AFTER Tool Registry |
| Low | Add asynchronous execution support. | Some future tools may be async, but the current project is synchronous. Support can be added through adapters later. | AFTER Tool Registry |
| Low | Add dependency/version compatibility checks between tools. | Helpful when tool count grows, but not required for initial registry correctness. | AFTER Tool Registry |

## Architectural Weaknesses

1. `AIOrchestrator` still owns default worker wiring for `CodeAgent`, Builder, and LLM chat.
2. Tools do not share a common metadata model.
3. `TaskExecutor` has a worker registry, but no metadata or discovery.
4. Existing `FileTool`, `ProjectScanner`, and `ProjectReader` do not implement a shared interface.
5. Route selection and worker selection are separate concepts with no global capability index.
6. There is no central place to ask, "Which tool supports this task?"

## Tight Coupling

- `AIOrchestrator.initialize()` imports concrete default classes.
- Builder auto-wiring imports specific modules by string.
- Executor task workers are local to `TaskExecutor`.
- Existing tools are plain classes with different method names and no lifecycle contract.

These are manageable today, but for 100+ workers they will create routing and maintenance pressure.

## Missing Abstractions

Recommended abstractions:

- `ToolMetadata`
- `BaseTool`
- `ToolRegistry`
- `ToolRegistryValidator`
- `ToolDiscovery`
- `ToolLoader`

These should be added without replacing existing modules.

## Duplicate Responsibilities

- Worker registration exists in both `AIOrchestrator` and `TaskExecutor`.
- Validation patterns exist separately in Planner, Executor, Memory, and future Registry.
- Logging setup is repeated in several modules.

The registry should not consolidate all of these yet, but it should stop new tool metadata/validation duplication.

## Interfaces To Improve

| Interface | Improvement |
| --- | --- |
| `BaseWorker` | Eventually add metadata or capability descriptors. |
| `TaskRouter` | Eventually support registry-backed routing hints. |
| `TaskExecutor` | Eventually select workers/tools using registry metadata. |
| Existing tools | Add adapters or native `BaseTool` implementations over time. |

## Missing Extension Points

- Tool discovery from packages.
- Tool category/task indexes.
- Enable/disable filtering.
- Tool lifecycle initialization/shutdown.
- Validation before registration.
- Reload mechanism for discovered tool packages.

## Scalability Issues

For 500 tools and 100 AI workers:

- Hardcoded imports will not scale.
- Linear scans without indexes will make lookup logic sprawl.
- Missing metadata will prevent automated routing.
- No central validation means broken tools can fail at runtime.
- No lifecycle boundaries can leak resources.

## Performance Bottlenecks

Likely future bottlenecks:

- Repeated linear search over all tools.
- Repeated import/discovery of the same packages.
- Heavy tool initialization at startup.
- JSON memory storage for high-volume execution logs.

Initial registry should use in-memory indexes and avoid initializing undiscovered packages repeatedly.

## Security And Reliability Concerns

Future high-risk tool categories include:

```text
filesystem
browser
git
docker
ocr
pdf
vision
automation
communication
```

Concerns:

- Filesystem path traversal.
- Shell/process execution.
- External network calls.
- Credential leakage.
- Unsafe browser automation.
- Tool registration from untrusted packages.

The first registry should validate structure and metadata. Permission enforcement can follow after the registry contract exists.

## Fix Before Tool Registry

Must be handled in this implementation:

- Add `ToolMetadata`.
- Add `BaseTool`.
- Add duplicate ID prevention.
- Add metadata validation.
- Add implementation validation.
- Add package discovery.
- Add category/task indexes.
- Add registry-specific exceptions.
- Add logging for registration and unregistration.

## Fix After Tool Registry

Defer until the registry contract exists:

- Full orchestrator routing through registry.
- Tool permissions and sandbox policy.
- Async tool execution.
- Persistent registry state.
- Tool version compatibility checks.
- Production audit log storage.
- UI/API listing of tools.

## Conclusion

The current architecture should not be redesigned. The right next step is to add a Tool Registry as a separate extension layer that existing and future tools can adopt incrementally.

The registry should be designed around metadata, protocol validation, indexed lookup, package discovery, and lifecycle hooks. This gives the system enough structure to support hundreds of tools and many workers without forcing an immediate rewrite of Orchestrator, Planner, Executor, Memory, Builder, or CodeAgent.
