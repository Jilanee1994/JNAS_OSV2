from llm.context_builder import ContextBuilder

builder = ContextBuilder()

prompt = builder.build(
    "Add logging support to main.py"
)

print(prompt[:3000])
