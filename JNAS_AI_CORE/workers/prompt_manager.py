"""Prompt construction for autonomous code generation."""

from __future__ import annotations


class PromptManager:
    """Build strict prompts for file-by-file code generation."""

    FORMAT_RULES = """You are generating production code for JNAS_AI_CORE.
Never ask for confirmation.
Never ask "continue?"
Never stop after one file.
Continue until every requested file is generated.
Return only code content wrapped in file markers.
Do not include markdown fences or explanations.
Use this exact format for every file:
===FILE:relative/path.py===
<file content>
===END===
"""

    def build_generation_prompt(
        self,
        instruction: str,
        project_context: str = "",
        target_root: str = ".",
    ) -> str:
        """Build the initial generation prompt."""
        context = f"\nProject context:\n{project_context}\n" if project_context else ""
        return (
            f"{self.FORMAT_RULES}\n"
            f"Target root: {target_root}\n"
            f"{context}\n"
            f"User request:\n{instruction}\n"
        )

    def build_fix_prompt(
        self,
        original_prompt: str,
        compiler_output: str,
        previous_files: list[str],
    ) -> str:
        """Build a correction prompt using compiler feedback."""
        files = "\n".join(previous_files)
        return (
            f"{self.FORMAT_RULES}\n"
            "The generated project failed compile validation.\n"
            "Return corrected complete files using the same file markers.\n\n"
            f"Original prompt:\n{original_prompt}\n\n"
            f"Generated files:\n{files}\n\n"
            f"Compiler output:\n{compiler_output}\n"
        )
