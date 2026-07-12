# PLANNER Specification

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
- Planner
- Task
- Plan

Required Functions:
- create_plan(goal)
- execute_plan(plan)
- main(argv=None)

CLI:
python main.py --goal "Build AI Agent"

Tests MUST import:
from src.main import Planner, Task, Plan

Requirements:
- Task planning
- Ordered execution
- Dependency handling
- Plan serialization
- CLI interface

Never:
- Generate Hello application
- Generate placeholder code
- Generate non-Python files
