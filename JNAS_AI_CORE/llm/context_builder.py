try:
    from JNAS_AI_CORE.tools.project_reader import ProjectReader
except ImportError:
    from tools.project_reader import ProjectReader


class ContextBuilder:

    def __init__(self):
        self.reader = ProjectReader()

    def build(self, task):

        project = self.reader.read_project()

        context = ""

        for file, code in project.items():

            context += f"\nFILE: {file}\n"
            context += code
            context += "\n"

        prompt = f"""
You are the AI core of JNAS.

Below is the current project.

{context}

User Request:

{task}

Modify or create code while keeping compatibility with the existing project.
Return ONLY code.
"""

        return prompt
