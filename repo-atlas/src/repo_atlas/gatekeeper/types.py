"""Shared, provider-agnostic types: the response shape, the retry signal, the client contract.

Split out from ``client.py`` (CLAUDE.md sec.3: files stay under 150 lines) so both
``offline.py`` and ``provider.py`` depend on this small leaf module instead of on
``client.py`` itself, which keeps the import graph acyclic.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


class RateLimitError(RuntimeError):
    """Raised by a client to signal a retryable rate-limit/transient failure."""


@dataclass(frozen=True)
class LLMResponse:
    """Normalized provider response (text + token usage)."""

    text: str
    input_tokens: int
    output_tokens: int


class LLMClient(Protocol):
    """The minimal provider-agnostic surface the gatekeeper depends on."""

    def generate(self, messages: list[dict[str, Any]], system: str | None) -> LLMResponse: ...
