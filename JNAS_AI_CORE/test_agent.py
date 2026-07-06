from agent.code_agent import CodeAgent

agent = CodeAgent()

agent.create_python_file(
    "workspace/logger.py",
    "Create a reusable Python logger class."
)

print("Done")
