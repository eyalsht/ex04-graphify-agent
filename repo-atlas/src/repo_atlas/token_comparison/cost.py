"""USD cost from logged tokens x config-driven per-million rates (PRD R5.1).

The dollar figure is a deterministic derivation of already-logged tokens times the
``pricing`` block of the atlas config — never a hand-typed estimate. This module never
reads ``config/atlas.json`` itself (that belongs to the SDK layer, which loads the config
once and passes the ``pricing`` mapping in), so it stays usable with any already-parsed
config dict, including one built inline in a test.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

_PRICING_KEY = "pricing"
_IN_KEY = "input_per_million_usd"
_OUT_KEY = "output_per_million_usd"


class PricingError(RuntimeError):
    """The supplied config has no usable ``pricing`` block."""


def cost_usd(input_tokens: int, output_tokens: int, pricing: Mapping[str, float]) -> float:
    """USD for one run: ``input_tokens * in_rate + output_tokens * out_rate`` (per 1M), 6-dp.

    An all-zero ``pricing`` block (the offline provider's, per ``config/atlas.json``) always
    yields ``0.0`` — a real cost figure requires a real, priced provider.
    """
    rate_in = float(pricing.get(_IN_KEY, 0.0))
    rate_out = float(pricing.get(_OUT_KEY, 0.0))
    return round(input_tokens / 1e6 * rate_in + output_tokens / 1e6 * rate_out, 6)


def require_pricing(config: Mapping[str, Any]) -> dict[str, float]:
    """Extract ``{input_per_million_usd, output_per_million_usd}`` from an atlas config dict.

    Fails loudly rather than defaulting silently to zero rates for a misconfigured provider.
    """
    block = config.get(_PRICING_KEY)
    if not isinstance(block, Mapping) or _IN_KEY not in block or _OUT_KEY not in block:
        msg = f"atlas config must define a {_PRICING_KEY!r} block with {_IN_KEY!r} and {_OUT_KEY!r}"
        raise PricingError(msg)
    return {_IN_KEY: float(block[_IN_KEY]), _OUT_KEY: float(block[_OUT_KEY])}
