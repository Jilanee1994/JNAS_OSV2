# Builder Engine v1 — JNAS_AI_CORE

Automatic module scaffolding engine for `JNAS_AI_CORE`. Given a module
name, it generates a complete, tested Python package skeleton using
the project's existing LLM and file-system components.

## What it does

```
python builder/builder.py planner
```

produces:

```
planner/
├── __init__.py
├── planner.py
├── prompt.txt
└── test_planner.py
```

Pipeline:

1. **Scaffold** — create `planner/` if missing.
2. **Generate** — use the existing `LLMManager` to write `planner.py`
   and `test_planner.py`; strip Markdown code fences from the output.
3. **Persist** — save files via the existing `FileTool`.
4. **Test** — run `pytest` against the generated test file.
5. **Report** — write a Markdown build report to
   `logs/build_reports/planner_build_report.md` and print a console
   summary.

## Files

| File | Responsibility |
|---|---|
| `builder.py` | `BuilderEngine` orchestrator + CLI entrypoint |
| `generator.py` | `CodeGenerator` — LLM-backed code/test/prompt generation |
| `templates.py` | Prompt templates + safe fallback skeletons |
| `tester.py` | `TestRunner` — runs pytest, parses pass/fail counts |
| `reporter.py` | `BuildReport` / `BuildReporter` — Markdown reports + console summary |
| `utils.py` | Logging, fence stripping, flexible component adapter, pytest runner |

## Reused components (not duplicated)

`BuilderEngine` is constructed with the project's already-implemented
components. It never reimplements their logic:

- `LLMManager` — all text generation (required).
- `FileTool` — all file persistence (optional; falls back to direct
  filesystem writes if absent).
- `ContextBuilder` — enriches generation prompts with project context
  (optional).
- `ProjectReader`, `ProjectScanner`, `CodeAgent` — accepted and wired
  in for future Builder features (e.g. context-aware regeneration,
  code review passes); not required for v1's core pipeline.

By default, `BuilderEngine()` attempts to auto-import these from:

```
llm.llm_manager.LLMManager
tools.file_tool.FileTool
agent.project_reader.ProjectReader
agent.project_scanner.ProjectScanner
agent.context_builder.ContextBuilder
agent.code_agent.CodeAgent
```

If your real classes live elsewhere or require constructor arguments,
inject already-constructed instances explicitly (see Integration
Guide).

### Adapting to unknown exact method names

Because this Builder was written alongside — not inside — the real
component implementations, it calls them through
`builder.utils.call_flexible`, which tries a short list of common
method names (`generate`, `write_file`, `build`, etc.) in order. If
your real components use different method names, either:

- rename/alias the method to one of the candidates, or
- add your method name to the relevant `_..._CANDIDATES` tuple in
  `generator.py` / `builder.py`.

## CLI usage

```bash
python builder/builder.py <module_name> [--project-root PATH] [--no-tests]
```

- `module_name`: name of the module to create (must be a valid Python
  identifier).
- `--project-root`: where the module folder is created (defaults to
  CWD — normally run from `JNAS_AI_CORE/`).
- `--no-tests`: skip running pytest after generation.

Exit code is `0` on success, `1` if generation or tests failed.

## Programmatic usage

```python
from builder import BuilderEngine

engine = BuilderEngine()  # auto-wires existing components
report = engine.build("planner")

if not report.success:
    print(report.generation_errors)
```

## Testing the Builder itself

```bash
pip install -r builder/requirements.txt
pytest tests/test_builder_engine.py -v
```

All 25 tests mock the external components (`LLMManager`, `FileTool`,
etc.) so they validate Builder Engine logic in isolation, independent
of the real implementations.
