from .main import BuildAgent, ExecutionPlan

def test_build_agent():
    agent = BuildAgent()
    plan = agent.create_execution_plan("test_goal")
    assert isinstance(plan, ExecutionPlan)
