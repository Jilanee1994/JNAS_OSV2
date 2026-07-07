# Import Graph

This import graph is generated from Python AST imports. It resolves internal dependencies using the repository root plus likely script roots such as `JNAS_AI_CORE`, `Scraper-Engine`, and `updater`.

## Dependency Edges

- `JNAS_AI_CORE/Builder/builder.py` -> `JNAS_AI_CORE/Builder/generator.py`
- `JNAS_AI_CORE/Builder/builder.py` -> `JNAS_AI_CORE/Builder/reporter.py`
- `JNAS_AI_CORE/Builder/builder.py` -> `JNAS_AI_CORE/Builder/tester.py`
- `JNAS_AI_CORE/Builder/builder.py` -> `JNAS_AI_CORE/Builder/utils.py`
- `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/builder.py` -> `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/generator.py`
- `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/builder.py` -> `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/reporter.py`
- `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/builder.py` -> `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/tester.py`
- `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/builder.py` -> `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/utils.py`
- `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/generator.py` -> `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/__init__.py`
- `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/generator.py` -> `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/templates.py`
- `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/generator.py` -> `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/utils.py`
- `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/reporter.py` -> `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/tester.py`
- `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/reporter.py` -> `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/utils.py`
- `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/tester.py` -> `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/utils.py`
- `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/tests/test_builder_engine.py` -> `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/builder.py`
- `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/tests/test_builder_engine.py` -> `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/generator.py`
- `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/tests/test_builder_engine.py` -> `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/reporter.py`
- `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/tests/test_builder_engine.py` -> `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/tester.py`
- `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/tests/test_builder_engine.py` -> `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/utils.py`
- `JNAS_AI_CORE/Builder/generator.py` -> `JNAS_AI_CORE/Builder/__init__.py`
- `JNAS_AI_CORE/Builder/generator.py` -> `JNAS_AI_CORE/Builder/templates.py`
- `JNAS_AI_CORE/Builder/generator.py` -> `JNAS_AI_CORE/Builder/utils.py`
- `JNAS_AI_CORE/Builder/reporter.py` -> `JNAS_AI_CORE/Builder/tester.py`
- `JNAS_AI_CORE/Builder/reporter.py` -> `JNAS_AI_CORE/Builder/utils.py`
- `JNAS_AI_CORE/Builder/tester.py` -> `JNAS_AI_CORE/Builder/utils.py`
- `JNAS_AI_CORE/agent/code_agent.py` -> `JNAS_AI_CORE/llm/context_builder.py`
- `JNAS_AI_CORE/agent/code_agent.py` -> `JNAS_AI_CORE/llm/manager.py`
- `JNAS_AI_CORE/agent/code_agent.py` -> `JNAS_AI_CORE/tools/file_tool.py`
- `JNAS_AI_CORE/llm/context_builder.py` -> `JNAS_AI_CORE/tools/project_reader.py`
- `JNAS_AI_CORE/llm/manager.py` -> `JNAS_AI_CORE/llm/ollama_client.py`
- `JNAS_AI_CORE/llm/ollama_client.py` -> `JNAS_AI_CORE/config/settings.py`
- `JNAS_AI_CORE/main.py` -> `JNAS_AI_CORE/llm/manager.py`
- `JNAS_AI_CORE/test_agent.py` -> `JNAS_AI_CORE/agent/code_agent.py`
- `JNAS_AI_CORE/test_context.py` -> `JNAS_AI_CORE/llm/context_builder.py`
- `JNAS_AI_CORE/test_reader.py` -> `JNAS_AI_CORE/tools/project_reader.py`
- `JNAS_AI_CORE/test_scanner.py` -> `JNAS_AI_CORE/tools/project_scanner.py`
- `Scraper-Engine/app.py` -> `Scraper-Engine/src/cleaner.py`
- `Scraper-Engine/app.py` -> `Scraper-Engine/src/downloader.py`
- `Scraper-Engine/app.py` -> `Scraper-Engine/src/logger.py`
- `Scraper-Engine/app.py` -> `Scraper-Engine/src/parser.py`
- `Scraper-Engine/src/cleaner.py` -> `Scraper-Engine/src/logger.py`
- `Scraper-Engine/src/downloader.py` -> `Scraper-Engine/config/config.py`
- `Scraper-Engine/src/downloader.py` -> `Scraper-Engine/src/logger.py`
- `Scraper-Engine/src/logger.py` -> `Scraper-Engine/config/config.py`
- `Scraper-Engine/src/parser.py` -> `Scraper-Engine/src/logger.py`
- `updater/updater.py` -> `updater/backup.py`
- `updater/updater.py` -> `updater/logger.py`
- `updater/updater.py` -> `updater/parser.py`
- `updater/updater.py` -> `updater/validator.py`
- `updater/updater.py` -> `updater/writer.py`

## Circular Imports

- None detected by AST import analysis.

## High Coupling Modules

Modules listed here have at least four combined incoming and outgoing internal dependency edges.

- `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/builder.py`: outgoing=4, incoming=1, total=5
- `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/generator.py`: outgoing=3, incoming=2, total=5
- `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/utils.py`: outgoing=0, incoming=5, total=5
- `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/tests/test_builder_engine.py`: outgoing=5, incoming=0, total=5
- `Scraper-Engine/src/logger.py`: outgoing=1, incoming=4, total=5
- `updater/updater.py`: outgoing=5, incoming=0, total=5
- `JNAS_AI_CORE/Builder/builder.py`: outgoing=4, incoming=0, total=4
- `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/reporter.py`: outgoing=2, incoming=2, total=4
- `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/tester.py`: outgoing=1, incoming=3, total=4
- `JNAS_AI_CORE/Builder/generator.py`: outgoing=3, incoming=1, total=4
- `JNAS_AI_CORE/Builder/utils.py`: outgoing=0, incoming=4, total=4
- `JNAS_AI_CORE/agent/code_agent.py`: outgoing=3, incoming=1, total=4
- `Scraper-Engine/app.py`: outgoing=4, incoming=0, total=4

## Low Coupling Modules

Modules listed here have zero or one combined internal dependency edge.

- `JNAS_AI_CORE/Builder/test_builder_engine.py`: outgoing=0, incoming=0, total=0
- `JNAS_AI_CORE/workspace/logger.py`: outgoing=0, incoming=0, total=0
- `JNAS_AI_CORE/workspace/test.py`: outgoing=0, incoming=0, total=0
- `Scraper-Engine/src/browser.py`: outgoing=0, incoming=0, total=0
- `Scraper-Engine/src/cookies.py`: outgoing=0, incoming=0, total=0
- `Scraper-Engine/src/playwright_engine.py`: outgoing=0, incoming=0, total=0
- `Scraper-Engine/src/screenshot.py`: outgoing=0, incoming=0, total=0
- `Scraper-Engine/src/waits.py`: outgoing=0, incoming=0, total=0
- `backend/__init__.py`: outgoing=0, incoming=0, total=0
- `backend/main.py`: outgoing=0, incoming=0, total=0
- `config/settings.py`: outgoing=0, incoming=0, total=0
- `frontend/app.py`: outgoing=0, incoming=0, total=0
- `updater/utils.py`: outgoing=0, incoming=0, total=0
- `updater/utlis.py`: outgoing=0, incoming=0, total=0
- `JNAS_AI_CORE/Builder/__init__.py`: outgoing=0, incoming=1, total=1
- `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/__init__.py`: outgoing=0, incoming=1, total=1
- `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/templates.py`: outgoing=0, incoming=1, total=1
- `JNAS_AI_CORE/Builder/templates.py`: outgoing=0, incoming=1, total=1
- `JNAS_AI_CORE/config/settings.py`: outgoing=0, incoming=1, total=1
- `JNAS_AI_CORE/main.py`: outgoing=1, incoming=0, total=1
- `JNAS_AI_CORE/test_agent.py`: outgoing=1, incoming=0, total=1
- `JNAS_AI_CORE/test_context.py`: outgoing=1, incoming=0, total=1
- `JNAS_AI_CORE/test_reader.py`: outgoing=1, incoming=0, total=1
- `JNAS_AI_CORE/test_scanner.py`: outgoing=1, incoming=0, total=1
- `JNAS_AI_CORE/tools/file_tool.py`: outgoing=0, incoming=1, total=1
- `JNAS_AI_CORE/tools/project_scanner.py`: outgoing=0, incoming=1, total=1
- `updater/backup.py`: outgoing=0, incoming=1, total=1
- `updater/logger.py`: outgoing=0, incoming=1, total=1
- `updater/parser.py`: outgoing=0, incoming=1, total=1
- `updater/validator.py`: outgoing=0, incoming=1, total=1
- `updater/writer.py`: outgoing=0, incoming=1, total=1

## Shared Utilities

- `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/utils.py`
- `JNAS_AI_CORE/Builder/utils.py`
- `JNAS_AI_CORE/config/settings.py`
- `JNAS_AI_CORE/tools/file_tool.py`
- `JNAS_AI_CORE/workspace/logger.py`
- `Scraper-Engine/src/logger.py`
- `config/settings.py`
- `updater/logger.py`
- `updater/utils.py`
- `updater/utlis.py`

## Core Modules

Core modules are inferred from incoming dependency count and entry-point role.

- `JNAS_AI_CORE/Builder/builder.py`: incoming=0, outgoing=4, entry_point=True
- `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/builder.py`: incoming=1, outgoing=4, entry_point=True
- `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/generator.py`: incoming=2, outgoing=3, entry_point=False
- `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/reporter.py`: incoming=2, outgoing=2, entry_point=False
- `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/tester.py`: incoming=3, outgoing=1, entry_point=False
- `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/utils.py`: incoming=5, outgoing=0, entry_point=False
- `JNAS_AI_CORE/Builder/tester.py`: incoming=2, outgoing=1, entry_point=False
- `JNAS_AI_CORE/Builder/utils.py`: incoming=4, outgoing=0, entry_point=False
- `JNAS_AI_CORE/llm/context_builder.py`: incoming=2, outgoing=1, entry_point=False
- `JNAS_AI_CORE/llm/manager.py`: incoming=2, outgoing=1, entry_point=False
- `JNAS_AI_CORE/llm/ollama_client.py`: incoming=1, outgoing=1, entry_point=True
- `JNAS_AI_CORE/main.py`: incoming=0, outgoing=1, entry_point=True
- `JNAS_AI_CORE/tools/project_reader.py`: incoming=2, outgoing=0, entry_point=False
- `Scraper-Engine/app.py`: incoming=0, outgoing=4, entry_point=True
- `Scraper-Engine/config/config.py`: incoming=2, outgoing=0, entry_point=False
- `Scraper-Engine/src/logger.py`: incoming=4, outgoing=1, entry_point=False
- `backend/main.py`: incoming=0, outgoing=0, entry_point=True
- `frontend/app.py`: incoming=0, outgoing=0, entry_point=True
- `updater/updater.py`: incoming=0, outgoing=5, entry_point=True

## Internal Dependency Adjacency List

- `JNAS_AI_CORE/Builder/__init__.py`: none
- `JNAS_AI_CORE/Builder/builder.py`: `JNAS_AI_CORE/Builder/generator.py`, `JNAS_AI_CORE/Builder/reporter.py`, `JNAS_AI_CORE/Builder/tester.py`, `JNAS_AI_CORE/Builder/utils.py`
- `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/__init__.py`: none
- `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/builder.py`: `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/generator.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/reporter.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/tester.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/utils.py`
- `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/generator.py`: `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/__init__.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/templates.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/utils.py`
- `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/reporter.py`: `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/tester.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/utils.py`
- `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/templates.py`: none
- `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/tester.py`: `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/utils.py`
- `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/utils.py`: none
- `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/tests/test_builder_engine.py`: `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/builder.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/generator.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/reporter.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/tester.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/utils.py`
- `JNAS_AI_CORE/Builder/generator.py`: `JNAS_AI_CORE/Builder/__init__.py`, `JNAS_AI_CORE/Builder/templates.py`, `JNAS_AI_CORE/Builder/utils.py`
- `JNAS_AI_CORE/Builder/reporter.py`: `JNAS_AI_CORE/Builder/tester.py`, `JNAS_AI_CORE/Builder/utils.py`
- `JNAS_AI_CORE/Builder/templates.py`: none
- `JNAS_AI_CORE/Builder/test_builder_engine.py`: none
- `JNAS_AI_CORE/Builder/tester.py`: `JNAS_AI_CORE/Builder/utils.py`
- `JNAS_AI_CORE/Builder/utils.py`: none
- `JNAS_AI_CORE/agent/code_agent.py`: `JNAS_AI_CORE/llm/context_builder.py`, `JNAS_AI_CORE/llm/manager.py`, `JNAS_AI_CORE/tools/file_tool.py`
- `JNAS_AI_CORE/config/settings.py`: none
- `JNAS_AI_CORE/llm/context_builder.py`: `JNAS_AI_CORE/tools/project_reader.py`
- `JNAS_AI_CORE/llm/manager.py`: `JNAS_AI_CORE/llm/ollama_client.py`
- `JNAS_AI_CORE/llm/ollama_client.py`: `JNAS_AI_CORE/config/settings.py`
- `JNAS_AI_CORE/main.py`: `JNAS_AI_CORE/llm/manager.py`
- `JNAS_AI_CORE/test_agent.py`: `JNAS_AI_CORE/agent/code_agent.py`
- `JNAS_AI_CORE/test_context.py`: `JNAS_AI_CORE/llm/context_builder.py`
- `JNAS_AI_CORE/test_reader.py`: `JNAS_AI_CORE/tools/project_reader.py`
- `JNAS_AI_CORE/test_scanner.py`: `JNAS_AI_CORE/tools/project_scanner.py`
- `JNAS_AI_CORE/tools/file_tool.py`: none
- `JNAS_AI_CORE/tools/project_reader.py`: none
- `JNAS_AI_CORE/tools/project_scanner.py`: none
- `JNAS_AI_CORE/workspace/logger.py`: none
- `JNAS_AI_CORE/workspace/test.py`: none
- `Scraper-Engine/app.py`: `Scraper-Engine/src/cleaner.py`, `Scraper-Engine/src/downloader.py`, `Scraper-Engine/src/logger.py`, `Scraper-Engine/src/parser.py`
- `Scraper-Engine/config/config.py`: none
- `Scraper-Engine/src/browser.py`: none
- `Scraper-Engine/src/cleaner.py`: `Scraper-Engine/src/logger.py`
- `Scraper-Engine/src/cookies.py`: none
- `Scraper-Engine/src/downloader.py`: `Scraper-Engine/config/config.py`, `Scraper-Engine/src/logger.py`
- `Scraper-Engine/src/logger.py`: `Scraper-Engine/config/config.py`
- `Scraper-Engine/src/parser.py`: `Scraper-Engine/src/logger.py`
- `Scraper-Engine/src/playwright_engine.py`: none
- `Scraper-Engine/src/screenshot.py`: none
- `Scraper-Engine/src/waits.py`: none
- `backend/__init__.py`: none
- `backend/main.py`: none
- `config/settings.py`: none
- `frontend/app.py`: none
- `updater/backup.py`: none
- `updater/logger.py`: none
- `updater/parser.py`: none
- `updater/updater.py`: `updater/backup.py`, `updater/logger.py`, `updater/parser.py`, `updater/validator.py`, `updater/writer.py`
- `updater/utils.py`: none
- `updater/utlis.py`: none
- `updater/validator.py`: none
- `updater/writer.py`: none

## Observations

- `JNAS_AI_CORE` modules use imports such as `llm.manager` and `tools.file_tool`, which assume `JNAS_AI_CORE` is on `PYTHONPATH` or the current working directory is the package root.
- `Scraper-Engine` modules use imports such as `src.downloader` and `config.config`, which assume execution from inside the `Scraper-Engine` folder or equivalent path setup.
- `updater/updater.py` imports sibling modules as top-level names (`parser`, `writer`, `backup`, `validator`, `logger`), which assumes script-style execution from the `updater` directory.
- No circular imports were detected by static AST analysis, but runtime path manipulation or dynamic imports would require separate execution-time validation.
