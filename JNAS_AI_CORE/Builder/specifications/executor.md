
# EXECUTOR Specification

IMPORTANT

Do NOT generate a Hello application.

Do NOT generate greet().

Do NOT generate --name.

The project MUST implement an execution engine.

Build an execution engine that runs tasks from a Planner.


Language: Python

Project Structure:
- README.md
- requirements.txt
- src/
  - __init__.py
  - main.py
- tests/
  - test_main.py

Required Classes:
- Executor
- ExecutionTask
- ExecutionResult

Required Functions:
- execute_task()
- execute_plan()
- main(argv=None)

CLI:
python main.py --goal "Execute plan"

Tests MUST import:
from src.main import Executor, ExecutionTask, ExecutionResult

Requirements:
- Execute tasks sequentially
- Track execution status
- Handle failures
- Retry failed tasks
- Generate execution report

Never:
- Generate Hello application
- Generate placeholder code
- Generate non-Python files
