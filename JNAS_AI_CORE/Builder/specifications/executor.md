# EXECUTOR Specification

Build an execution engine that executes tasks produced by the Planner.

Language: Python

Project Structure:
- README.md
- requirements.txt
- src/
    - __init__.py
    - main.py
    - execution_engine.py
- tests/
    - test_main.py

Required Classes:

ExecutionTask
- Represents a single executable task.
- __init__(...)

ExecutionResult
- Stores execution status and execution report.
- __init__(...)

Executor
- __init__()
- execute_task(task)
- execute_plan(plan)

Rules:

- execute_task() MUST be a method of Executor.
- execute_plan() MUST be a method of Executor.
- Do NOT create standalone execute_task() functions.
- Do NOT create standalone execute_plan() functions.
- Only one __init__() per class.
- Do not duplicate classes.
- Do not duplicate methods.

CLI

main(argv=None)

The CLI must:

- Accept --goal
- Build an Executor
- Execute a plan
- Print an execution report

Tests MUST import:

from src.main import Executor, ExecutionTask, ExecutionResult

Requirements

- Execute tasks sequentially.
- Track execution status.
- Retry failed tasks.
- Handle execution failures.
- Return ExecutionResult.
- Generate an execution report.

Never

- Generate Hello application.
- Generate placeholder code.
- Generate pass.
- Generate NotImplementedError.
- Generate duplicate __init__ methods.
- Generate duplicate execute_task methods.
- Generate duplicate execute_plan methods.
- Generate standalone helper functions for execute_task or execute_plan.
- Generate non-Python files.