"""The offline provider: no network, deterministic, and always available (R6.1).

Split out of ``client.py`` (CLAUDE.md sec.3: files stay under 150 lines). It is the default
provider in ``config/atlas.json`` and the automatic fallback whenever the configured API key
is absent, so the whole tool -- and the whole test suite -- runs with no key at all.
"""

from __future__ import annotations

from typing import Any

from .types import LLMResponse, RateLimitError


class OfflineClient:
    """Deterministic, network-free client; can simulate ``fail_times`` rate limits.

    ``input_tokens`` is the whitespace-token count of the prompt -- not a stub zero -- which
    is what makes a keyless token comparison produce a real, meaningful reduction figure
    (P5 depends on this property).
    """

    def __init__(self, fail_times: int = 0) -> None:
        self.fail_times = fail_times
        self.calls = 0

    def generate(self, messages: list[dict[str, Any]], system: str | None) -> LLMResponse:
        self.calls += 1
        if self.calls <= self.fail_times:
            raise RateLimitError("simulated rate limit")
        prompt = " ".join(str(m.get("content", "")) for m in messages)
        in_tokens = len(prompt.split()) + (len(system.split()) if system else 0)
        return LLMResponse(text="offline-response", input_tokens=in_tokens, output_tokens=2)
