"""AI OS decision engine."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from .rules import RulesEngine


@dataclass(frozen=True)
class DecisionResult:
    """Result from the decision engine."""

    source: str
    result: Any
    confidence: float


class DecisionEngine:
    """Route work through rules, ML, LLM router, executor, and self-healing."""

    def __init__(
        self,
        rules_engine: RulesEngine | None = None,
        ml_predictor: Any | None = None,
        llm_router: Any | None = None,
        executor: Any | None = None,
        self_healing: Any | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self.rules_engine = rules_engine or RulesEngine()
        self.ml_predictor = ml_predictor
        self.llm_router = llm_router
        self.executor = executor
        self.self_healing = self_healing
        self.logger = logger or logging.getLogger("JNAS_AI_CORE.decision_engine")

    def decide(self, task: dict[str, Any]) -> DecisionResult:
        """Choose the cheapest reliable decision path."""
        rule_result = self.rules_engine.decide(task)
        if rule_result is not None:
            return DecisionResult("rules", rule_result, 1.0)

        ml_result = self._try_ml(task)
        if ml_result is not None and ml_result.confidence >= float(task.get("confidence_threshold", 0.75)):
            return ml_result

        if self.llm_router is not None:
            prompt = str(task.get("prompt") or task.get("description") or task)
            routed = self.llm_router.route(prompt, capability=str(task.get("capability", "general")))
            return DecisionResult("llm_router", routed, 1.0 if routed.success else 0.0)

        if self.executor is not None and "plan" in task:
            try:
                return DecisionResult("executor", self.executor.execute_plan(task["plan"]), 1.0)
            except Exception as exc:
                if self.self_healing is not None:
                    return DecisionResult("self_healing", self.self_healing.recover(exc), 0.5)
                raise

        return DecisionResult("unresolved", None, 0.0)

    def _try_ml(self, task: dict[str, Any]) -> DecisionResult | None:
        if self.ml_predictor is None or "model_name" not in task or "rows" not in task:
            return None
        predictions = self.ml_predictor.predict(task["model_name"], task["rows"], task.get("version"))
        confidence = float(task.get("ml_confidence", 0.8 if predictions else 0.0))
        return DecisionResult("ml", predictions, confidence)
