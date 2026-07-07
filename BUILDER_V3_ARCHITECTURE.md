# Builder Agent V3 Architecture

Project: `JNAS Builder Agent V3`

## Current State

Builder Agent V1 provides file-by-file project generation using `LLMManager`, `BuilderFileWriter`, `BuilderPromptManager`, and `BuildValidator`.

Builder Agent V2 added:

- Provider-agnostic `BuilderLLMClient`
- LLM Router integration
- `BuilderAgent.execute()`
- Self-Healing integration
- V2 build reports

V2 is validated and remains unchanged for existing integrations.

## V3 Objective

Builder Agent V3 becomes the autonomous project builder:

```text
User Prompt
  -> Planner
  -> Project Specification
  -> LLM Router
  -> Generate Project Structure
  -> Generate One File
  -> Write File
  -> Compile
  -> Run Tests
  -> Self-Healing on failure
  -> Retry
  -> Generate Report
  -> Optional Git Commit
```

## Proposed V3 Architecture

V3 adds explicit pipeline stage classes while reusing V2 and core JNAS modules:

- `BuilderProviderFactory`: builds providers from configuration and preserves configured priority.
- `ConfiguredLLMProvider`: one provider interface for Ollama, Gemini, Groq, and OpenRouter style HTTP APIs.
- `ProjectCreator`: uses Planner and LLM output to create a `ProjectSpec`.
- `LLMGenerator`: generates one file at a time through `BuilderLLMClient`.
- `Compiler`: wraps existing `BuildValidator.compile_project()`.
- `PytestRunner`: wraps existing `BuildValidator.test_project()`.
- `BuilderReporter`: writes final `BUILD_REPORT.md`.
- `BuilderPipeline`: coordinates all stages.
- `BuilderAgentV3`: public facade for V3.

## Configuration

Provider selection is configuration-driven. V3 reads:

- `builder_v3.provider_priority`
- `builder_v3.max_retries`
- `builder_v3.workspace`
- `llm_router.providers`

The default priority order is:

1. `ollama`
2. `gemini`
3. `groq`
4. `openrouter`

Providers can be enabled, disabled, reordered, or extended through configuration without changing the pipeline.

## Integration Points

- Planner: reused to convert the prompt into planning context.
- LLM Router: reused for provider ranking and fallback.
- Self-Healing: reused for compile and pytest recovery.
- Builder V2: reused for prompt management, file writing, validation models, and patch generation.
- Configuration Manager: reused for provider priority and retry/workspace settings.

## Files Added

- `JNAS_AI_CORE/Builder/provider_factory_v3.py`
- `JNAS_AI_CORE/Builder/project_creator_v3.py`
- `JNAS_AI_CORE/Builder/generator_v3.py`
- `JNAS_AI_CORE/Builder/validation_v3.py`
- `JNAS_AI_CORE/Builder/reporter_v3.py`
- `JNAS_AI_CORE/Builder/builder_v3.py`
- `tests/test_builder_agent_v3.py`
- `BUILDER_V3_REPORT.md`
- `NEXT_BUILDER_V4.md`

## Files Modified

- `JNAS_AI_CORE/Builder/__init__.py`
- `JNAS_AI_CORE/configuration/defaults.py`

## Compatibility

Builder V1 and V2 behavior is preserved. V3 is additive and exposed through new classes.
