class ExecutionPlan:
    def create_plan(self, project_goal: str) -> list:
        plan = [
            {"name": "step1", "description": "First step"},
            {"name": "step2", "description": "Second step"},
            {"name": "failed_step", "description": "A step that fails"}
        ]
        return plan
