"""USD cost from token counts x config-driven per-million rates (cost analysis, R4.1).

The dollar figure is a deterministic derivation of the gatekeeper's logged tokens times the
``pricing`` block in ``config/agent.json`` — never a hand-typed estimate (CLAUDE.md §4). The
rates live in config (not code) so swapping the model only touches JSON.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ex04_graphify_agent.gatekeeper.config import load_agent_config

_PRICING_KEY = "pricing"
_IN_KEY = "input_per_million_usd"
_OUT_KEY = "output_per_million_usd"


def cost_usd(input_tokens: int, output_tokens: int, pricing: Mapping[str, float]) -> float:
    """USD for one run: ``input_tokens x in_rate + output_tokens x out_rate`` (per 1M), 6-dp."""
    rate_in = float(pricing.get(_IN_KEY, 0.0))
    rate_out = float(pricing.get(_OUT_KEY, 0.0))
    return round(input_tokens / 1e6 * rate_in + output_tokens / 1e6 * rate_out, 6)


def load_pricing(config: Mapping[str, Any] | None = None) -> dict[str, float]:
    """Read the ``pricing`` block from ``config/agent.json``; fail loud if it is absent."""
    cfg = config if config is not None else load_agent_config()
    block = cfg.get(_PRICING_KEY)
    if not isinstance(block, Mapping) or _IN_KEY not in block or _OUT_KEY not in block:
        msg = (
            "config/agent.json must define a 'pricing' block with "
            f"'{_IN_KEY}' and '{_OUT_KEY}' (USD per 1M tokens)"
        )
        raise KeyError(msg)
    return {_IN_KEY: float(block[_IN_KEY]), _OUT_KEY: float(block[_OUT_KEY])}
