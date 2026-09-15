"""Concrete Gemini adapter -- the ONLY module that touches the provider SDK.

Isolated behind the ``LLMClient`` protocol so the provider can be swapped without touching
the gatekeeper or any caller. The SDK import is deferred into ``GeminiClient.__init__`` so
``repo_atlas.gatekeeper`` imports cleanly with no provider SDK installed at all (it is an
optional dependency -- ``pip install repo-atlas[gemini]``).

``GeminiClient`` itself is exercised only on a real manual run with a key present
(no-cover); its two defects are each isolated into a pure, fully-tested helper below:

* ``gemini_role`` -- the origin flattened every message into one string, dropping roles,
  making multi-turn conversations impossible. Content roles now round-trip through this.
* ``as_rate_limit_error`` -- the origin's ``generate`` never raised ``RateLimitError``, so
  the gatekeeper's retry path was dead for a real 429. Provider errors are mapped here.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from .types import LLMResponse, RateLimitError

_RATE_LIMIT_STATUS = 429
_RATE_LIMIT_MARKERS = ("RESOURCE_EXHAUSTED", "rate limit", "Too Many Requests")


def join_text_parts(parts: Iterable[Any] | None) -> str:
    """Concatenate the text of every text-bearing response part.

    A provider response may return a function-call part next to the answer; such parts
    expose no usable ``.text`` and are skipped, so the caller still receives the full text
    the model actually wrote (a bare ``.text`` accessor can warn and drop content otherwise).
    """
    out: list[str] = []
    for part in parts or []:
        text = getattr(part, "text", None)
        if text:
            out.append(str(text))
    return "".join(out)


def gemini_role(role: str | None) -> str:
    """Map a message role onto the two roles Gemini's ``contents`` API accepts.

    ``"assistant"`` (and this codebase's own ``"model"``) becomes ``"model"``; every other
    role -- including ``None``, ``""`` and ``"user"`` -- becomes ``"user"``.
    """
    return "model" if role in ("assistant", "model") else "user"


def as_rate_limit_error(exc: Exception) -> RateLimitError | None:
    """Return a ``RateLimitError`` wrapping ``exc`` if it signals a rate limit, else ``None``.

    Provider SDKs surface a 429 in different shapes (a ``.code`` attribute, an HTTP response
    status, or just the message text) -- checked in that order so a real 429 always maps.
    """
    code = getattr(exc, "code", None)
    if code == _RATE_LIMIT_STATUS:
        return RateLimitError(str(exc))
    response = getattr(exc, "response", None)
    if getattr(response, "status_code", None) == _RATE_LIMIT_STATUS:
        return RateLimitError(str(exc))
    message = str(exc)
    if any(marker in message for marker in _RATE_LIMIT_MARKERS):
        return RateLimitError(str(exc))
    return None


class GeminiClient:  # pragma: no cover - requires a real API key (manual run)
    """Thin wrapper over the optional Gemini SDK; constructed only when a key is present."""

    def __init__(self, api_key: str, model: str) -> None:
        from google import genai

        if not model:
            msg = "config/atlas.json 'model' must be set for a real run"
            raise ValueError(msg)
        self._client = genai.Client(api_key=api_key)
        self._model = model

    def generate(self, messages: list[dict[str, Any]], system: str | None) -> LLMResponse:
        from google.genai import types

        contents = [
            types.Content(
                role=gemini_role(str(m.get("role")) if m.get("role") is not None else None),
                parts=[types.Part(text=str(m.get("content", "")))],
            )
            for m in messages
        ]
        config = types.GenerateContentConfig(
            system_instruction=system,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        )
        try:
            result = self._client.models.generate_content(
                model=self._model, contents=contents, config=config
            )
        except Exception as exc:
            mapped = as_rate_limit_error(exc)
            if mapped is not None:
                raise mapped from exc
            raise
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
