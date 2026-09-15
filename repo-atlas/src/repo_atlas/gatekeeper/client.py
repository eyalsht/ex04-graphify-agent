"""Provider-agnostic LLM client wrapper -- the single LLM choke point.

Every external provider call goes through ``Gatekeeper.call``: it enforces the rate limit
(request spacing), retries with backoff on transient/rate-limit errors, records one
``TokenRecord`` per call, and hides the concrete provider behind a tiny client protocol so
the provider named by ``config/atlas.json`` can be swapped without touching callers.

Dispatch goes through the registry in ``registry.py`` (keyed by ``config["provider"]``), not
a hardcoded import -- the origin project read ``provider`` into an attribute and then always
imported the Gemini adapter regardless of it. The API key is read from ``os.environ`` only
(env var named by ``api_key_env``); when it is absent -- or set to an empty string -- the
``offline`` client is used instead so the suite runs keyless (R6.1).
"""

from __future__ import annotations

import os
import random
import time
from typing import TYPE_CHECKING, Any

from .token_log import TokenLogger, TokenRecord
from .types import LLMClient, LLMResponse, RateLimitError

if TYPE_CHECKING:
    from .registry import ProviderFactory

__all__ = ["Gatekeeper", "LLMClient", "LLMResponse", "RateLimitError"]


class Gatekeeper:
    """Provider-agnostic rate-limited/retrying/logging wrapper around an LLM client."""

    def __init__(
        self,
        config: dict[str, Any],
        logger: TokenLogger,
        client: LLMClient | None = None,
        registry: dict[str, ProviderFactory] | None = None,
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
        self._registry = registry if registry is not None else self._default_registry()
        self.client = client if client is not None else self._select_client()

    @staticmethod
    def _default_registry() -> dict[str, ProviderFactory]:
        # Deferred import breaks the client<->registry import cycle (registry.py imports
        # OfflineClient, which -- like this module -- depends on types.py).
        from .registry import default_registry

        return default_registry()

    def _select_client(self) -> LLMClient:
        """Inject the offline client when keyless; the registered provider otherwise."""
        if self.api_key is None:
            return self._registry["offline"]("", self.model)
        return self._build_provider_client()

    def _build_provider_client(self) -> LLMClient:
        factory = self._registry.get(self.provider)
        if factory is None:
            known = ", ".join(sorted(self._registry)) or "(none registered)"
            msg = f"unknown provider {self.provider!r}; registered providers: {known}"
            raise ValueError(msg)
        return factory(self.api_key or "", self.model)

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
        """The single LLM entry point: throttle -> retry -> log a TokenRecord."""
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
