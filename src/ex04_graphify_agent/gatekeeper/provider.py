"""Concrete Gemini adapter — the ONLY module that touches the provider SDK.

Isolated behind the ``LLMClient`` protocol so the provider can be swapped without touching
the gatekeeper or any caller (ADR-0002). Exercised only on a real manual run with a key
present (Phase 6); the keyless suite uses ``MockClient`` instead, so this is no-cover.
"""

from __future__ import annotations

from typing import Any

from .client import LLMResponse


class GeminiClient:  # pragma: no cover - requires a real API key (manual Phase-6 run)
    """Thin wrapper over ``google-genai``; constructed only when a key is present."""

    def __init__(self, api_key: str, model: str) -> None:
        from google import genai

        if not model:
            msg = "config/agent.json 'model' must be set for a real run (D6)"
            raise ValueError(msg)
        self._client = genai.Client(api_key=api_key)
        self._model = model

    def generate(self, messages: list[dict[str, Any]], system: str | None) -> LLMResponse:
        contents = "\n".join(str(m.get("content", "")) for m in messages)
        result = self._client.models.generate_content(
            model=self._model,
            contents=contents,
            config={"system_instruction": system} if system else None,
        )
        usage = getattr(result, "usage_metadata", None)
        return LLMResponse(
            text=str(getattr(result, "text", "")),
            input_tokens=int(getattr(usage, "prompt_token_count", 0) or 0),
            output_tokens=int(getattr(usage, "candidates_token_count", 0) or 0),
        )
