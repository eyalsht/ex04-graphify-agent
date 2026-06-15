"""gatekeeper — provider-agnostic choke point for every LLM call.

Rate-limit, retry, queue, logging, and per-call token counters tagged by {run_type, node}.
The single mock seam for keyless tests (ADR-0002, ADR-0005). The concrete provider is named
by ``config/agent.json``; the API key comes from ``os.environ`` only — never a config file.
"""

from __future__ import annotations

from .client import Gatekeeper, LLMResponse, MockClient
from .token_log import TokenLogger, TokenRecord

__all__ = [
    "Gatekeeper",
    "LLMResponse",
    "MockClient",
    "TokenLogger",
    "TokenRecord",
]
