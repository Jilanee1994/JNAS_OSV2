# BUILD_AGENT Specification


Build an orchestration agent for generating projects.

The agent must create an execution plan, invoke a builder step, produce a build report, handle retries, and provide a command-line interface.


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
- BuildAgent
- ExecutionPlan
- BuildReport

Required Functions:
- create_execution_plan()
- run_build()
- main(argv=None)

CLI:
python main.py --goal "Build a project" --retries 1

Tests MUST import:
from src.main import BuildAgent, ExecutionPlan, BuildReport

Requirements:
- Planner
- Executor
- Retry support
- Build report
- Workflow
- Queue

Never:
- Generate hello.py
- Generate Go, Java, Rust, C#, C++, JS, TS, PHP, Swift files
- Invent different class names
