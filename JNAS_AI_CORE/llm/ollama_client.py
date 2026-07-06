import requests

try:
    from JNAS_AI_CORE.config.settings import (
        OLLAMA_HOST,
        DEFAULT_MODEL
    )
except ImportError:
    from config.settings import (
        OLLAMA_HOST,
        DEFAULT_MODEL
    )


class OllamaClient:

    def __init__(self):
        self.url = f"{OLLAMA_HOST}/api/generate"

    def generate(self, prompt, model=DEFAULT_MODEL):

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }

        response = requests.post(
            self.url,
            json=payload,
            timeout=300
        )

        response.raise_for_status()

        return response.json()["response"]


if __name__ == "__main__":

    client = OllamaClient()

    print(
        client.generate(
            "Say Hello from JNAS AI Core"
        )
    )
