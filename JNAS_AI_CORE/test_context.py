try:
    from JNAS_AI_CORE.llm.context_builder import ContextBuilder
except ImportError:
    from llm.context_builder import ContextBuilder

def main():
    builder = ContextBuilder()

    prompt = builder.build(
        "Add logging support to main.py"
    )

    print(prompt[:3000])


if __name__ == "__main__":
    main()
