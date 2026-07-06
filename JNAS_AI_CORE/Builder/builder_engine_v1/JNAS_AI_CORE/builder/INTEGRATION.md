# Builder Engine v1 — Integration Guide

Steps to drop this module into the real `JNAS_OSV2 / JNAS_AI_CORE`
repository.

## 1. Copy the folder

Copy `builder/` as-is into the `JNAS_AI_CORE/` root, alongside
`agent/`, `llm/`, `tools/`, etc. Do not place it inside another
package.

```
JNAS_AI_CORE/
├── agent/
├── api/
├── builder/          <-- new
├── config/
├── executor/
├── llm/
├── logs/
├── memory/
├── models/
├── planner/
├── prompts/
├── tests/
├── tools/
├── workspace/
└── main.py
```

Also copy `tests/test_builder_engine.py` into the existing `tests/`
folder.

## 2. Verify auto-wiring or inject manually

`BuilderEngine()` tries to auto-import, in order:

```python
llm.llm_manager.LLMManager()
tools.file_tool.FileTool()
agent.project_reader.ProjectReader()
agent.project_scanner.ProjectScanner()
agent.context_builder.ContextBuilder()
agent.code_agent.CodeAgent()
```

If any real class:

- lives at a **different import path** — no auto-wiring will occur;
  you must inject an instance explicitly (see below).
- **requires constructor arguments** — auto-instantiation will fail
  and log a warning; inject an already-constructed instance instead.

Explicit injection (recommended for production use):

```python
from builder import BuilderEngine
from llm.llm_manager import LLMManager
from tools.file_tool import FileTool
from agent.context_builder import ContextBuilder
from agent.project_reader import ProjectReader
from agent.project_scanner import ProjectScanner
from agent.code_agent import CodeAgent

engine = BuilderEngine(
    project_root=Path(__file__).parent,  # JNAS_AI_CORE root
    llm_manager=LLMManager(model="your-model", ...),
    file_tool=FileTool(...),
    context_builder=ContextBuilder(...),
    project_reader=ProjectReader(...),
    project_scanner=ProjectScanner(...),
    code_agent=CodeAgent(...),
)
report = engine.build("planner")
```

## 3. Reconcile method names

`builder/generator.py` and `builder/builder.py` call the injected
components through `call_flexible`, trying these candidate method
names in order:

| Component | Candidates tried |
|---|---|
| `LLMManager` | `generate`, `generate_code`, `complete`, `chat`, `run` |
| `ContextBuilder` | `build`, `build_context`, `get_context`, `run` |
| `FileTool` | `write_file`, `save_file`, `write`, `create_file` |

If the real signatures differ from `(prompt: str) -> str` /
`(path: str, content: str) -> Any`, either:

- Add a thin wrapper/alias method matching one of the candidates, **or**
- Extend the relevant `_..._CANDIDATES` tuple with your actual method
  name.

`ProjectReader`, `ProjectScanner`, and `CodeAgent` are accepted by
`BuilderEngine.__init__` and stored on the instance
(`self.project_reader`, `self.project_scanner`, `self.code_agent`) for
future Builder Engine versions (e.g. richer context gathering, a
review/fix loop using `CodeAgent`). v1 does not call them directly in
the core pipeline, so no reconciliation is required to get the basic
flow working — only `LLMManager` is required for v1.

## 4. Run it

```bash
cd JNAS_AI_CORE
python builder/builder.py planner
```

Check:

- `planner/__init__.py`, `planner.py`, `prompt.txt`,
  `test_planner.py` were created.
- `logs/build_reports/planner_build_report.md` was written.
- Console shows a `BUILD SUMMARY` block.

## 5. CI / automation

`BuilderEngine.build()` returns a `BuildReport` whose `.success`
property is `True` only if generation had no errors and tests passed.
Use the CLI's exit code (`main()` returns `0`/`1`) to gate CI steps:

```bash
python builder/builder.py new_module || exit 1
```

## 6. Extending Builder Engine v2+

Planned extension points already scaffolded in v1:

- `CodeAgent` is wired into `BuilderEngine` but unused by the core
  pipeline — a v2 could route generated code through it for a
  review/refinement pass before saving.
- `ProjectScanner` / `ProjectReader` are wired in for future
  "regenerate existing module" or "scan for missing modules" commands.
- `_gather_context` in `generator.py` already calls `ContextBuilder`
  if present — richer context (e.g. related module signatures) will
  automatically improve generation quality without code changes here.
