from llm.ollama_client import OllamaClient


class LLMManager:

    def __init__(self, provider="ollama"):

        self.provider = provider

        self.ollama = OllamaClient()

    def generate(self, prompt):

        if self.provider == "ollama":
            return self.ollama.generate(prompt)

        raise Exception(f"Unknown provider: {self.provider}")
