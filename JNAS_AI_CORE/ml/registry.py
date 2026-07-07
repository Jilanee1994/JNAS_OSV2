"""Tool Registry integration for ML models."""

from __future__ import annotations

from typing import Any

try:
    from JNAS_AI_CORE.registry.metadata import ToolMetadata
except ImportError:
    ToolMetadata = None


class MLModelTool:
    """Expose a trained ML model as a Tool Registry-compatible tool."""

    def __init__(self, model_name: str, predictor: Any, version: str | None = None) -> None:
        self.model_name = model_name
        self.predictor = predictor
        self.version = version
        self.metadata = self._metadata()

    def initialize(self) -> None:
        """Prepare the model tool."""

    def execute(self, payload: Any) -> list[Any]:
        """Run model prediction through the registry tool interface."""
        rows = payload.get("rows", payload) if isinstance(payload, dict) else payload
        return self.predictor.predict(self.model_name, list(rows), self.version)

    def validate(self) -> bool:
        """Validate tool readiness."""
        return self.predictor is not None

    def shutdown(self) -> None:
        """Release model tool resources."""

    def _metadata(self) -> Any:
        if ToolMetadata is None:
            return None
        return ToolMetadata(
            tool_id=f"ml_model_{self.model_name}",
            name=f"ML Model: {self.model_name}",
            description=f"Prediction tool for ML model {self.model_name}.",
            version=self.version or "latest",
            author="JNAS_AI_CORE",
            category="ml",
            supported_tasks=["ml_prediction", "classification", "decision_support"],
            input_types=["list[dict]", "dict"],
            output_types=["list"],
            enabled=True,
            priority=50,
        )


class MLRegistry:
    """Register trained ML models into the existing Tool Registry."""

    def __init__(self, tool_registry: Any | None = None) -> None:
        self.tool_registry = tool_registry

    def register_model(self, model_name: str, predictor: Any, version: str | None = None) -> MLModelTool:
        """Create and optionally register an ML model tool."""
        tool = MLModelTool(model_name, predictor, version)
        if self.tool_registry is not None:
            self.tool_registry.register_tool(tool)
        return tool
