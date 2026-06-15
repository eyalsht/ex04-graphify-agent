"""Provider-agnostic LLM client wrapper — the single LLM choke point (ADR-0002).

Every external provider call goes through ``Gatekeeper.call``: it enforces the rate-limit
(request queue), retries with backoff on transient/rate-limit errors, records one
``TokenRecord`` per call, and hides the concrete provider behind a tiny client protocol so
the provider (Gemini per ``config/agent.json``) can be swapped without touching callers.
The API key is read from ``os.environ`` only (env var named by ``api_key_env``); when it is
absent a deterministic ``MockClient`` is injected so the suite runs keyless (ADR-0005).
"""

from __future__ import annotations

import os
import random
import time
from dataclasses import dataclass
from typing import Any, Protocol

from .token_log import TokenLogger, TokenRecord


@dataclass(frozen=True)
class LLMResponse:
    """Normalized provider response (text + token usage)."""

    text: str
    input_tokens: int
    output_tokens: int


class RateLimitError(RuntimeError):
    """Raised by a client to signal a retryable rate-limit/transient failure."""


class LLMClient(Protocol):
    """The minimal provider-agnostic surface the gatekeeper depends on."""

    def generate(self, messages: list[dict[str, Any]], system: str | None) -> LLMResponse: ...


class MockClient:
    """Deterministic keyless client (ADR-0005); can simulate ``fail_times`` rate limits."""

    def __init__(self, fail_times: int = 0) -> None:
        self.fail_times = fail_times
        self.calls = 0

    def generate(self, messages: list[dict[str, Any]], system: str | None) -> LLMResponse:
        self.calls += 1
        if self.calls <= self.fail_times:
            raise RateLimitError("simulated rate limit")
        prompt = " ".join(str(m.get("content", "")) for m in messages)
        in_tokens = len(prompt.split()) + (len(system.split()) if system else 0)
        return LLMResponse(text="mock-response", input_tokens=in_tokens, output_tokens=2)


class Gatekeeper:
    """Provider-agnostic rate-limited/retrying/logging wrapper around an LLM client."""

    def __init__(
        self,
        config: dict[str, Any],
        logger: TokenLogger,
        client: LLMClient | None = None,
    ) -> None:
        self._config = config
        self._logger = logger
        self.provider = str(config.get("provider", ""))
        self.model = str(config.get("model", ""))
        self.api_key = os.environ.get(str(config.get("api_key_env", "")), None) or None
        retry = config.get("retry", {})
        self._max_attempts = int(retry.get("max_attempts", 1))
        self._backoff = float(retry.get("backoff_seconds", 0.0))
        rpm = float(config.get("rate_limit_per_minute", 0) or 0)
        self._min_interval = 60.0 / rpm if rpm > 0 else 0.0
        self._last_call = 0.0
        self.client = client if client is not None else self._select_client()

    def _select_client(self) -> LLMClient:
        """Inject the mock when keyless; the real provider adapter otherwise."""
        if self.api_key is None:
            return MockClient()
        return self._build_provider_client()

    def _build_provider_client(self) -> LLMClient:  # pragma: no cover - needs a real key
        from .provider import GeminiClient

        return GeminiClient(api_key=self.api_key or "", model=self.model)

    def _throttle(self) -> None:
        if self._min_interval <= 0:
            return
        wait = self._min_interval - (time.monotonic() - self._last_call)
        if wait > 0:
            time.sleep(wait)
        self._last_call = time.monotonic()

    def call(
        self,
        messages: list[dict[str, Any]],
        run_id: str,
        node: str,
        system: str | None = None,
        run_type: str = "graph_guided",
    ) -> LLMResponse:
        """The single LLM entry point: throttle → retry → log a TokenRecord."""
        self._throttle()
        response = self._call_with_retry(messages, system)
        self._logger.record(
            TokenRecord(
                run_id=run_id,
                run_type=run_type,
                node=node,
                input_tokens=response.input_tokens,
                output_tokens=response.output_tokens,
                model=self.model,
            )
        )
        return response

    def _call_with_retry(self, messages: list[dict[str, Any]], system: str | None) -> LLMResponse:
        last_error: Exception | None = None
        for attempt in range(self._max_attempts):
            try:
                return self.client.generate(messages, system)
            except RateLimitError as exc:
                last_error = exc
                if attempt + 1 < self._max_attempts:
                    # Exponential backoff with full jitter (avoids thundering herd);
                    # ``backoff_seconds == 0`` (tests) yields no delay.
                    delay = self._backoff * (2**attempt)
                    time.sleep(delay + random.uniform(0.0, self._backoff))
        msg = f"LLM call failed after {self._max_attempts} attempts"
        raise RuntimeError(msg) from last_error
