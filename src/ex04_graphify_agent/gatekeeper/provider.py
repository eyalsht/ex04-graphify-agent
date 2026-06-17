"""Concrete Gemini adapter — the ONLY module that touches the provider SDK.

Isolated behind the ``LLMClient`` protocol so the provider can be swapped without touching
the gatekeeper or any caller (ADR-0002). The ``GeminiClient`` itself is exercised only on a
real manual run with a key present (no-cover); ``join_text_parts`` is a pure helper covered
by the keyless suite.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from .client import LLMResponse


def join_text_parts(parts: Iterable[Any] | None) -> str:
    """Concatenate the text of every text-bearing response part.

    Gemini 3.x may return a ``function_call`` part next to the answer; such parts expose no
    usable ``.text`` and are skipped, so the caller still receives the full text the model
    actually wrote (the SDK's ``.text`` accessor warns and can drop content otherwise).
    """
    out: list[str] = []
    for part in parts or []:
        text = getattr(part, "text", None)
        if text:
            out.append(str(text))
    return "".join(out)


class GeminiClient:  # pragma: no cover - requires a real API key (manual run)
    """Thin wrapper over ``google-genai``; constructed only when a key is present."""

    def __init__(self, api_key: str, model: str) -> None:
        from google import genai

        if not model:
            msg = "config/agent.json 'model' must be set for a real run (D6)"
            raise ValueError(msg)
        self._client = genai.Client(api_key=api_key)
        self._model = model

    def generate(self, messages: list[dict[str, Any]], system: str | None) -> LLMResponse:
        from google.genai import types

        contents = "\n".join(str(m.get("content", "")) for m in messages)
        # Disable automatic function-calling so the model returns the patch as plain text
        # instead of a spurious function_call part (which the .text accessor would drop).
        config = types.GenerateContentConfig(
            system_instruction=system,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        )
        result = self._client.models.generate_content(
            model=self._model, contents=contents, config=config
        )
        text = str(getattr(result, "text", "") or "")
        if not text:
            candidates = getattr(result, "candidates", None) or []
            if candidates:
                content = getattr(candidates[0], "content", None)
                text = join_text_parts(getattr(content, "parts", None))
        usage = getattr(result, "usage_metadata", None)
        return LLMResponse(
            text=text,
            input_tokens=int(getattr(usage, "prompt_token_count", 0) or 0),
            output_tokens=int(getattr(usage, "candidates_token_count", 0) or 0),
        )
