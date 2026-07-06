try:
    from JNAS_AI_CORE.llm.manager import LLMManager
    from JNAS_AI_CORE.llm.context_builder import ContextBuilder
    from JNAS_AI_CORE.tools.file_tool import FileTool
except ImportError:
    from llm.manager import LLMManager
    from llm.context_builder import ContextBuilder
    from tools.file_tool import FileTool


class CodeAgent:

    def __init__(self):

        self.llm = LLMManager()
        self.context = ContextBuilder()
        self.files = FileTool()

    def generate_code(self, task):

        prompt = self.context.build(task)

        return self.llm.generate(prompt)

    def create_python_file(self, filename, task):

        code = self.generate_code(task)

        code = code.replace("```python", "")
        code = code.replace("```", "")
        code = code.strip()

        self.files.write(filename, code)

        print(f"Saved: {filename}")

        return filename
