"""gatekeeper -- the single path to any LLM provider (PLAN sec.2/sec.4).

Rate-limit, retry, and per-call token counters tagged by ``{run_id, run_type, node}``.
Dispatch is a registry keyed by ``config["provider"]`` (``registry.py``); ``offline`` is
always available and needs no network or key, so the full test suite runs keyless.
"""

from __future__ import annotations

from .client import Gatekeeper
from .offline import OfflineClient
from .registry import default_registry
from .token_log import TokenLogger, TokenRecord
from .types import LLMResponse, RateLimitError

__all__ = [
    "Gatekeeper",
    "LLMResponse",
    "OfflineClient",
    "RateLimitError",
    "TokenLogger",
    "TokenRecord",
    "default_registry",
]
