"""HTTP client for the local Ollama API."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any
from urllib import error, request


@dataclass(frozen=True)
class OllamaApiClient:
    """Call Ollama through the non-interactive HTTP API."""

    host: str = "http://127.0.0.1:11434"
    model: str = "qwen2.5:7b"
    timeout: int = 300
    logger: logging.Logger | None = None

    def generate(self, prompt: str, model: str | None = None) -> str:
        """Generate text from the configured Ollama model."""
        payload = {
            "model": model or self.model,
            "prompt": prompt,
            "stream": False,
        }
        data = json.dumps(payload).encode("utf-8")
        http_request = request.Request(
            f"{self.host.rstrip('/')}/api/generate",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(http_request, timeout=self.timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
        except error.URLError as exc:
            raise ConnectionError(f"Ollama API request failed: {exc}") from exc

        generated = body.get("response")
        if not isinstance(generated, str):
            raise ValueError("Ollama API response did not include a text response.")
        if self.logger:
            self.logger.info("Received Ollama response with %s characters.", len(generated))
        return generated
