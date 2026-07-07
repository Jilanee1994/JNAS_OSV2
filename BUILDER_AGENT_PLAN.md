# Builder Agent Plan

Project: `JNAS Builder Agent V1`

## Goal

Build a standard project creation tool for future JNAS applications. The Builder Agent accepts a project specification, creates folders and files, asks Ollama for each file through the existing LLM manager, saves responses automatically, validates the generated project, and repairs failed files until the project passes or the retry limit is reached.

## Architecture

The implementation extends the existing `JNAS_AI_CORE/Builder` package.

Reused existing Builder modules:

- `utils.call_flexible`
- `utils.strip_markdown_fences`
- `utils.write_text_file`
- existing `LLMManager` integration pattern

New Builder Agent modules:

- `builder_agent.py`
- `project_spec.py`
- `prompt_manager.py`
- `file_writer.py`
- `validator.py`

CLI entrypoints:

- `build_project.py`
- `build_project`

## Phase 1 - BuilderAgent, Project Creator, File Creator

- Added `ProjectSpec` and `ProjectFile` to normalize project specifications.
- Added default project layout for text-only project names such as `AI File Organizer`.
- Added `BuilderFileWriter` to create project roots, directories, and files safely.
- Added path escape protection.

## Phase 2 - Ollama Integration, Prompt Manager, File Writer

- Added `BuilderPromptManager` for file-by-file prompts.
- The agent delegates generation to the existing `LLMManager`, which calls Ollama through the existing JNAS LLM path.
- The agent strips markdown fences and saves each response to its target file automatically.

## Phase 3 - Compile Validation, Test Validation, Auto-Fix Loop

- Added `BuildValidator`.
- Runs `python -m compileall <project_root>`.
- Runs `python -m pytest -q` from the generated project root.
- Extracts failed files from compile and pytest output.
- Sends only validation errors and target file identity back to Ollama for repair.
- Regenerates only failed files.
- Repeats until success or retry limit.

## Phase 4 - Build Report and CLI

- Added `BuilderAgentReport`.
- Saves `BUILD_REPORT.md` inside each generated project.
- Added CLI:

```text
python build_project.py "AI File Organizer"
```

On Linux/Oracle VM, the `build_project` wrapper can be used directly when the repository root is on `PATH`:

```text
build_project "AI File Organizer"
```

## Success Criteria

- Create folders: implemented.
- Create files: implemented.
- Ask Ollama file-by-file: implemented through `LLMManager`.
- Save every file: implemented.
- Compile: implemented.
- Run pytest: implemented.
- Auto-repair failed files: implemented.
- Generate `BUILD_REPORT.md`: implemented.
