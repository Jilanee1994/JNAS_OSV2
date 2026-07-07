<<<<<<< HEAD
# Module Map

This document maps every Python module found in `JNAS_OSV2-main`. Public classes and functions are derived from AST parsing. Dependencies are split into internal repository modules and external/standard-library imports.

## `JNAS_AI_CORE/Builder/__init__.py`

- Module name: `JNAS_AI_CORE.Builder`
- Purpose: Builder Engine v1 for JNAS_AI_CORE. Automatically scaffolds new modules (folder, source file, prompt artifact, and unit tests), using the project's existing LLMManager, FileTool, ProjectReader, ProjectScanner, ContextBuilder, and CodeAgent 
- Responsibilities:
  - Contains constants, module-level setup, placeholder code, or package initialization
- Public classes: none
- Public functions: none
- Internal dependencies: none detected
- External / stdlib dependencies: `__future__`, `builder`, `generator`, `reporter`, `tester`
- Used by: `JNAS_AI_CORE/Builder/generator.py`

## `JNAS_AI_CORE/Builder/builder.py`

- Module name: `JNAS_AI_CORE.Builder.builder`
- Purpose: builder.builder ================ Builder Engine v1 -- orchestrates automatic module generation for JNAS_AI_CORE. Given a module name (e.g. ``planner``), the ``BuilderEngine``: 1. Creates the module folder (if missing). 2. Generates ``__init
- Responsibilities:
  - Expose `BuilderEngine` with methods `build`
  - Expose functions `main`
  - Serve as an executable entry point or script module
  - Coordinate with internal modules: `JNAS_AI_CORE/Builder/generator.py`, `JNAS_AI_CORE/Builder/reporter.py`, `JNAS_AI_CORE/Builder/tester.py`, `JNAS_AI_CORE/Builder/utils.py`
- Public classes:
  - `BuilderEngine`; methods: `build`
- Public functions: `main`
- Internal dependencies: `JNAS_AI_CORE/Builder/generator.py`, `JNAS_AI_CORE/Builder/reporter.py`, `JNAS_AI_CORE/Builder/tester.py`, `JNAS_AI_CORE/Builder/utils.py`
- External / stdlib dependencies: `__future__`, `argparse`, `importlib`, `logging`, `pathlib`, `sys`, `typing`
- Used by: no internal dependents detected

## `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/__init__.py`

- Module name: `JNAS_AI_CORE.Builder.builder_engine_v1.JNAS_AI_CORE.builder`
- Purpose: Builder Engine v1 for JNAS_AI_CORE. Automatically scaffolds new modules (folder, source file, prompt artifact, and unit tests), using the project's existing LLMManager, FileTool, ProjectReader, ProjectScanner, ContextBuilder, and CodeAgent 
- Responsibilities:
  - Contains constants, module-level setup, placeholder code, or package initialization
- Public classes: none
- Public functions: none
- Internal dependencies: none detected
- External / stdlib dependencies: `__future__`, `generator`, `reporter`, `tester`
- Used by: `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/generator.py`

## `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/builder.py`

- Module name: `JNAS_AI_CORE.Builder.builder_engine_v1.JNAS_AI_CORE.builder.builder`
- Purpose: builder.builder ================ Builder Engine v1 -- orchestrates automatic module generation for JNAS_AI_CORE. Given a module name (e.g. ``planner``), the ``BuilderEngine``: 1. Creates the module folder (if missing). 2. Generates ``__init
- Responsibilities:
  - Expose `BuilderEngine` with methods `build`
  - Expose functions `main`
  - Serve as an executable entry point or script module
  - Coordinate with internal modules: `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/generator.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/reporter.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/tester.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/utils.py`
- Public classes:
  - `BuilderEngine`; methods: `build`
- Public functions: `main`
- Internal dependencies: `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/generator.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/reporter.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/tester.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/utils.py`
- External / stdlib dependencies: `__future__`, `argparse`, `importlib`, `logging`, `pathlib`, `sys`, `typing`
- Used by: `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/tests/test_builder_engine.py`

## `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/generator.py`

- Module name: `JNAS_AI_CORE.Builder.builder_engine_v1.JNAS_AI_CORE.builder.generator`
- Purpose: builder.generator ================== Wraps the existing ``LLMManager`` (and optionally ``ContextBuilder`` / ``CodeAgent``) to generate module source code, unit tests, and prompt artifacts for the Builder Engine. This module does NOT impleme
- Responsibilities:
  - Expose `CodeGenerator` with methods `generate_module_code`, `generate_test_code`, `generate_prompt_artifact`, `generate_init_code`
  - Coordinate with internal modules: `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/__init__.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/templates.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/utils.py`
- Public classes:
  - `CodeGenerator`; methods: `generate_module_code`, `generate_test_code`, `generate_prompt_artifact`, `generate_init_code`
- Public functions: none
- Internal dependencies: `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/__init__.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/templates.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/utils.py`
- External / stdlib dependencies: `__future__`, `logging`, `typing`
- Used by: `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/builder.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/tests/test_builder_engine.py`

## `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/reporter.py`

- Module name: `JNAS_AI_CORE.Builder.builder_engine_v1.JNAS_AI_CORE.builder.reporter`
- Purpose: builder.reporter ================= Produces build reports (Markdown + in-memory structured data) and prints a human-readable build summary to the console.
- Responsibilities:
  - Expose `BuildReport` with methods `success`, `to_markdown`
  - Expose `BuildReporter` with methods `save_report`, `print_summary`
  - Coordinate with internal modules: `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/tester.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/utils.py`
- Public classes:
  - `BuildReport`; methods: `success`, `to_markdown`
  - `BuildReporter`; methods: `save_report`, `print_summary`
- Public functions: none
- Internal dependencies: `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/tester.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/utils.py`
- External / stdlib dependencies: `__future__`, `dataclasses`, `datetime`, `logging`, `pathlib`, `typing`
- Used by: `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/builder.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/tests/test_builder_engine.py`

## `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/templates.py`

- Module name: `JNAS_AI_CORE.Builder.builder_engine_v1.JNAS_AI_CORE.builder.templates`
- Purpose: builder.templates ================== Centralized templates used by the Builder Engine: - LLM prompt templates for module/test generation - Static fallback templates used only if the LLM is unreachable (keeps the Builder resilient / producti
- Responsibilities:
  - Expose functions `module_generation_prompt`, `test_generation_prompt`, `prompt_artifact`, `fallback_module_code`, `fallback_test_code`, `init_file_content`
- Public classes: none
- Public functions: `module_generation_prompt`, `test_generation_prompt`, `prompt_artifact`, `fallback_module_code`, `fallback_test_code`, `init_file_content`
- Internal dependencies: none detected
- External / stdlib dependencies: `__future__`
- Used by: `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/generator.py`

## `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/tester.py`

- Module name: `JNAS_AI_CORE.Builder.builder_engine_v1.JNAS_AI_CORE.builder.tester`
- Purpose: builder.tester ============== Executes pytest against generated modules and captures structured pass/fail results for the Builder Engine's reporting stage.
- Responsibilities:
  - Expose `TestOutcome`
  - Expose `TestRunner` with methods `run`
  - Coordinate with internal modules: `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/utils.py`
- Public classes:
  - `TestOutcome`; methods: none listed
  - `TestRunner`; methods: `run`
- Public functions: none
- Internal dependencies: `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/utils.py`
- External / stdlib dependencies: `__future__`, `dataclasses`, `logging`, `pathlib`, `re`, `typing`
- Used by: `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/builder.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/reporter.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/tests/test_builder_engine.py`

## `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/utils.py`

- Module name: `JNAS_AI_CORE.Builder.builder_engine_v1.JNAS_AI_CORE.builder.utils`
- Purpose: builder.utils ============= Shared low-level utilities for the Builder Engine. This module provides: - Logger factory - Markdown code-fence stripping - Filesystem helpers (used only as a fallback when ``FileTool`` is unavailable) - A flexib
- Responsibilities:
  - Expose `PytestResult`
  - Expose `LLMManagerProtocol` with methods `generate`
  - Expose `FileToolProtocol` with methods `write_file`, `read_file`
  - Expose `ProjectReaderProtocol` with methods `read`
  - Expose `ProjectScannerProtocol` with methods `scan`
  - Expose `ContextBuilderProtocol` with methods `build`
  - Expose `CodeAgentProtocol` with methods `run`
  - Expose functions `get_logger`, `strip_markdown_fences`, `ensure_dir`, `write_text_file`, `call_flexible`, `run_pytest`
- Public classes:
  - `PytestResult`; methods: none listed
  - `LLMManagerProtocol`; methods: `generate`
  - `FileToolProtocol`; methods: `write_file`, `read_file`
  - `ProjectReaderProtocol`; methods: `read`
  - `ProjectScannerProtocol`; methods: `scan`
  - `ContextBuilderProtocol`; methods: `build`
  - `CodeAgentProtocol`; methods: `run`
- Public functions: `get_logger`, `strip_markdown_fences`, `ensure_dir`, `write_text_file`, `call_flexible`, `run_pytest`
- Internal dependencies: none detected
- External / stdlib dependencies: `__future__`, `dataclasses`, `logging`, `pathlib`, `re`, `subprocess`, `sys`, `typing`
- Used by: `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/builder.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/generator.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/reporter.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/tester.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/tests/test_builder_engine.py`

## `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/tests/test_builder_engine.py`

- Module name: `JNAS_AI_CORE.Builder.builder_engine_v1.JNAS_AI_CORE.tests.test_builder_engine`
- Purpose: Unit tests for the Builder Engine (builder/ package). All existing JNAS_AI_CORE components (LLMManager, FileTool, ContextBuilder, etc.) are mocked here so these tests exercise only the Builder Engine's own logic, independent of the real imp
- Responsibilities:
  - Expose `TestStripMarkdownFences` with methods `test_strips_full_fenced_block`, `test_strips_fence_without_language`, `test_returns_clean_text_unchanged`, `test_handles_empty_string`, `test_handles_none`
  - Expose `TestCallFlexible` with methods `test_calls_first_matching_method`, `test_raises_attribute_error_when_no_method_found`, `test_raises_on_none_object`
  - Expose `TestCodeGenerator` with methods `test_requires_llm_manager`, `test_generate_module_code_strips_fences`, `test_generate_module_code_falls_back_on_llm_failure`, `test_generate_test_code_uses_module_code_context`, `test_context_builder_failure_is_non_fatal`
  - Expose `TestTestRunner` with methods `test_parses_passed_counts`, `test_parses_failures`
  - Expose `TestBuildReporter` with methods `test_report_success_property_true_when_no_errors_or_tests`, `test_report_success_property_false_on_generation_error`, `test_report_success_reflects_test_outcome`, `test_to_markdown_contains_module_name`, `test_save_report_writes_file`, `test_print_summary_does_not_raise`
  - Expose `TestBuilderEngine` with methods `test_build_creates_expected_files`, `test_build_rejects_invalid_module_name`, `test_build_requires_llm_manager`, `test_build_runs_tests_when_requested`
  - Expose `Component` with methods `generate`
  - Expose `Component`
  - Expose functions `mock_llm_manager`, `mock_file_tool`
  - Coordinate with internal modules: `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/builder.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/generator.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/reporter.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/tester.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/utils.py`
- Public classes:
  - `TestStripMarkdownFences`; methods: `test_strips_full_fenced_block`, `test_strips_fence_without_language`, `test_returns_clean_text_unchanged`, `test_handles_empty_string`, `test_handles_none`
  - `TestCallFlexible`; methods: `test_calls_first_matching_method`, `test_raises_attribute_error_when_no_method_found`, `test_raises_on_none_object`
  - `TestCodeGenerator`; methods: `test_requires_llm_manager`, `test_generate_module_code_strips_fences`, `test_generate_module_code_falls_back_on_llm_failure`, `test_generate_test_code_uses_module_code_context`, `test_context_builder_failure_is_non_fatal`
  - `TestTestRunner`; methods: `test_parses_passed_counts`, `test_parses_failures`
  - `TestBuildReporter`; methods: `test_report_success_property_true_when_no_errors_or_tests`, `test_report_success_property_false_on_generation_error`, `test_report_success_reflects_test_outcome`, `test_to_markdown_contains_module_name`, `test_save_report_writes_file`, `test_print_summary_does_not_raise`
  - `TestBuilderEngine`; methods: `test_build_creates_expected_files`, `test_build_rejects_invalid_module_name`, `test_build_requires_llm_manager`, `test_build_runs_tests_when_requested`
  - `Component`; methods: `generate`
  - `Component`; methods: none listed
- Public functions: `mock_llm_manager`, `mock_file_tool`
- Internal dependencies: `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/builder.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/generator.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/reporter.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/tester.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/utils.py`
- External / stdlib dependencies: `__future__`, `pathlib`, `pytest`, `typing`, `unittest`
- Used by: no internal dependents detected

## `JNAS_AI_CORE/Builder/generator.py`

- Module name: `JNAS_AI_CORE.Builder.generator`
- Purpose: builder.generator ================== Wraps the existing ``LLMManager`` (and optionally ``ContextBuilder`` / ``CodeAgent``) to generate module source code, unit tests, and prompt artifacts for the Builder Engine. This module does NOT impleme
- Responsibilities:
  - Expose `CodeGenerator` with methods `generate_module_code`, `generate_test_code`, `generate_prompt_artifact`, `generate_init_code`
  - Coordinate with internal modules: `JNAS_AI_CORE/Builder/__init__.py`, `JNAS_AI_CORE/Builder/templates.py`, `JNAS_AI_CORE/Builder/utils.py`
- Public classes:
  - `CodeGenerator`; methods: `generate_module_code`, `generate_test_code`, `generate_prompt_artifact`, `generate_init_code`
- Public functions: none
- Internal dependencies: `JNAS_AI_CORE/Builder/__init__.py`, `JNAS_AI_CORE/Builder/templates.py`, `JNAS_AI_CORE/Builder/utils.py`
- External / stdlib dependencies: `__future__`, `logging`, `typing`
- Used by: `JNAS_AI_CORE/Builder/builder.py`

## `JNAS_AI_CORE/Builder/reporter.py`

- Module name: `JNAS_AI_CORE.Builder.reporter`
- Purpose: builder.reporter ================= Produces build reports (Markdown + in-memory structured data) and prints a human-readable build summary to the console.
- Responsibilities:
  - Expose `BuildReport` with methods `success`, `to_markdown`
  - Expose `BuildReporter` with methods `save_report`, `print_summary`
  - Coordinate with internal modules: `JNAS_AI_CORE/Builder/tester.py`, `JNAS_AI_CORE/Builder/utils.py`
- Public classes:
  - `BuildReport`; methods: `success`, `to_markdown`
  - `BuildReporter`; methods: `save_report`, `print_summary`
- Public functions: none
- Internal dependencies: `JNAS_AI_CORE/Builder/tester.py`, `JNAS_AI_CORE/Builder/utils.py`
- External / stdlib dependencies: `__future__`, `dataclasses`, `datetime`, `logging`, `pathlib`, `typing`
- Used by: `JNAS_AI_CORE/Builder/builder.py`

## `JNAS_AI_CORE/Builder/templates.py`

- Module name: `JNAS_AI_CORE.Builder.templates`
- Purpose: builder.templates ================== Centralized templates used by the Builder Engine: - LLM prompt templates for module/test generation - Static fallback templates used only if the LLM is unreachable (keeps the Builder resilient / producti
- Responsibilities:
  - Expose functions `module_generation_prompt`, `test_generation_prompt`, `prompt_artifact`, `fallback_module_code`, `fallback_test_code`, `init_file_content`
- Public classes: none
- Public functions: `module_generation_prompt`, `test_generation_prompt`, `prompt_artifact`, `fallback_module_code`, `fallback_test_code`, `init_file_content`
- Internal dependencies: none detected
- External / stdlib dependencies: `__future__`
- Used by: `JNAS_AI_CORE/Builder/generator.py`

## `JNAS_AI_CORE/Builder/test_builder_engine.py`

- Module name: `JNAS_AI_CORE.Builder.test_builder_engine`
- Purpose: Unit tests for the Builder Engine (builder/ package). All existing JNAS_AI_CORE components (LLMManager, FileTool, ContextBuilder, etc.) are mocked here so these tests exercise only the Builder Engine's own logic, independent of the real imp
- Responsibilities:
  - Expose `TestStripMarkdownFences` with methods `test_strips_full_fenced_block`, `test_strips_fence_without_language`, `test_returns_clean_text_unchanged`, `test_handles_empty_string`, `test_handles_none`
  - Expose `TestCallFlexible` with methods `test_calls_first_matching_method`, `test_raises_attribute_error_when_no_method_found`, `test_raises_on_none_object`
  - Expose `TestCodeGenerator` with methods `test_requires_llm_manager`, `test_generate_module_code_strips_fences`, `test_generate_module_code_falls_back_on_llm_failure`, `test_generate_test_code_uses_module_code_context`, `test_context_builder_failure_is_non_fatal`
  - Expose `TestTestRunner` with methods `test_parses_passed_counts`, `test_parses_failures`
  - Expose `TestBuildReporter` with methods `test_report_success_property_true_when_no_errors_or_tests`, `test_report_success_property_false_on_generation_error`, `test_report_success_reflects_test_outcome`, `test_to_markdown_contains_module_name`, `test_save_report_writes_file`, `test_print_summary_does_not_raise`
  - Expose `TestBuilderEngine` with methods `test_build_creates_expected_files`, `test_build_rejects_invalid_module_name`, `test_build_requires_llm_manager`, `test_build_runs_tests_when_requested`
  - Expose `Component` with methods `generate`
  - Expose `Component`
  - Expose functions `mock_llm_manager`, `mock_file_tool`
- Public classes:
  - `TestStripMarkdownFences`; methods: `test_strips_full_fenced_block`, `test_strips_fence_without_language`, `test_returns_clean_text_unchanged`, `test_handles_empty_string`, `test_handles_none`
  - `TestCallFlexible`; methods: `test_calls_first_matching_method`, `test_raises_attribute_error_when_no_method_found`, `test_raises_on_none_object`
  - `TestCodeGenerator`; methods: `test_requires_llm_manager`, `test_generate_module_code_strips_fences`, `test_generate_module_code_falls_back_on_llm_failure`, `test_generate_test_code_uses_module_code_context`, `test_context_builder_failure_is_non_fatal`
  - `TestTestRunner`; methods: `test_parses_passed_counts`, `test_parses_failures`
  - `TestBuildReporter`; methods: `test_report_success_property_true_when_no_errors_or_tests`, `test_report_success_property_false_on_generation_error`, `test_report_success_reflects_test_outcome`, `test_to_markdown_contains_module_name`, `test_save_report_writes_file`, `test_print_summary_does_not_raise`
  - `TestBuilderEngine`; methods: `test_build_creates_expected_files`, `test_build_rejects_invalid_module_name`, `test_build_requires_llm_manager`, `test_build_runs_tests_when_requested`
  - `Component`; methods: `generate`
  - `Component`; methods: none listed
- Public functions: `mock_llm_manager`, `mock_file_tool`
- Internal dependencies: none detected
- External / stdlib dependencies: `__future__`, `builder`, `pathlib`, `pytest`, `typing`, `unittest`
- Used by: no internal dependents detected

## `JNAS_AI_CORE/Builder/tester.py`

- Module name: `JNAS_AI_CORE.Builder.tester`
- Purpose: builder.tester ============== Executes pytest against generated modules and captures structured pass/fail results for the Builder Engine's reporting stage.
- Responsibilities:
  - Expose `TestOutcome`
  - Expose `TestRunner` with methods `run`
  - Coordinate with internal modules: `JNAS_AI_CORE/Builder/utils.py`
- Public classes:
  - `TestOutcome`; methods: none listed
  - `TestRunner`; methods: `run`
- Public functions: none
- Internal dependencies: `JNAS_AI_CORE/Builder/utils.py`
- External / stdlib dependencies: `__future__`, `dataclasses`, `logging`, `pathlib`, `re`, `typing`
- Used by: `JNAS_AI_CORE/Builder/builder.py`, `JNAS_AI_CORE/Builder/reporter.py`

## `JNAS_AI_CORE/Builder/utils.py`

- Module name: `JNAS_AI_CORE.Builder.utils`
- Purpose: builder.utils ============= Shared low-level utilities for the Builder Engine. This module provides: - Logger factory - Markdown code-fence stripping - Filesystem helpers (used only as a fallback when ``FileTool`` is unavailable) - A flexib
- Responsibilities:
  - Expose `PytestResult`
  - Expose `LLMManagerProtocol` with methods `generate`
  - Expose `FileToolProtocol` with methods `write_file`, `read_file`
  - Expose `ProjectReaderProtocol` with methods `read`
  - Expose `ProjectScannerProtocol` with methods `scan`
  - Expose `ContextBuilderProtocol` with methods `build`
  - Expose `CodeAgentProtocol` with methods `run`
  - Expose functions `get_logger`, `strip_markdown_fences`, `ensure_dir`, `write_text_file`, `call_flexible`, `run_pytest`
- Public classes:
  - `PytestResult`; methods: none listed
  - `LLMManagerProtocol`; methods: `generate`
  - `FileToolProtocol`; methods: `write_file`, `read_file`
  - `ProjectReaderProtocol`; methods: `read`
  - `ProjectScannerProtocol`; methods: `scan`
  - `ContextBuilderProtocol`; methods: `build`
  - `CodeAgentProtocol`; methods: `run`
- Public functions: `get_logger`, `strip_markdown_fences`, `ensure_dir`, `write_text_file`, `call_flexible`, `run_pytest`
- Internal dependencies: none detected
- External / stdlib dependencies: `__future__`, `dataclasses`, `logging`, `pathlib`, `re`, `subprocess`, `sys`, `typing`
- Used by: `JNAS_AI_CORE/Builder/builder.py`, `JNAS_AI_CORE/Builder/generator.py`, `JNAS_AI_CORE/Builder/reporter.py`, `JNAS_AI_CORE/Builder/tester.py`

## `JNAS_AI_CORE/agent/code_agent.py`

- Module name: `JNAS_AI_CORE.agent.code_agent`
- Purpose: Python module in the current repository; purpose inferred from symbols and dependencies.
- Responsibilities:
  - Expose `CodeAgent` with methods `generate_code`, `create_python_file`
  - Coordinate with internal modules: `JNAS_AI_CORE/llm/context_builder.py`, `JNAS_AI_CORE/llm/manager.py`, `JNAS_AI_CORE/tools/file_tool.py`
- Public classes:
  - `CodeAgent`; methods: `generate_code`, `create_python_file`
- Public functions: none
- Internal dependencies: `JNAS_AI_CORE/llm/context_builder.py`, `JNAS_AI_CORE/llm/manager.py`, `JNAS_AI_CORE/tools/file_tool.py`
- External / stdlib dependencies: none detected
- Used by: `JNAS_AI_CORE/test_agent.py`

## `JNAS_AI_CORE/config/settings.py`

- Module name: `JNAS_AI_CORE.config.settings`
- Purpose: Configuration constants and runtime settings.
- Responsibilities:
  - Contains constants, module-level setup, placeholder code, or package initialization
- Public classes: none
- Public functions: none
- Internal dependencies: none detected
- External / stdlib dependencies: `pathlib`
- Used by: `JNAS_AI_CORE/llm/ollama_client.py`

## `JNAS_AI_CORE/llm/context_builder.py`

- Module name: `JNAS_AI_CORE.llm.context_builder`
- Purpose: Python module in the current repository; purpose inferred from symbols and dependencies.
- Responsibilities:
  - Expose `ContextBuilder` with methods `build`
  - Coordinate with internal modules: `JNAS_AI_CORE/tools/project_reader.py`
- Public classes:
  - `ContextBuilder`; methods: `build`
- Public functions: none
- Internal dependencies: `JNAS_AI_CORE/tools/project_reader.py`
- External / stdlib dependencies: none detected
- Used by: `JNAS_AI_CORE/agent/code_agent.py`, `JNAS_AI_CORE/test_context.py`

## `JNAS_AI_CORE/llm/manager.py`

- Module name: `JNAS_AI_CORE.llm.manager`
- Purpose: Manager/facade module coordinating a lower-level service.
- Responsibilities:
  - Expose `LLMManager` with methods `generate`
  - Coordinate with internal modules: `JNAS_AI_CORE/llm/ollama_client.py`
- Public classes:
  - `LLMManager`; methods: `generate`
- Public functions: none
- Internal dependencies: `JNAS_AI_CORE/llm/ollama_client.py`
- External / stdlib dependencies: none detected
- Used by: `JNAS_AI_CORE/agent/code_agent.py`, `JNAS_AI_CORE/main.py`

## `JNAS_AI_CORE/llm/ollama_client.py`

- Module name: `JNAS_AI_CORE.llm.ollama_client`
- Purpose: Client wrapper for an external service.
- Responsibilities:
  - Expose `OllamaClient` with methods `generate`
  - Serve as an executable entry point or script module
  - Coordinate with internal modules: `JNAS_AI_CORE/config/settings.py`
- Public classes:
  - `OllamaClient`; methods: `generate`
- Public functions: none
- Internal dependencies: `JNAS_AI_CORE/config/settings.py`
- External / stdlib dependencies: `requests`
- Used by: `JNAS_AI_CORE/llm/manager.py`

## `JNAS_AI_CORE/main.py`

- Module name: `JNAS_AI_CORE.main`
- Purpose: Application or command entry point.
- Responsibilities:
  - Expose functions `main`
  - Serve as an executable entry point or script module
  - Coordinate with internal modules: `JNAS_AI_CORE/llm/manager.py`
- Public classes: none
- Public functions: `main`
- Internal dependencies: `JNAS_AI_CORE/llm/manager.py`
- External / stdlib dependencies: none detected
- Used by: no internal dependents detected

## `JNAS_AI_CORE/test_agent.py`

- Module name: `JNAS_AI_CORE.test_agent`
- Purpose: Test module for validating related project behavior.
- Responsibilities:
  - Coordinate with internal modules: `JNAS_AI_CORE/agent/code_agent.py`
- Public classes: none
- Public functions: none
- Internal dependencies: `JNAS_AI_CORE/agent/code_agent.py`
- External / stdlib dependencies: none detected
- Used by: no internal dependents detected

## `JNAS_AI_CORE/test_context.py`

- Module name: `JNAS_AI_CORE.test_context`
- Purpose: Test module for validating related project behavior.
- Responsibilities:
  - Coordinate with internal modules: `JNAS_AI_CORE/llm/context_builder.py`
- Public classes: none
- Public functions: none
- Internal dependencies: `JNAS_AI_CORE/llm/context_builder.py`
- External / stdlib dependencies: none detected
- Used by: no internal dependents detected

## `JNAS_AI_CORE/test_reader.py`

- Module name: `JNAS_AI_CORE.test_reader`
- Purpose: Test module for validating related project behavior.
- Responsibilities:
  - Coordinate with internal modules: `JNAS_AI_CORE/tools/project_reader.py`
- Public classes: none
- Public functions: none
- Internal dependencies: `JNAS_AI_CORE/tools/project_reader.py`
- External / stdlib dependencies: none detected
- Used by: no internal dependents detected

## `JNAS_AI_CORE/test_scanner.py`

- Module name: `JNAS_AI_CORE.test_scanner`
- Purpose: Test module for validating related project behavior.
- Responsibilities:
  - Coordinate with internal modules: `JNAS_AI_CORE/tools/project_scanner.py`
- Public classes: none
- Public functions: none
- Internal dependencies: `JNAS_AI_CORE/tools/project_scanner.py`
- External / stdlib dependencies: none detected
- Used by: no internal dependents detected

## `JNAS_AI_CORE/tools/file_tool.py`

- Module name: `JNAS_AI_CORE.tools.file_tool`
- Purpose: File-system read/write helper.
- Responsibilities:
  - Expose `FileTool` with methods `read`, `write`, `exists`, `list`
- Public classes:
  - `FileTool`; methods: `read`, `write`, `exists`, `list`
- Public functions: none
- Internal dependencies: none detected
- External / stdlib dependencies: `pathlib`
- Used by: `JNAS_AI_CORE/agent/code_agent.py`

## `JNAS_AI_CORE/tools/project_reader.py`

- Module name: `JNAS_AI_CORE.tools.project_reader`
- Purpose: Project/file reading helper.
- Responsibilities:
  - Expose `ProjectReader` with methods `read`, `read_project`
- Public classes:
  - `ProjectReader`; methods: `read`, `read_project`
- Public functions: none
- Internal dependencies: none detected
- External / stdlib dependencies: `pathlib`
- Used by: `JNAS_AI_CORE/llm/context_builder.py`, `JNAS_AI_CORE/test_reader.py`

## `JNAS_AI_CORE/tools/project_scanner.py`

- Module name: `JNAS_AI_CORE.tools.project_scanner`
- Purpose: Project/file scanning helper.
- Responsibilities:
  - Expose `ProjectScanner` with methods `scan`
- Public classes:
  - `ProjectScanner`; methods: `scan`
- Public functions: none
- Internal dependencies: none detected
- External / stdlib dependencies: `pathlib`
- Used by: `JNAS_AI_CORE/test_scanner.py`

## `JNAS_AI_CORE/workspace/logger.py`

- Module name: `JNAS_AI_CORE.workspace.logger`
- Purpose: Logging setup or logging helper.
- Responsibilities:
  - Could not be parsed due to syntax error; responsibilities require manual inspection
- Public classes: none
- Public functions: none
- Internal dependencies: none detected
- External / stdlib dependencies: none detected
- Used by: no internal dependents detected
- Parse status: `unterminated string literal (detected at line 1) at line 1`

## `JNAS_AI_CORE/workspace/test.py`

- Module name: `JNAS_AI_CORE.workspace.test`
- Purpose: Python module in the current repository; purpose inferred from symbols and dependencies.
- Responsibilities:
  - Expose functions `factorial`
- Public classes: none
- Public functions: `factorial`
- Internal dependencies: none detected
- External / stdlib dependencies: none detected
- Used by: no internal dependents detected

## `Scraper-Engine/app.py`

- Module name: `Scraper-Engine.app`
- Purpose: Application or command entry point.
- Responsibilities:
  - Expose functions `save_json`, `save_csv`, `main`
  - Serve as an executable entry point or script module
  - Coordinate with internal modules: `Scraper-Engine/src/cleaner.py`, `Scraper-Engine/src/downloader.py`, `Scraper-Engine/src/logger.py`, `Scraper-Engine/src/parser.py`
- Public classes: none
- Public functions: `save_json`, `save_csv`, `main`
- Internal dependencies: `Scraper-Engine/src/cleaner.py`, `Scraper-Engine/src/downloader.py`, `Scraper-Engine/src/logger.py`, `Scraper-Engine/src/parser.py`
- External / stdlib dependencies: `csv`, `json`, `os`, `sys`
- Used by: no internal dependents detected

## `Scraper-Engine/config/config.py`

- Module name: `Scraper-Engine.config.config`
- Purpose: Configuration constants and runtime settings.
- Responsibilities:
  - Contains constants, module-level setup, placeholder code, or package initialization
- Public classes: none
- Public functions: none
- Internal dependencies: none detected
- External / stdlib dependencies: none detected
- Used by: `Scraper-Engine/src/downloader.py`, `Scraper-Engine/src/logger.py`

## `Scraper-Engine/src/browser.py`

- Module name: `Scraper-Engine.src.browser`
- Purpose: Python module in the current repository; purpose inferred from symbols and dependencies.
- Responsibilities:
  - Contains constants, module-level setup, placeholder code, or package initialization
- Public classes: none
- Public functions: none
- Internal dependencies: none detected
- External / stdlib dependencies: none detected
- Used by: no internal dependents detected

## `Scraper-Engine/src/cleaner.py`

- Module name: `Scraper-Engine.src.cleaner`
- Purpose: Python module in the current repository; purpose inferred from symbols and dependencies.
- Responsibilities:
  - Expose functions `clean_data`
  - Coordinate with internal modules: `Scraper-Engine/src/logger.py`
- Public classes: none
- Public functions: `clean_data`
- Internal dependencies: `Scraper-Engine/src/logger.py`
- External / stdlib dependencies: none detected
- Used by: `Scraper-Engine/app.py`

## `Scraper-Engine/src/cookies.py`

- Module name: `Scraper-Engine.src.cookies`
- Purpose: Python module in the current repository; purpose inferred from symbols and dependencies.
- Responsibilities:
  - Contains constants, module-level setup, placeholder code, or package initialization
- Public classes: none
- Public functions: none
- Internal dependencies: none detected
- External / stdlib dependencies: none detected
- Used by: no internal dependents detected

## `Scraper-Engine/src/downloader.py`

- Module name: `Scraper-Engine.src.downloader`
- Purpose: Python module in the current repository; purpose inferred from symbols and dependencies.
- Responsibilities:
  - Expose functions `download_page`
  - Coordinate with internal modules: `Scraper-Engine/config/config.py`, `Scraper-Engine/src/logger.py`
- Public classes: none
- Public functions: `download_page`
- Internal dependencies: `Scraper-Engine/config/config.py`, `Scraper-Engine/src/logger.py`
- External / stdlib dependencies: `requests`
- Used by: `Scraper-Engine/app.py`

## `Scraper-Engine/src/logger.py`

- Module name: `Scraper-Engine.src.logger`
- Purpose: Logging setup or logging helper.
- Responsibilities:
  - Coordinate with internal modules: `Scraper-Engine/config/config.py`
- Public classes: none
- Public functions: none
- Internal dependencies: `Scraper-Engine/config/config.py`
- External / stdlib dependencies: `logging`, `os`
- Used by: `Scraper-Engine/app.py`, `Scraper-Engine/src/cleaner.py`, `Scraper-Engine/src/downloader.py`, `Scraper-Engine/src/parser.py`

## `Scraper-Engine/src/parser.py`

- Module name: `Scraper-Engine.src.parser`
- Purpose: Python module in the current repository; purpose inferred from symbols and dependencies.
- Responsibilities:
  - Expose functions `parse_html`
  - Coordinate with internal modules: `Scraper-Engine/src/logger.py`
- Public classes: none
- Public functions: `parse_html`
- Internal dependencies: `Scraper-Engine/src/logger.py`
- External / stdlib dependencies: `bs4`
- Used by: `Scraper-Engine/app.py`

## `Scraper-Engine/src/playwright_engine.py`

- Module name: `Scraper-Engine.src.playwright_engine`
- Purpose: Python module in the current repository; purpose inferred from symbols and dependencies.
- Responsibilities:
  - Contains constants, module-level setup, placeholder code, or package initialization
- Public classes: none
- Public functions: none
- Internal dependencies: none detected
- External / stdlib dependencies: none detected
- Used by: no internal dependents detected

## `Scraper-Engine/src/screenshot.py`

- Module name: `Scraper-Engine.src.screenshot`
- Purpose: Python module in the current repository; purpose inferred from symbols and dependencies.
- Responsibilities:
  - Contains constants, module-level setup, placeholder code, or package initialization
- Public classes: none
- Public functions: none
- Internal dependencies: none detected
- External / stdlib dependencies: none detected
- Used by: no internal dependents detected

## `Scraper-Engine/src/waits.py`

- Module name: `Scraper-Engine.src.waits`
- Purpose: Python module in the current repository; purpose inferred from symbols and dependencies.
- Responsibilities:
  - Contains constants, module-level setup, placeholder code, or package initialization
- Public classes: none
- Public functions: none
- Internal dependencies: none detected
- External / stdlib dependencies: none detected
- Used by: no internal dependents detected

## `backend/__init__.py`

- Module name: `backend`
- Purpose: Python module in the current repository; purpose inferred from symbols and dependencies.
- Responsibilities:
  - Contains constants, module-level setup, placeholder code, or package initialization
- Public classes: none
- Public functions: none
- Internal dependencies: none detected
- External / stdlib dependencies: none detected
- Used by: no internal dependents detected

## `backend/main.py`

- Module name: `backend.main`
- Purpose: Application or command entry point.
- Responsibilities:
  - Expose functions `home`, `health`
  - Serve as an executable entry point or script module
- Public classes: none
- Public functions: `home`, `health`
- Internal dependencies: none detected
- External / stdlib dependencies: `fastapi`
- Used by: no internal dependents detected

## `config/settings.py`

- Module name: `config.settings`
- Purpose: Configuration constants and runtime settings.
- Responsibilities:
  - Contains constants, module-level setup, placeholder code, or package initialization
- Public classes: none
- Public functions: none
- Internal dependencies: none detected
- External / stdlib dependencies: none detected
- Used by: no internal dependents detected

## `frontend/app.py`

- Module name: `frontend.app`
- Purpose: Application or command entry point.
- Responsibilities:
  - Serve as an executable entry point or script module
- Public classes: none
- Public functions: none
- Internal dependencies: none detected
- External / stdlib dependencies: none detected
- Used by: no internal dependents detected

## `updater/backup.py`

- Module name: `updater.backup`
- Purpose: Python module in the current repository; purpose inferred from symbols and dependencies.
- Responsibilities:
  - Expose `BackupManager` with methods `create_backup`, `restore`, `list_backups`, `latest_backup`, `delete_backup`, `backup_exists`, `backup_count`, `clear_all`
- Public classes:
  - `BackupManager`; methods: `create_backup`, `restore`, `list_backups`, `latest_backup`, `delete_backup`, `backup_exists`, `backup_count`, `clear_all`
- Public functions: none
- Internal dependencies: none detected
- External / stdlib dependencies: `datetime`, `pathlib`, `shutil`
- Used by: `updater/updater.py`

## `updater/logger.py`

- Module name: `updater.logger`
- Purpose: Logging setup or logging helper.
- Responsibilities:
  - Expose `Logger` with methods `info`, `warning`, `error`, `critical`, `exception`, `debug`, `separator`, `blank`
- Public classes:
  - `Logger`; methods: `info`, `warning`, `error`, `critical`, `exception`, `debug`, `separator`, `blank`
- Public functions: none
- Internal dependencies: none detected
- External / stdlib dependencies: `logging`, `pathlib`
- Used by: `updater/updater.py`

## `updater/parser.py`

- Module name: `updater.parser`
- Purpose: Python module in the current repository; purpose inferred from symbols and dependencies.
- Responsibilities:
  - Expose `ReleaseFile`
  - Expose `Release`
  - Expose `ReleaseParser` with methods `parse`, `get_file`, `has_file`, `file_count`, `list_files`, `summary`, `validate`
- Public classes:
  - `ReleaseFile`; methods: none listed
  - `Release`; methods: none listed
  - `ReleaseParser`; methods: `parse`, `get_file`, `has_file`, `file_count`, `list_files`, `summary`, `validate`
- Public functions: none
- Internal dependencies: none detected
- External / stdlib dependencies: `dataclasses`, `pathlib`
- Used by: `updater/updater.py`

## `updater/updater.py`

- Module name: `updater.updater`
- Purpose: Python module in the current repository; purpose inferred from symbols and dependencies.
- Responsibilities:
  - Expose `Updater` with methods `run`, `process_files`, `update_file`, `file_hash`, `string_hash`, `summary`, `verify`, `rollback`, `install_requirements`, `finish`, `print_header`, `print_footer`, `delete_file`, `create_directory`, `create_empty_file`, `file_exists`, `directory_exists`, `run_post_tasks`, `report`, `execute`
  - Expose functions `main`
  - Serve as an executable entry point or script module
  - Coordinate with internal modules: `updater/backup.py`, `updater/logger.py`, `updater/parser.py`, `updater/validator.py`, `updater/writer.py`
- Public classes:
  - `Updater`; methods: `run`, `process_files`, `update_file`, `file_hash`, `string_hash`, `summary`, `verify`, `rollback`, `install_requirements`, `finish`, `print_header`, `print_footer`, `delete_file`, `create_directory`, `create_empty_file`, `file_exists`, `directory_exists`, `run_post_tasks`, `report`, `execute`
- Public functions: `main`
- Internal dependencies: `updater/backup.py`, `updater/logger.py`, `updater/parser.py`, `updater/validator.py`, `updater/writer.py`
- External / stdlib dependencies: `hashlib`, `pathlib`, `sys`
- Used by: no internal dependents detected

## `updater/utils.py`

- Module name: `updater.utils`
- Purpose: Python module in the current repository; purpose inferred from symbols and dependencies.
- Responsibilities:
  - Expose `Utils` with methods `sha256`, `sha256_text`, `ensure_directory`, `exists`, `read`, `write`, `normalize`, `filename`, `extension`, `filesize`, `is_file`, `is_directory`, `delete`, `touch`
- Public classes:
  - `Utils`; methods: `sha256`, `sha256_text`, `ensure_directory`, `exists`, `read`, `write`, `normalize`, `filename`, `extension`, `filesize`, `is_file`, `is_directory`, `delete`, `touch`
- Public functions: none
- Internal dependencies: none detected
- External / stdlib dependencies: `hashlib`, `os`, `pathlib`
- Used by: no internal dependents detected

## `updater/utlis.py`

- Module name: `updater.utlis`
- Purpose: Python module in the current repository; purpose inferred from symbols and dependencies.
- Responsibilities:
  - Expose `Utils` with methods `sha256`, `sha256_text`, `ensure_directory`, `exists`, `read`, `write`, `normalize`, `filename`, `extension`, `filesize`, `is_file`, `is_directory`, `delete`, `touch`
- Public classes:
  - `Utils`; methods: `sha256`, `sha256_text`, `ensure_directory`, `exists`, `read`, `write`, `normalize`, `filename`, `extension`, `filesize`, `is_file`, `is_directory`, `delete`, `touch`
- Public functions: none
- Internal dependencies: none detected
- External / stdlib dependencies: `hashlib`, `os`, `pathlib`
- Used by: no internal dependents detected

## `updater/validator.py`

- Module name: `updater.validator`
- Purpose: Python module in the current repository; purpose inferred from symbols and dependencies.
- Responsibilities:
  - Expose `Validator` with methods `validate_release`, `validate_file`, `validate_path`, `validate_content`, `validate_all`, `file_exists`, `directory_exists`
- Public classes:
  - `Validator`; methods: `validate_release`, `validate_file`, `validate_path`, `validate_content`, `validate_all`, `file_exists`, `directory_exists`
- Public functions: none
- Internal dependencies: none detected
- External / stdlib dependencies: `pathlib`
- Used by: `updater/updater.py`

## `updater/writer.py`

- Module name: `updater.writer`
- Purpose: File-system read/write helper.
- Responsibilities:
  - Expose `FileWriter` with methods `write`, `append`, `read`, `exists`, `delete`, `mkdir`, `touch`, `copy`, `overwrite`, `write_bytes`, `read_bytes`, `rename`, `move`, `size`, `is_file`, `is_directory`
- Public classes:
  - `FileWriter`; methods: `write`, `append`, `read`, `exists`, `delete`, `mkdir`, `touch`, `copy`, `overwrite`, `write_bytes`, `read_bytes`, `rename`, `move`, `size`, `is_file`, `is_directory`
- Public functions: none
- Internal dependencies: none detected
- External / stdlib dependencies: `pathlib`
- Used by: `updater/updater.py`
=======
# Module Map

This document maps every Python module found in `JNAS_OSV2-main`. Public classes and functions are derived from AST parsing. Dependencies are split into internal repository modules and external/standard-library imports.

## `JNAS_AI_CORE/Builder/__init__.py`

- Module name: `JNAS_AI_CORE.Builder`
- Purpose: Builder Engine v1 for JNAS_AI_CORE. Automatically scaffolds new modules (folder, source file, prompt artifact, and unit tests), using the project's existing LLMManager, FileTool, ProjectReader, ProjectScanner, ContextBuilder, and CodeAgent 
- Responsibilities:
  - Contains constants, module-level setup, placeholder code, or package initialization
- Public classes: none
- Public functions: none
- Internal dependencies: none detected
- External / stdlib dependencies: `__future__`, `builder`, `generator`, `reporter`, `tester`
- Used by: `JNAS_AI_CORE/Builder/generator.py`

## `JNAS_AI_CORE/Builder/builder.py`

- Module name: `JNAS_AI_CORE.Builder.builder`
- Purpose: builder.builder ================ Builder Engine v1 -- orchestrates automatic module generation for JNAS_AI_CORE. Given a module name (e.g. ``planner``), the ``BuilderEngine``: 1. Creates the module folder (if missing). 2. Generates ``__init
- Responsibilities:
  - Expose `BuilderEngine` with methods `build`
  - Expose functions `main`
  - Serve as an executable entry point or script module
  - Coordinate with internal modules: `JNAS_AI_CORE/Builder/generator.py`, `JNAS_AI_CORE/Builder/reporter.py`, `JNAS_AI_CORE/Builder/tester.py`, `JNAS_AI_CORE/Builder/utils.py`
- Public classes:
  - `BuilderEngine`; methods: `build`
- Public functions: `main`
- Internal dependencies: `JNAS_AI_CORE/Builder/generator.py`, `JNAS_AI_CORE/Builder/reporter.py`, `JNAS_AI_CORE/Builder/tester.py`, `JNAS_AI_CORE/Builder/utils.py`
- External / stdlib dependencies: `__future__`, `argparse`, `importlib`, `logging`, `pathlib`, `sys`, `typing`
- Used by: no internal dependents detected

## `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/__init__.py`

- Module name: `JNAS_AI_CORE.Builder.builder_engine_v1.JNAS_AI_CORE.builder`
- Purpose: Builder Engine v1 for JNAS_AI_CORE. Automatically scaffolds new modules (folder, source file, prompt artifact, and unit tests), using the project's existing LLMManager, FileTool, ProjectReader, ProjectScanner, ContextBuilder, and CodeAgent 
- Responsibilities:
  - Contains constants, module-level setup, placeholder code, or package initialization
- Public classes: none
- Public functions: none
- Internal dependencies: none detected
- External / stdlib dependencies: `__future__`, `generator`, `reporter`, `tester`
- Used by: `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/generator.py`

## `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/builder.py`

- Module name: `JNAS_AI_CORE.Builder.builder_engine_v1.JNAS_AI_CORE.builder.builder`
- Purpose: builder.builder ================ Builder Engine v1 -- orchestrates automatic module generation for JNAS_AI_CORE. Given a module name (e.g. ``planner``), the ``BuilderEngine``: 1. Creates the module folder (if missing). 2. Generates ``__init
- Responsibilities:
  - Expose `BuilderEngine` with methods `build`
  - Expose functions `main`
  - Serve as an executable entry point or script module
  - Coordinate with internal modules: `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/generator.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/reporter.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/tester.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/utils.py`
- Public classes:
  - `BuilderEngine`; methods: `build`
- Public functions: `main`
- Internal dependencies: `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/generator.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/reporter.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/tester.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/utils.py`
- External / stdlib dependencies: `__future__`, `argparse`, `importlib`, `logging`, `pathlib`, `sys`, `typing`
- Used by: `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/tests/test_builder_engine.py`

## `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/generator.py`

- Module name: `JNAS_AI_CORE.Builder.builder_engine_v1.JNAS_AI_CORE.builder.generator`
- Purpose: builder.generator ================== Wraps the existing ``LLMManager`` (and optionally ``ContextBuilder`` / ``CodeAgent``) to generate module source code, unit tests, and prompt artifacts for the Builder Engine. This module does NOT impleme
- Responsibilities:
  - Expose `CodeGenerator` with methods `generate_module_code`, `generate_test_code`, `generate_prompt_artifact`, `generate_init_code`
  - Coordinate with internal modules: `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/__init__.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/templates.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/utils.py`
- Public classes:
  - `CodeGenerator`; methods: `generate_module_code`, `generate_test_code`, `generate_prompt_artifact`, `generate_init_code`
- Public functions: none
- Internal dependencies: `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/__init__.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/templates.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/utils.py`
- External / stdlib dependencies: `__future__`, `logging`, `typing`
- Used by: `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/builder.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/tests/test_builder_engine.py`

## `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/reporter.py`

- Module name: `JNAS_AI_CORE.Builder.builder_engine_v1.JNAS_AI_CORE.builder.reporter`
- Purpose: builder.reporter ================= Produces build reports (Markdown + in-memory structured data) and prints a human-readable build summary to the console.
- Responsibilities:
  - Expose `BuildReport` with methods `success`, `to_markdown`
  - Expose `BuildReporter` with methods `save_report`, `print_summary`
  - Coordinate with internal modules: `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/tester.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/utils.py`
- Public classes:
  - `BuildReport`; methods: `success`, `to_markdown`
  - `BuildReporter`; methods: `save_report`, `print_summary`
- Public functions: none
- Internal dependencies: `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/tester.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/utils.py`
- External / stdlib dependencies: `__future__`, `dataclasses`, `datetime`, `logging`, `pathlib`, `typing`
- Used by: `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/builder.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/tests/test_builder_engine.py`

## `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/templates.py`

- Module name: `JNAS_AI_CORE.Builder.builder_engine_v1.JNAS_AI_CORE.builder.templates`
- Purpose: builder.templates ================== Centralized templates used by the Builder Engine: - LLM prompt templates for module/test generation - Static fallback templates used only if the LLM is unreachable (keeps the Builder resilient / producti
- Responsibilities:
  - Expose functions `module_generation_prompt`, `test_generation_prompt`, `prompt_artifact`, `fallback_module_code`, `fallback_test_code`, `init_file_content`
- Public classes: none
- Public functions: `module_generation_prompt`, `test_generation_prompt`, `prompt_artifact`, `fallback_module_code`, `fallback_test_code`, `init_file_content`
- Internal dependencies: none detected
- External / stdlib dependencies: `__future__`
- Used by: `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/generator.py`

## `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/tester.py`

- Module name: `JNAS_AI_CORE.Builder.builder_engine_v1.JNAS_AI_CORE.builder.tester`
- Purpose: builder.tester ============== Executes pytest against generated modules and captures structured pass/fail results for the Builder Engine's reporting stage.
- Responsibilities:
  - Expose `TestOutcome`
  - Expose `TestRunner` with methods `run`
  - Coordinate with internal modules: `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/utils.py`
- Public classes:
  - `TestOutcome`; methods: none listed
  - `TestRunner`; methods: `run`
- Public functions: none
- Internal dependencies: `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/utils.py`
- External / stdlib dependencies: `__future__`, `dataclasses`, `logging`, `pathlib`, `re`, `typing`
- Used by: `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/builder.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/reporter.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/tests/test_builder_engine.py`

## `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/utils.py`

- Module name: `JNAS_AI_CORE.Builder.builder_engine_v1.JNAS_AI_CORE.builder.utils`
- Purpose: builder.utils ============= Shared low-level utilities for the Builder Engine. This module provides: - Logger factory - Markdown code-fence stripping - Filesystem helpers (used only as a fallback when ``FileTool`` is unavailable) - A flexib
- Responsibilities:
  - Expose `PytestResult`
  - Expose `LLMManagerProtocol` with methods `generate`
  - Expose `FileToolProtocol` with methods `write_file`, `read_file`
  - Expose `ProjectReaderProtocol` with methods `read`
  - Expose `ProjectScannerProtocol` with methods `scan`
  - Expose `ContextBuilderProtocol` with methods `build`
  - Expose `CodeAgentProtocol` with methods `run`
  - Expose functions `get_logger`, `strip_markdown_fences`, `ensure_dir`, `write_text_file`, `call_flexible`, `run_pytest`
- Public classes:
  - `PytestResult`; methods: none listed
  - `LLMManagerProtocol`; methods: `generate`
  - `FileToolProtocol`; methods: `write_file`, `read_file`
  - `ProjectReaderProtocol`; methods: `read`
  - `ProjectScannerProtocol`; methods: `scan`
  - `ContextBuilderProtocol`; methods: `build`
  - `CodeAgentProtocol`; methods: `run`
- Public functions: `get_logger`, `strip_markdown_fences`, `ensure_dir`, `write_text_file`, `call_flexible`, `run_pytest`
- Internal dependencies: none detected
- External / stdlib dependencies: `__future__`, `dataclasses`, `logging`, `pathlib`, `re`, `subprocess`, `sys`, `typing`
- Used by: `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/builder.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/generator.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/reporter.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/tester.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/tests/test_builder_engine.py`

## `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/tests/test_builder_engine.py`

- Module name: `JNAS_AI_CORE.Builder.builder_engine_v1.JNAS_AI_CORE.tests.test_builder_engine`
- Purpose: Unit tests for the Builder Engine (builder/ package). All existing JNAS_AI_CORE components (LLMManager, FileTool, ContextBuilder, etc.) are mocked here so these tests exercise only the Builder Engine's own logic, independent of the real imp
- Responsibilities:
  - Expose `TestStripMarkdownFences` with methods `test_strips_full_fenced_block`, `test_strips_fence_without_language`, `test_returns_clean_text_unchanged`, `test_handles_empty_string`, `test_handles_none`
  - Expose `TestCallFlexible` with methods `test_calls_first_matching_method`, `test_raises_attribute_error_when_no_method_found`, `test_raises_on_none_object`
  - Expose `TestCodeGenerator` with methods `test_requires_llm_manager`, `test_generate_module_code_strips_fences`, `test_generate_module_code_falls_back_on_llm_failure`, `test_generate_test_code_uses_module_code_context`, `test_context_builder_failure_is_non_fatal`
  - Expose `TestTestRunner` with methods `test_parses_passed_counts`, `test_parses_failures`
  - Expose `TestBuildReporter` with methods `test_report_success_property_true_when_no_errors_or_tests`, `test_report_success_property_false_on_generation_error`, `test_report_success_reflects_test_outcome`, `test_to_markdown_contains_module_name`, `test_save_report_writes_file`, `test_print_summary_does_not_raise`
  - Expose `TestBuilderEngine` with methods `test_build_creates_expected_files`, `test_build_rejects_invalid_module_name`, `test_build_requires_llm_manager`, `test_build_runs_tests_when_requested`
  - Expose `Component` with methods `generate`
  - Expose `Component`
  - Expose functions `mock_llm_manager`, `mock_file_tool`
  - Coordinate with internal modules: `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/builder.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/generator.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/reporter.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/tester.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/utils.py`
- Public classes:
  - `TestStripMarkdownFences`; methods: `test_strips_full_fenced_block`, `test_strips_fence_without_language`, `test_returns_clean_text_unchanged`, `test_handles_empty_string`, `test_handles_none`
  - `TestCallFlexible`; methods: `test_calls_first_matching_method`, `test_raises_attribute_error_when_no_method_found`, `test_raises_on_none_object`
  - `TestCodeGenerator`; methods: `test_requires_llm_manager`, `test_generate_module_code_strips_fences`, `test_generate_module_code_falls_back_on_llm_failure`, `test_generate_test_code_uses_module_code_context`, `test_context_builder_failure_is_non_fatal`
  - `TestTestRunner`; methods: `test_parses_passed_counts`, `test_parses_failures`
  - `TestBuildReporter`; methods: `test_report_success_property_true_when_no_errors_or_tests`, `test_report_success_property_false_on_generation_error`, `test_report_success_reflects_test_outcome`, `test_to_markdown_contains_module_name`, `test_save_report_writes_file`, `test_print_summary_does_not_raise`
  - `TestBuilderEngine`; methods: `test_build_creates_expected_files`, `test_build_rejects_invalid_module_name`, `test_build_requires_llm_manager`, `test_build_runs_tests_when_requested`
  - `Component`; methods: `generate`
  - `Component`; methods: none listed
- Public functions: `mock_llm_manager`, `mock_file_tool`
- Internal dependencies: `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/builder.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/generator.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/reporter.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/tester.py`, `JNAS_AI_CORE/Builder/builder_engine_v1/JNAS_AI_CORE/builder/utils.py`
- External / stdlib dependencies: `__future__`, `pathlib`, `pytest`, `typing`, `unittest`
- Used by: no internal dependents detected

## `JNAS_AI_CORE/Builder/generator.py`

- Module name: `JNAS_AI_CORE.Builder.generator`
- Purpose: builder.generator ================== Wraps the existing ``LLMManager`` (and optionally ``ContextBuilder`` / ``CodeAgent``) to generate module source code, unit tests, and prompt artifacts for the Builder Engine. This module does NOT impleme
- Responsibilities:
  - Expose `CodeGenerator` with methods `generate_module_code`, `generate_test_code`, `generate_prompt_artifact`, `generate_init_code`
  - Coordinate with internal modules: `JNAS_AI_CORE/Builder/__init__.py`, `JNAS_AI_CORE/Builder/templates.py`, `JNAS_AI_CORE/Builder/utils.py`
- Public classes:
  - `CodeGenerator`; methods: `generate_module_code`, `generate_test_code`, `generate_prompt_artifact`, `generate_init_code`
- Public functions: none
- Internal dependencies: `JNAS_AI_CORE/Builder/__init__.py`, `JNAS_AI_CORE/Builder/templates.py`, `JNAS_AI_CORE/Builder/utils.py`
- External / stdlib dependencies: `__future__`, `logging`, `typing`
- Used by: `JNAS_AI_CORE/Builder/builder.py`

## `JNAS_AI_CORE/Builder/reporter.py`

- Module name: `JNAS_AI_CORE.Builder.reporter`
- Purpose: builder.reporter ================= Produces build reports (Markdown + in-memory structured data) and prints a human-readable build summary to the console.
- Responsibilities:
  - Expose `BuildReport` with methods `success`, `to_markdown`
  - Expose `BuildReporter` with methods `save_report`, `print_summary`
  - Coordinate with internal modules: `JNAS_AI_CORE/Builder/tester.py`, `JNAS_AI_CORE/Builder/utils.py`
- Public classes:
  - `BuildReport`; methods: `success`, `to_markdown`
  - `BuildReporter`; methods: `save_report`, `print_summary`
- Public functions: none
- Internal dependencies: `JNAS_AI_CORE/Builder/tester.py`, `JNAS_AI_CORE/Builder/utils.py`
- External / stdlib dependencies: `__future__`, `dataclasses`, `datetime`, `logging`, `pathlib`, `typing`
- Used by: `JNAS_AI_CORE/Builder/builder.py`

## `JNAS_AI_CORE/Builder/templates.py`

- Module name: `JNAS_AI_CORE.Builder.templates`
- Purpose: builder.templates ================== Centralized templates used by the Builder Engine: - LLM prompt templates for module/test generation - Static fallback templates used only if the LLM is unreachable (keeps the Builder resilient / producti
- Responsibilities:
  - Expose functions `module_generation_prompt`, `test_generation_prompt`, `prompt_artifact`, `fallback_module_code`, `fallback_test_code`, `init_file_content`
- Public classes: none
- Public functions: `module_generation_prompt`, `test_generation_prompt`, `prompt_artifact`, `fallback_module_code`, `fallback_test_code`, `init_file_content`
- Internal dependencies: none detected
- External / stdlib dependencies: `__future__`
- Used by: `JNAS_AI_CORE/Builder/generator.py`

## `JNAS_AI_CORE/Builder/test_builder_engine.py`

- Module name: `JNAS_AI_CORE.Builder.test_builder_engine`
- Purpose: Unit tests for the Builder Engine (builder/ package). All existing JNAS_AI_CORE components (LLMManager, FileTool, ContextBuilder, etc.) are mocked here so these tests exercise only the Builder Engine's own logic, independent of the real imp
- Responsibilities:
  - Expose `TestStripMarkdownFences` with methods `test_strips_full_fenced_block`, `test_strips_fence_without_language`, `test_returns_clean_text_unchanged`, `test_handles_empty_string`, `test_handles_none`
  - Expose `TestCallFlexible` with methods `test_calls_first_matching_method`, `test_raises_attribute_error_when_no_method_found`, `test_raises_on_none_object`
  - Expose `TestCodeGenerator` with methods `test_requires_llm_manager`, `test_generate_module_code_strips_fences`, `test_generate_module_code_falls_back_on_llm_failure`, `test_generate_test_code_uses_module_code_context`, `test_context_builder_failure_is_non_fatal`
  - Expose `TestTestRunner` with methods `test_parses_passed_counts`, `test_parses_failures`
  - Expose `TestBuildReporter` with methods `test_report_success_property_true_when_no_errors_or_tests`, `test_report_success_property_false_on_generation_error`, `test_report_success_reflects_test_outcome`, `test_to_markdown_contains_module_name`, `test_save_report_writes_file`, `test_print_summary_does_not_raise`
  - Expose `TestBuilderEngine` with methods `test_build_creates_expected_files`, `test_build_rejects_invalid_module_name`, `test_build_requires_llm_manager`, `test_build_runs_tests_when_requested`
  - Expose `Component` with methods `generate`
  - Expose `Component`
  - Expose functions `mock_llm_manager`, `mock_file_tool`
- Public classes:
  - `TestStripMarkdownFences`; methods: `test_strips_full_fenced_block`, `test_strips_fence_without_language`, `test_returns_clean_text_unchanged`, `test_handles_empty_string`, `test_handles_none`
  - `TestCallFlexible`; methods: `test_calls_first_matching_method`, `test_raises_attribute_error_when_no_method_found`, `test_raises_on_none_object`
  - `TestCodeGenerator`; methods: `test_requires_llm_manager`, `test_generate_module_code_strips_fences`, `test_generate_module_code_falls_back_on_llm_failure`, `test_generate_test_code_uses_module_code_context`, `test_context_builder_failure_is_non_fatal`
  - `TestTestRunner`; methods: `test_parses_passed_counts`, `test_parses_failures`
  - `TestBuildReporter`; methods: `test_report_success_property_true_when_no_errors_or_tests`, `test_report_success_property_false_on_generation_error`, `test_report_success_reflects_test_outcome`, `test_to_markdown_contains_module_name`, `test_save_report_writes_file`, `test_print_summary_does_not_raise`
  - `TestBuilderEngine`; methods: `test_build_creates_expected_files`, `test_build_rejects_invalid_module_name`, `test_build_requires_llm_manager`, `test_build_runs_tests_when_requested`
  - `Component`; methods: `generate`
  - `Component`; methods: none listed
- Public functions: `mock_llm_manager`, `mock_file_tool`
- Internal dependencies: none detected
- External / stdlib dependencies: `__future__`, `builder`, `pathlib`, `pytest`, `typing`, `unittest`
- Used by: no internal dependents detected

## `JNAS_AI_CORE/Builder/tester.py`

- Module name: `JNAS_AI_CORE.Builder.tester`
- Purpose: builder.tester ============== Executes pytest against generated modules and captures structured pass/fail results for the Builder Engine's reporting stage.
- Responsibilities:
  - Expose `TestOutcome`
  - Expose `TestRunner` with methods `run`
  - Coordinate with internal modules: `JNAS_AI_CORE/Builder/utils.py`
- Public classes:
  - `TestOutcome`; methods: none listed
  - `TestRunner`; methods: `run`
- Public functions: none
- Internal dependencies: `JNAS_AI_CORE/Builder/utils.py`
- External / stdlib dependencies: `__future__`, `dataclasses`, `logging`, `pathlib`, `re`, `typing`
- Used by: `JNAS_AI_CORE/Builder/builder.py`, `JNAS_AI_CORE/Builder/reporter.py`

## `JNAS_AI_CORE/Builder/utils.py`

- Module name: `JNAS_AI_CORE.Builder.utils`
- Purpose: builder.utils ============= Shared low-level utilities for the Builder Engine. This module provides: - Logger factory - Markdown code-fence stripping - Filesystem helpers (used only as a fallback when ``FileTool`` is unavailable) - A flexib
- Responsibilities:
  - Expose `PytestResult`
  - Expose `LLMManagerProtocol` with methods `generate`
  - Expose `FileToolProtocol` with methods `write_file`, `read_file`
  - Expose `ProjectReaderProtocol` with methods `read`
  - Expose `ProjectScannerProtocol` with methods `scan`
  - Expose `ContextBuilderProtocol` with methods `build`
  - Expose `CodeAgentProtocol` with methods `run`
  - Expose functions `get_logger`, `strip_markdown_fences`, `ensure_dir`, `write_text_file`, `call_flexible`, `run_pytest`
- Public classes:
  - `PytestResult`; methods: none listed
  - `LLMManagerProtocol`; methods: `generate`
  - `FileToolProtocol`; methods: `write_file`, `read_file`
  - `ProjectReaderProtocol`; methods: `read`
  - `ProjectScannerProtocol`; methods: `scan`
  - `ContextBuilderProtocol`; methods: `build`
  - `CodeAgentProtocol`; methods: `run`
- Public functions: `get_logger`, `strip_markdown_fences`, `ensure_dir`, `write_text_file`, `call_flexible`, `run_pytest`
- Internal dependencies: none detected
- External / stdlib dependencies: `__future__`, `dataclasses`, `logging`, `pathlib`, `re`, `subprocess`, `sys`, `typing`
- Used by: `JNAS_AI_CORE/Builder/builder.py`, `JNAS_AI_CORE/Builder/generator.py`, `JNAS_AI_CORE/Builder/reporter.py`, `JNAS_AI_CORE/Builder/tester.py`

## `JNAS_AI_CORE/agent/code_agent.py`

- Module name: `JNAS_AI_CORE.agent.code_agent`
- Purpose: Python module in the current repository; purpose inferred from symbols and dependencies.
- Responsibilities:
  - Expose `CodeAgent` with methods `generate_code`, `create_python_file`
  - Coordinate with internal modules: `JNAS_AI_CORE/llm/context_builder.py`, `JNAS_AI_CORE/llm/manager.py`, `JNAS_AI_CORE/tools/file_tool.py`
- Public classes:
  - `CodeAgent`; methods: `generate_code`, `create_python_file`
- Public functions: none
- Internal dependencies: `JNAS_AI_CORE/llm/context_builder.py`, `JNAS_AI_CORE/llm/manager.py`, `JNAS_AI_CORE/tools/file_tool.py`
- External / stdlib dependencies: none detected
- Used by: `JNAS_AI_CORE/test_agent.py`

## `JNAS_AI_CORE/config/settings.py`

- Module name: `JNAS_AI_CORE.config.settings`
- Purpose: Configuration constants and runtime settings.
- Responsibilities:
  - Contains constants, module-level setup, placeholder code, or package initialization
- Public classes: none
- Public functions: none
- Internal dependencies: none detected
- External / stdlib dependencies: `pathlib`
- Used by: `JNAS_AI_CORE/llm/ollama_client.py`

## `JNAS_AI_CORE/llm/context_builder.py`

- Module name: `JNAS_AI_CORE.llm.context_builder`
- Purpose: Python module in the current repository; purpose inferred from symbols and dependencies.
- Responsibilities:
  - Expose `ContextBuilder` with methods `build`
  - Coordinate with internal modules: `JNAS_AI_CORE/tools/project_reader.py`
- Public classes:
  - `ContextBuilder`; methods: `build`
- Public functions: none
- Internal dependencies: `JNAS_AI_CORE/tools/project_reader.py`
- External / stdlib dependencies: none detected
- Used by: `JNAS_AI_CORE/agent/code_agent.py`, `JNAS_AI_CORE/test_context.py`

## `JNAS_AI_CORE/llm/manager.py`

- Module name: `JNAS_AI_CORE.llm.manager`
- Purpose: Manager/facade module coordinating a lower-level service.
- Responsibilities:
  - Expose `LLMManager` with methods `generate`
  - Coordinate with internal modules: `JNAS_AI_CORE/llm/ollama_client.py`
- Public classes:
  - `LLMManager`; methods: `generate`
- Public functions: none
- Internal dependencies: `JNAS_AI_CORE/llm/ollama_client.py`
- External / stdlib dependencies: none detected
- Used by: `JNAS_AI_CORE/agent/code_agent.py`, `JNAS_AI_CORE/main.py`

## `JNAS_AI_CORE/llm/ollama_client.py`

- Module name: `JNAS_AI_CORE.llm.ollama_client`
- Purpose: Client wrapper for an external service.
- Responsibilities:
  - Expose `OllamaClient` with methods `generate`
  - Serve as an executable entry point or script module
  - Coordinate with internal modules: `JNAS_AI_CORE/config/settings.py`
- Public classes:
  - `OllamaClient`; methods: `generate`
- Public functions: none
- Internal dependencies: `JNAS_AI_CORE/config/settings.py`
- External / stdlib dependencies: `requests`
- Used by: `JNAS_AI_CORE/llm/manager.py`

## `JNAS_AI_CORE/main.py`

- Module name: `JNAS_AI_CORE.main`
- Purpose: Application or command entry point.
- Responsibilities:
  - Expose functions `main`
  - Serve as an executable entry point or script module
  - Coordinate with internal modules: `JNAS_AI_CORE/llm/manager.py`
- Public classes: none
- Public functions: `main`
- Internal dependencies: `JNAS_AI_CORE/llm/manager.py`
- External / stdlib dependencies: none detected
- Used by: no internal dependents detected

## `JNAS_AI_CORE/test_agent.py`

- Module name: `JNAS_AI_CORE.test_agent`
- Purpose: Test module for validating related project behavior.
- Responsibilities:
  - Coordinate with internal modules: `JNAS_AI_CORE/agent/code_agent.py`
- Public classes: none
- Public functions: none
- Internal dependencies: `JNAS_AI_CORE/agent/code_agent.py`
- External / stdlib dependencies: none detected
- Used by: no internal dependents detected

## `JNAS_AI_CORE/test_context.py`

- Module name: `JNAS_AI_CORE.test_context`
- Purpose: Test module for validating related project behavior.
- Responsibilities:
  - Coordinate with internal modules: `JNAS_AI_CORE/llm/context_builder.py`
- Public classes: none
- Public functions: none
- Internal dependencies: `JNAS_AI_CORE/llm/context_builder.py`
- External / stdlib dependencies: none detected
- Used by: no internal dependents detected

## `JNAS_AI_CORE/test_reader.py`

- Module name: `JNAS_AI_CORE.test_reader`
- Purpose: Test module for validating related project behavior.
- Responsibilities:
  - Coordinate with internal modules: `JNAS_AI_CORE/tools/project_reader.py`
- Public classes: none
- Public functions: none
- Internal dependencies: `JNAS_AI_CORE/tools/project_reader.py`
- External / stdlib dependencies: none detected
- Used by: no internal dependents detected

## `JNAS_AI_CORE/test_scanner.py`

- Module name: `JNAS_AI_CORE.test_scanner`
- Purpose: Test module for validating related project behavior.
- Responsibilities:
  - Coordinate with internal modules: `JNAS_AI_CORE/tools/project_scanner.py`
- Public classes: none
- Public functions: none
- Internal dependencies: `JNAS_AI_CORE/tools/project_scanner.py`
- External / stdlib dependencies: none detected
- Used by: no internal dependents detected

## `JNAS_AI_CORE/tools/file_tool.py`

- Module name: `JNAS_AI_CORE.tools.file_tool`
- Purpose: File-system read/write helper.
- Responsibilities:
  - Expose `FileTool` with methods `read`, `write`, `exists`, `list`
- Public classes:
  - `FileTool`; methods: `read`, `write`, `exists`, `list`
- Public functions: none
- Internal dependencies: none detected
- External / stdlib dependencies: `pathlib`
- Used by: `JNAS_AI_CORE/agent/code_agent.py`

## `JNAS_AI_CORE/tools/project_reader.py`

- Module name: `JNAS_AI_CORE.tools.project_reader`
- Purpose: Project/file reading helper.
- Responsibilities:
  - Expose `ProjectReader` with methods `read`, `read_project`
- Public classes:
  - `ProjectReader`; methods: `read`, `read_project`
- Public functions: none
- Internal dependencies: none detected
- External / stdlib dependencies: `pathlib`
- Used by: `JNAS_AI_CORE/llm/context_builder.py`, `JNAS_AI_CORE/test_reader.py`

## `JNAS_AI_CORE/tools/project_scanner.py`

- Module name: `JNAS_AI_CORE.tools.project_scanner`
- Purpose: Project/file scanning helper.
- Responsibilities:
  - Expose `ProjectScanner` with methods `scan`
- Public classes:
  - `ProjectScanner`; methods: `scan`
- Public functions: none
- Internal dependencies: none detected
- External / stdlib dependencies: `pathlib`
- Used by: `JNAS_AI_CORE/test_scanner.py`

## `JNAS_AI_CORE/workspace/logger.py`

- Module name: `JNAS_AI_CORE.workspace.logger`
- Purpose: Logging setup or logging helper.
- Responsibilities:
  - Could not be parsed due to syntax error; responsibilities require manual inspection
- Public classes: none
- Public functions: none
- Internal dependencies: none detected
- External / stdlib dependencies: none detected
- Used by: no internal dependents detected
- Parse status: `unterminated string literal (detected at line 1) at line 1`

## `JNAS_AI_CORE/workspace/test.py`

- Module name: `JNAS_AI_CORE.workspace.test`
- Purpose: Python module in the current repository; purpose inferred from symbols and dependencies.
- Responsibilities:
  - Expose functions `factorial`
- Public classes: none
- Public functions: `factorial`
- Internal dependencies: none detected
- External / stdlib dependencies: none detected
- Used by: no internal dependents detected

## `Scraper-Engine/app.py`

- Module name: `Scraper-Engine.app`
- Purpose: Application or command entry point.
- Responsibilities:
  - Expose functions `save_json`, `save_csv`, `main`
  - Serve as an executable entry point or script module
  - Coordinate with internal modules: `Scraper-Engine/src/cleaner.py`, `Scraper-Engine/src/downloader.py`, `Scraper-Engine/src/logger.py`, `Scraper-Engine/src/parser.py`
- Public classes: none
- Public functions: `save_json`, `save_csv`, `main`
- Internal dependencies: `Scraper-Engine/src/cleaner.py`, `Scraper-Engine/src/downloader.py`, `Scraper-Engine/src/logger.py`, `Scraper-Engine/src/parser.py`
- External / stdlib dependencies: `csv`, `json`, `os`, `sys`
- Used by: no internal dependents detected

## `Scraper-Engine/config/config.py`

- Module name: `Scraper-Engine.config.config`
- Purpose: Configuration constants and runtime settings.
- Responsibilities:
  - Contains constants, module-level setup, placeholder code, or package initialization
- Public classes: none
- Public functions: none
- Internal dependencies: none detected
- External / stdlib dependencies: none detected
- Used by: `Scraper-Engine/src/downloader.py`, `Scraper-Engine/src/logger.py`

## `Scraper-Engine/src/browser.py`

- Module name: `Scraper-Engine.src.browser`
- Purpose: Python module in the current repository; purpose inferred from symbols and dependencies.
- Responsibilities:
  - Contains constants, module-level setup, placeholder code, or package initialization
- Public classes: none
- Public functions: none
- Internal dependencies: none detected
- External / stdlib dependencies: none detected
- Used by: no internal dependents detected

## `Scraper-Engine/src/cleaner.py`

- Module name: `Scraper-Engine.src.cleaner`
- Purpose: Python module in the current repository; purpose inferred from symbols and dependencies.
- Responsibilities:
  - Expose functions `clean_data`
  - Coordinate with internal modules: `Scraper-Engine/src/logger.py`
- Public classes: none
- Public functions: `clean_data`
- Internal dependencies: `Scraper-Engine/src/logger.py`
- External / stdlib dependencies: none detected
- Used by: `Scraper-Engine/app.py`

## `Scraper-Engine/src/cookies.py`

- Module name: `Scraper-Engine.src.cookies`
- Purpose: Python module in the current repository; purpose inferred from symbols and dependencies.
- Responsibilities:
  - Contains constants, module-level setup, placeholder code, or package initialization
- Public classes: none
- Public functions: none
- Internal dependencies: none detected
- External / stdlib dependencies: none detected
- Used by: no internal dependents detected

## `Scraper-Engine/src/downloader.py`

- Module name: `Scraper-Engine.src.downloader`
- Purpose: Python module in the current repository; purpose inferred from symbols and dependencies.
- Responsibilities:
  - Expose functions `download_page`
  - Coordinate with internal modules: `Scraper-Engine/config/config.py`, `Scraper-Engine/src/logger.py`
- Public classes: none
- Public functions: `download_page`
- Internal dependencies: `Scraper-Engine/config/config.py`, `Scraper-Engine/src/logger.py`
- External / stdlib dependencies: `requests`
- Used by: `Scraper-Engine/app.py`

## `Scraper-Engine/src/logger.py`

- Module name: `Scraper-Engine.src.logger`
- Purpose: Logging setup or logging helper.
- Responsibilities:
  - Coordinate with internal modules: `Scraper-Engine/config/config.py`
- Public classes: none
- Public functions: none
- Internal dependencies: `Scraper-Engine/config/config.py`
- External / stdlib dependencies: `logging`, `os`
- Used by: `Scraper-Engine/app.py`, `Scraper-Engine/src/cleaner.py`, `Scraper-Engine/src/downloader.py`, `Scraper-Engine/src/parser.py`

## `Scraper-Engine/src/parser.py`

- Module name: `Scraper-Engine.src.parser`
- Purpose: Python module in the current repository; purpose inferred from symbols and dependencies.
- Responsibilities:
  - Expose functions `parse_html`
  - Coordinate with internal modules: `Scraper-Engine/src/logger.py`
- Public classes: none
- Public functions: `parse_html`
- Internal dependencies: `Scraper-Engine/src/logger.py`
- External / stdlib dependencies: `bs4`
- Used by: `Scraper-Engine/app.py`

## `Scraper-Engine/src/playwright_engine.py`

- Module name: `Scraper-Engine.src.playwright_engine`
- Purpose: Python module in the current repository; purpose inferred from symbols and dependencies.
- Responsibilities:
  - Contains constants, module-level setup, placeholder code, or package initialization
- Public classes: none
- Public functions: none
- Internal dependencies: none detected
- External / stdlib dependencies: none detected
- Used by: no internal dependents detected

## `Scraper-Engine/src/screenshot.py`

- Module name: `Scraper-Engine.src.screenshot`
- Purpose: Python module in the current repository; purpose inferred from symbols and dependencies.
- Responsibilities:
  - Contains constants, module-level setup, placeholder code, or package initialization
- Public classes: none
- Public functions: none
- Internal dependencies: none detected
- External / stdlib dependencies: none detected
- Used by: no internal dependents detected

## `Scraper-Engine/src/waits.py`

- Module name: `Scraper-Engine.src.waits`
- Purpose: Python module in the current repository; purpose inferred from symbols and dependencies.
- Responsibilities:
  - Contains constants, module-level setup, placeholder code, or package initialization
- Public classes: none
- Public functions: none
- Internal dependencies: none detected
- External / stdlib dependencies: none detected
- Used by: no internal dependents detected

## `backend/__init__.py`

- Module name: `backend`
- Purpose: Python module in the current repository; purpose inferred from symbols and dependencies.
- Responsibilities:
  - Contains constants, module-level setup, placeholder code, or package initialization
- Public classes: none
- Public functions: none
- Internal dependencies: none detected
- External / stdlib dependencies: none detected
- Used by: no internal dependents detected

## `backend/main.py`

- Module name: `backend.main`
- Purpose: Application or command entry point.
- Responsibilities:
  - Expose functions `home`, `health`
  - Serve as an executable entry point or script module
- Public classes: none
- Public functions: `home`, `health`
- Internal dependencies: none detected
- External / stdlib dependencies: `fastapi`
- Used by: no internal dependents detected

## `config/settings.py`

- Module name: `config.settings`
- Purpose: Configuration constants and runtime settings.
- Responsibilities:
  - Contains constants, module-level setup, placeholder code, or package initialization
- Public classes: none
- Public functions: none
- Internal dependencies: none detected
- External / stdlib dependencies: none detected
- Used by: no internal dependents detected

## `frontend/app.py`

- Module name: `frontend.app`
- Purpose: Application or command entry point.
- Responsibilities:
  - Serve as an executable entry point or script module
- Public classes: none
- Public functions: none
- Internal dependencies: none detected
- External / stdlib dependencies: none detected
- Used by: no internal dependents detected

## `updater/backup.py`

- Module name: `updater.backup`
- Purpose: Python module in the current repository; purpose inferred from symbols and dependencies.
- Responsibilities:
  - Expose `BackupManager` with methods `create_backup`, `restore`, `list_backups`, `latest_backup`, `delete_backup`, `backup_exists`, `backup_count`, `clear_all`
- Public classes:
  - `BackupManager`; methods: `create_backup`, `restore`, `list_backups`, `latest_backup`, `delete_backup`, `backup_exists`, `backup_count`, `clear_all`
- Public functions: none
- Internal dependencies: none detected
- External / stdlib dependencies: `datetime`, `pathlib`, `shutil`
- Used by: `updater/updater.py`

## `updater/logger.py`

- Module name: `updater.logger`
- Purpose: Logging setup or logging helper.
- Responsibilities:
  - Expose `Logger` with methods `info`, `warning`, `error`, `critical`, `exception`, `debug`, `separator`, `blank`
- Public classes:
  - `Logger`; methods: `info`, `warning`, `error`, `critical`, `exception`, `debug`, `separator`, `blank`
- Public functions: none
- Internal dependencies: none detected
- External / stdlib dependencies: `logging`, `pathlib`
- Used by: `updater/updater.py`

## `updater/parser.py`

- Module name: `updater.parser`
- Purpose: Python module in the current repository; purpose inferred from symbols and dependencies.
- Responsibilities:
  - Expose `ReleaseFile`
  - Expose `Release`
  - Expose `ReleaseParser` with methods `parse`, `get_file`, `has_file`, `file_count`, `list_files`, `summary`, `validate`
- Public classes:
  - `ReleaseFile`; methods: none listed
  - `Release`; methods: none listed
  - `ReleaseParser`; methods: `parse`, `get_file`, `has_file`, `file_count`, `list_files`, `summary`, `validate`
- Public functions: none
- Internal dependencies: none detected
- External / stdlib dependencies: `dataclasses`, `pathlib`
- Used by: `updater/updater.py`

## `updater/updater.py`

- Module name: `updater.updater`
- Purpose: Python module in the current repository; purpose inferred from symbols and dependencies.
- Responsibilities:
  - Expose `Updater` with methods `run`, `process_files`, `update_file`, `file_hash`, `string_hash`, `summary`, `verify`, `rollback`, `install_requirements`, `finish`, `print_header`, `print_footer`, `delete_file`, `create_directory`, `create_empty_file`, `file_exists`, `directory_exists`, `run_post_tasks`, `report`, `execute`
  - Expose functions `main`
  - Serve as an executable entry point or script module
  - Coordinate with internal modules: `updater/backup.py`, `updater/logger.py`, `updater/parser.py`, `updater/validator.py`, `updater/writer.py`
- Public classes:
  - `Updater`; methods: `run`, `process_files`, `update_file`, `file_hash`, `string_hash`, `summary`, `verify`, `rollback`, `install_requirements`, `finish`, `print_header`, `print_footer`, `delete_file`, `create_directory`, `create_empty_file`, `file_exists`, `directory_exists`, `run_post_tasks`, `report`, `execute`
- Public functions: `main`
- Internal dependencies: `updater/backup.py`, `updater/logger.py`, `updater/parser.py`, `updater/validator.py`, `updater/writer.py`
- External / stdlib dependencies: `hashlib`, `pathlib`, `sys`
- Used by: no internal dependents detected

## `updater/utils.py`

- Module name: `updater.utils`
- Purpose: Python module in the current repository; purpose inferred from symbols and dependencies.
- Responsibilities:
  - Expose `Utils` with methods `sha256`, `sha256_text`, `ensure_directory`, `exists`, `read`, `write`, `normalize`, `filename`, `extension`, `filesize`, `is_file`, `is_directory`, `delete`, `touch`
- Public classes:
  - `Utils`; methods: `sha256`, `sha256_text`, `ensure_directory`, `exists`, `read`, `write`, `normalize`, `filename`, `extension`, `filesize`, `is_file`, `is_directory`, `delete`, `touch`
- Public functions: none
- Internal dependencies: none detected
- External / stdlib dependencies: `hashlib`, `os`, `pathlib`
- Used by: no internal dependents detected

## `updater/utlis.py`

- Module name: `updater.utlis`
- Purpose: Python module in the current repository; purpose inferred from symbols and dependencies.
- Responsibilities:
  - Expose `Utils` with methods `sha256`, `sha256_text`, `ensure_directory`, `exists`, `read`, `write`, `normalize`, `filename`, `extension`, `filesize`, `is_file`, `is_directory`, `delete`, `touch`
- Public classes:
  - `Utils`; methods: `sha256`, `sha256_text`, `ensure_directory`, `exists`, `read`, `write`, `normalize`, `filename`, `extension`, `filesize`, `is_file`, `is_directory`, `delete`, `touch`
- Public functions: none
- Internal dependencies: none detected
- External / stdlib dependencies: `hashlib`, `os`, `pathlib`
- Used by: no internal dependents detected

## `updater/validator.py`

- Module name: `updater.validator`
- Purpose: Python module in the current repository; purpose inferred from symbols and dependencies.
- Responsibilities:
  - Expose `Validator` with methods `validate_release`, `validate_file`, `validate_path`, `validate_content`, `validate_all`, `file_exists`, `directory_exists`
- Public classes:
  - `Validator`; methods: `validate_release`, `validate_file`, `validate_path`, `validate_content`, `validate_all`, `file_exists`, `directory_exists`
- Public functions: none
- Internal dependencies: none detected
- External / stdlib dependencies: `pathlib`
- Used by: `updater/updater.py`

## `updater/writer.py`

- Module name: `updater.writer`
- Purpose: File-system read/write helper.
- Responsibilities:
  - Expose `FileWriter` with methods `write`, `append`, `read`, `exists`, `delete`, `mkdir`, `touch`, `copy`, `overwrite`, `write_bytes`, `read_bytes`, `rename`, `move`, `size`, `is_file`, `is_directory`
- Public classes:
  - `FileWriter`; methods: `write`, `append`, `read`, `exists`, `delete`, `mkdir`, `touch`, `copy`, `overwrite`, `write_bytes`, `read_bytes`, `rename`, `move`, `size`, `is_file`, `is_directory`
- Public functions: none
- Internal dependencies: none detected
- External / stdlib dependencies: `pathlib`
- Used by: `updater/updater.py`
>>>>>>> d3aaca4f603cf5fe37898156986c9973ca77d20c
