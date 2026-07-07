# Self-Healing Architecture Review

Repository: `JNAS_OSV2`
Project: `JNAS_AI_CORE`
Review date: 2026-07-06

## Current Strengths

- `AIOrchestrator` already has a worker interface and registry adapter path.
- `Planner` creates structured `ExecutionPlan` objects and does not execute work.
- `Executor` executes tasks and produces `ExecutionResult` records.
- `MemoryManager` provides reusable JSON-backed persistence.
- `ToolRegistry` gives the system a scalable metadata-driven way to locate tools.
- `FileTool` provides a simple existing write path for applying generated full-file patches.

## Current Weaknesses

- Failed `ExecutionResult` objects are not yet connected to an automated recovery workflow.
- Traceback capture is caller-provided rather than standardized across executor workers.
- Patch generation tools are not yet formally registered by category/task.
- There is no common history model for recovery attempts.
- Retry policy is not centralized.
- Rollback is not yet part of the normal patching lifecycle.

## Missing Recovery Mechanisms

- Failure classification by category.
- Recovery policy selection.
- Configurable retry attempts with backoff.
- Patch application with rollback support.
- Validation/test execution after patching.
- Recovery history persistence.
- Memory writeback for successful fixes.

## Failure Scenarios

Supported categories for the first recovery engine:

```text
Syntax Error
Import Error
Dependency Error
Runtime Error
Validation Error
Configuration Error
Filesystem Error
Unknown Error
```

Likely sources:

- Generated code syntax errors.
- Missing imports or package path mistakes.
- Missing Python packages.
- Runtime exceptions in workers.
- Invalid plan/task data.
- Bad configuration values.
- Missing or unwritable files.

## Recovery Opportunities

Initial strategies:

```text
Retry
Patch
Skip
Rollback
Escalate
Abort
```

Best first use cases:

- Syntax/import/runtime errors where a patch generator can return corrected file content.
- Transient runtime failures that should be retried.
- Filesystem failures that should escalate or abort rather than patch blindly.
- Validation failures that should be reported with history, not hidden.

## Scalability Concerns

For many workers and tools:

- Recovery should select patch generators through `ToolRegistry`, not hardcoded classes.
- Recovery history should be compact and searchable through `MemoryManager`.
- Patch validation should be pluggable so future sandbox execution can be added.
- Retry policies should be per-category/per-strategy over time.

## Security Concerns

- Patches must be applied only to explicit paths supplied by the caller.
- No shell execution should be added to the recovery engine.
- Human approval may be required later for sensitive files.
- Registry-selected tools should eventually include permissions and sandbox metadata.
- Rollback should exist before patching production files.

## Improve Before Self-Healing

Handled in this implementation:

- Failure classification.
- Recovery policy selection.
- Retry policy model.
- Patch apply and rollback support.
- Recovery history model.
- Memory storage for successful recovery.
- Registry-aware patch generation path.

## Improve After Self-Healing

Recommended future work:

- Executor-native traceback capture.
- Permission-aware Tool Registry policies.
- Human approval workflow.
- Sandboxed validation execution.
- Remote recovery orchestration.
- Multiple LLM/patch generator ranking.
- Persistent recovery dashboards.

## Conclusion

Self-Healing should be an extension that activates only after executor failure. It should not generate plans, replace Executor, or own AI decisions. Its responsibility is recovery coordination: classify failure, select a recovery strategy, request a patch from an appropriate tool, apply and validate the patch, retry where policy allows, and store successful recoveries in memory.
