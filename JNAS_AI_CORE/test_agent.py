try:
    from JNAS_AI_CORE.agent.code_agent import CodeAgent
except ImportError:
    from agent.code_agent import CodeAgent

def main():
    agent = CodeAgent()

    agent.create_python_file(
        "workspace/logger.py",
        "Create a reusable Python logger class."
    )

    print("Done")


if __name__ == "__main__":
    main()
