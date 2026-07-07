# Core V2 Architecture Review

Repository: `JNAS_OSV2`
Project: `JNAS_AI_CORE`
Review date: 2026-07-06

## Current Architecture

The project now has a layered AI core:

```text
AIOrchestrator -> TaskRouter / RegistryAdapter / ToolRegistry
Planner -> ExecutionPlan / Task / StrategyEngine
Executor -> ExecutionPipeline / TaskExecutor / MemoryManager
Self-Healing -> FailureAnalyzer / RecoveryPolicy / CodePatcher / MemoryManager
MemoryManager -> JSON MemoryStore
Builder / CodeAgent / LLMManager / FileTool / ProjectScanner
```

The design already supports incremental infrastructure additions through dependency injection and adapters.

## Integration Points

### Event Bus

Best integration points:

- Executor task lifecycle: `TaskStarted`, `TaskFinished`, `TaskFailed`, `ExecutionCompleted`.
- Self-Healing lifecycle: `RecoveryStarted`, `RecoveryFinished`, `PatchApplied`.
- MemoryManager writes: `MemorySaved`.
- ToolRegistry lifecycle: `ToolRegistered`.
- Planner completion: `PlannerFinished`.

Minimal approach: add an independent event package now. Existing modules can accept an injected bus later without breaking current constructors.

### Configuration Manager

Best integration points:

- Retry policy values for Self-Healing.
- Executor mode.
- Planner default strategy.
- Logging level.
- Registry package discovery list.

Minimal approach: add a manager that merges defaults, project file, environment variables, and user overrides. Existing modules can consume values later through optional constructor args.

### Permission System

Best integration points:

- FileTool write/delete operations.
- CodePatcher patch application.
- ToolRegistry tools in filesystem/network/docker/browser categories.
- Executor workers with side effects.

Minimal approach: add permission and policy primitives now. Enforce in future adapters before sensitive operations.

### Metrics Engine

Best integration points:

- Event subscribers can increment counters.
- Executor can record task durations.
- Self-Healing can record recovery success rate and retries.
- ToolRegistry can record tool usage.
- MemoryManager can record memory reads/writes.

Minimal approach: add collector/storage/reporter now. Existing modules can emit events or call collector later.

## Possible Risks

- Adding direct dependencies from every module to new services would create coupling.
- Synchronous event handlers could slow execution if subscribers do heavy work.
- Configuration precedence can become confusing without a clear hierarchy.
- Permission checks must fail closed for protected files.
- Metrics can grow unbounded without storage policy.

## Compatibility Concerns

- Existing constructors should remain valid.
- Existing behavior must not require config files.
- Missing event bus or metrics collector must not break current execution.
- Permission system should be opt-in until sensitive tools are migrated.

## Required Minimal Changes

For this V2 increment:

- Add standalone packages: `events`, `configuration`, `security`, `metrics`.
- Use dataclasses, protocols, validators, and storage abstractions.
- Avoid modifying current Builder, Orchestrator, Planner, Executor, Memory, Registry, and Self-Healing behavior.
- Provide tests and reports.

## Conclusion

The correct V2 path is additive. Build shared infrastructure now, then wire existing modules into it gradually through dependency injection, event subscribers, and registry/security adapters.
