To address your request to create a reusable Python logger class, we'll follow these steps:

1. **Generate the Code**: Use `CodeAgent` to generate the logger class based on the provided task.
2. **Save the File**: Save the generated logger class in the workspace directory.

Let's go through each step with the necessary code modifications and additions.

### Step 1: Generate the Logger Class

We'll use the `CodeAgent` to generate the required logger class. The task is "Create a reusable Python logger class."

Here’s how we can modify your existing setup:

#### Modify `test_agent.py`


from agent.code_agent import CodeAgent

def main():
    # Create an instance of CodeAgent
    code_agent = CodeAgent()

    # Generate the logger class
    task = "Create a reusable Python logger class."
    code = code_agent.generate_code(task)

    print("Generated Logger Class:")
    print(code)
    
if __name__ == "__main__":
    main()


#### Modify `code_agent.py` (If needed to generate context for the prompt)

Ensure that the `generate_code` method in `CodeAgent` can handle the task of creating a reusable logger class.


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
        code = code.replace("", "")
        code = code.replace("", "")
        code = code.strip()

        self.files.write(filename, code)

        print(f"Saved: {filename}")

        return filename


#### Modify `context_builder.py` (If needed to handle the task context)

Ensure that the `build` method in `ContextBuilder` can generate a proper prompt.


from tools.project_reader import ProjectReader

class ContextBuilder:

    def __init__(self):
        self.reader = ProjectReader()

    def build(self, task):

        project = self.reader.read_project()

        context = ""

        for file, code in project.items():
            if ".py" in file:  # Ensure only .py files are included
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


### Step 2: Save the Logger Class

The `create_python_file` method in `CodeAgent` will handle saving the generated logger class to a file.

#### Example of Generated Logger Class

Here is an example of what the generated logger class might look like:


class Logger:
    def __init__(self, name):
        self.name = name

    def log(self, message, level='INFO'):
        print(f"[{self.name} {level.upper()}] {message}")

# Usage Example:
# logger = Logger('my_logger')
# logger.log('This is an info message', level='INFO')


### Run the Code

Run `test_agent.py`:

sh
python test_agent.py


You should see the generated logger class printed in the console. This script will generate a reusable Python logger class and save it to the specified workspace directory.

If everything is set up correctly, you can now use this generated logger class within your project or modify it as needed.