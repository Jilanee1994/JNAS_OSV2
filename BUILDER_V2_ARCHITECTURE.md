# Builder Agent V2 Architecture

Project: `JNAS Builder Agent V2`

## Current Builder V1 Architecture

Builder Agent V1 extends the existing `JNAS_AI_CORE/Builder` package without replacing the original Builder Engine. Its current flow is:

1. Convert a user specification into `ProjectSpec`.
2. Create a generated project root with `BuilderFileWriter`.
3. Build one prompt per file with `BuilderPromptManager`.
4. Generate file content through the existing LLM manager adapter path.
5. Strip markdown fences and write files safely.
6. Run `python -m compileall`.
7. Run `pytest`.
8. Regenerate failed files until success or retry limit.
9. Write `BUILD_REPORT.md`.

Key V1 files:

- `JNAS_AI_CORE/Builder/builder_agent.py`
- `JNAS_AI_CORE/Builder/project_spec.py`
- `JNAS_AI_CORE/Builder/prompt_manager.py`
- `JNAS_AI_CORE/Builder/file_writer.py`
- `JNAS_AI_CORE/Builder/validator.py`

## Weaknesses

- LLM access is still centered on the existing `LLMManager` fallback path, so provider selection is not explicit.
- The retry loop repairs files directly instead of routing recovery through the Self-Healing Engine.
- Validation results are useful but not detailed enough for V2 reporting, especially pytest pass/fail/skip counts and execution time.
- The primary public method is `build_project()`, which works, but the requested V2 workflow needs a clearer `execute()` pipeline boundary.
- Build reports do not yet include self-healing actions.

## Proposed V2 Architecture

Builder V2 keeps V1 intact and adds a thin autonomous pipeline:

```text
User Prompt
  -> ProjectSpec
  -> Planner
  -> BuilderAgent.execute()
  -> LLM Router / Provider Interface
  -> BuilderFileWriter
  -> BuildValidator
  -> SelfHealingEngine on validation failure
  -> BuilderV2Report
```

The V2 implementation will:

- Add a Builder-level LLM interface that adapts to the existing `JNAS_AI_CORE.llm_router`.
- Add provider classes for Ollama, Gemini, Groq, and OpenRouter that reuse the existing HTTP provider implementation.
- Add an execution pipeline that coordinates project creation, generation, writing, compile validation, pytest validation, self-healing, retry, and reporting.
- Extend validation result metadata in a backward-compatible way.
- Preserve `BuilderAgent.build_project()` and add `BuilderAgent.execute()` for V2.

## Integration Points

- Planner: used to create an execution plan from the user prompt for reporting and future orchestration.
- LLM Router: used for provider selection and fallback. V2 does not hardcode Ollama.
- Builder V1 modules: reused for project specs, prompt generation, file writing, fence stripping, and validation.
- Self-Healing Engine: invoked after compile or pytest failures. V2 does not duplicate recovery logic.
- FileTool path: still available through `BuilderFileWriter` injection.

## Files To Modify

- `JNAS_AI_CORE/Builder/__init__.py`
- `JNAS_AI_CORE/Builder/builder_agent.py`
- `JNAS_AI_CORE/Builder/validator.py`

## Files To Add

- `JNAS_AI_CORE/Builder/llm_interface.py`
- `JNAS_AI_CORE/Builder/pipeline.py`
- `JNAS_AI_CORE/Builder/report_v2.py`
- `tests/test_builder_agent_v2.py`
- `BUILDER_V2_REPORT.md`
- `NEXT_BUILDER_V3.md`

## Compatibility

Builder V1 remains available through `build_project()`, the existing CLI, and the current exported classes. V2 is additive and uses constructor dependency injection so existing tests and integrations continue to work.
