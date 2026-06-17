"""TDD for token_comparison.cost — USD from token counts x config-driven per-million rates.

Cost is a deterministic derivation (logged tokens x published rate), so it stays traceable
and reproducible (CLAUDE.md §4): no hand-typed dollar figures.
"""

from __future__ import annotations

import pytest

from ex04_graphify_agent.token_comparison import cost

_PRICING = {"input_per_million_usd": 2.0, "output_per_million_usd": 12.0}


def test_cost_usd_combines_input_and_output_rates() -> None:
    # 1_000_000 in @ $2 + 1_000_000 out @ $12 = $14.00
    assert cost.cost_usd(1_000_000, 1_000_000, _PRICING) == 14.0


def test_cost_usd_scales_with_token_counts() -> None:
    # 1559 in @ $2/M + 507 out @ $12/M
    expected = round(1559 / 1e6 * 2.0 + 507 / 1e6 * 12.0, 6)
    assert cost.cost_usd(1559, 507, _PRICING) == expected


def test_cost_usd_zero_tokens_is_zero() -> None:
    assert cost.cost_usd(0, 0, _PRICING) == 0.0


def test_load_pricing_reads_configured_block() -> None:
    pricing = cost.load_pricing()
    assert pricing["input_per_million_usd"] > 0
    assert pricing["output_per_million_usd"] > 0


def test_load_pricing_fails_loud_when_block_absent() -> None:
    with pytest.raises(KeyError, match="pricing"):
        cost.load_pricing({"model": "x"})
