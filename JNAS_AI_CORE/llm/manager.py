from JNAS_AI_CORE.llm_router.router import LLMRouter


class LLMManager:

    def __init__(self):
        self.router = LLMRouter()

    def generate(self, prompt, capability="general"):
        result = self.router.route(
            prompt,
            capability=capability
        )

        if not result.success:
            raise Exception(result.error)

        return result.response
