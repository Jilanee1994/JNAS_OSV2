"""Project creation stage for Builder Agent V3."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

try:
    from JNAS_AI_CORE.planner import Planner
except ImportError:
    Planner = None

from .llm_interface import BuilderLLMClient
from .project_spec import ProjectFile, ProjectSpec
from .specification_validator import SpecificationValidator


class ProjectCreator:
    """Create a project specification from a user prompt."""

    def __init__(
        self,
        llm_client: BuilderLLMClient,
        planner: Any | None = None,
        specification_validator: SpecificationValidator | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self.llm_client = llm_client
        self.planner = planner if planner is not None else (Planner() if Planner is not None else None)
        self.specification_validator = specification_validator or SpecificationValidator()
        self.logger = logger or logging.getLogger(__name__)

    def create(self, user_prompt: str) -> tuple[ProjectSpec, str]:
        """Create a ProjectSpec and return it with the plan id."""
        self.logger.info("Planner Started.")
        plan_id = ""
        plan_summary = ""
        if self.planner is not None:
            plan = self.planner.create_plan(user_prompt)
            plan_id = str(getattr(plan, "plan_id", ""))
            plan_summary = str(getattr(plan, "goal", user_prompt))
        self.logger.info("Planner Finished.")
        self.logger.info("Project Specification Started.")
        expected = self.specification_validator.expected_from_prompt(user_prompt)
        response = self.llm_client.generate(self._structure_prompt(user_prompt, plan_summary))
        spec = self._parse_spec(user_prompt, response.content)
        if expected is not None:
            validation = self.specification_validator.validate_project_spec(expected, spec)
            if not validation.success:
                self.logger.warning("Project specification rejected: %s", validation.to_message())
                spec = expected.to_project_spec()
        self.logger.info("Project Specification Finished.")
        return spec, plan_id

    def _structure_prompt(self, user_prompt: str, plan_summary: str) -> str:
        return (
            "Create a compact JSON project specification for the JNAS Builder Agent.\n"
            "Return only JSON with fields: name, slug, description, files.\n"
            "Each file must have path, purpose, and kind.\n"
            "Prefer the smallest useful Python project that satisfies the prompt.\n"
            "For a hello project, include hello.py and tests/test_hello.py.\n\n"
            f"User prompt: {user_prompt}\n"
            f"Plan summary: {plan_summary or user_prompt}\n"
        )

    def _parse_spec(self, user_prompt: str, content: str) -> ProjectSpec:
        try:
            data = json.loads(self._clean_json(content))
            return ProjectSpec.from_input(data)
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            return self._fallback_spec(user_prompt)

    def _clean_json(self, content: str) -> str:
        cleaned = content.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned.removeprefix("```json").strip()
        elif cleaned.startswith("```"):
            cleaned = cleaned.removeprefix("```").strip()
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3].strip()
        return cleaned

    def _fallback_spec(self, user_prompt: str) -> ProjectSpec:
        name = user_prompt.replace("Build ", "", 1).strip() or "JNAS Project"
        slug = "hello_project" if "hello" in user_prompt.lower() else ProjectSpec.from_input(name).slug
        if "hello" in user_prompt.lower():
            return ProjectSpec(
                name=name,
                slug=slug,
                description=user_prompt,
                files=[
                    ProjectFile(Path("README.md"), "Project overview.", "markdown"),
                    ProjectFile(Path("requirements.txt"), "Project dependencies.", "text"),
                    ProjectFile(Path("hello.py"), "Hello project implementation.", "python"),
                    ProjectFile(Path("tests") / "test_hello.py", "Pytest coverage for hello.py.", "python"),
                ],
            )
        return ProjectSpec.from_input({"name": name, "description": user_prompt})
