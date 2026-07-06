from llm.manager import LLMManager


def main():

    print("=" * 50)
    print("JNAS AI CORE v0.2")
    print("=" * 50)

    llm = LLMManager()

    while True:

        prompt = input("\nYou > ").strip()

        if prompt.lower() in ["exit", "quit"]:
            print("Bye...")
            break

        if not prompt:
            continue

        try:
            response = llm.generate(prompt)

            print("\nAI >")
            print(response)

        except Exception as e:
            print(f"\nERROR: {e}")


if __name__ == "__main__":
    main()
