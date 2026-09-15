"""TDD for cost_usd / require_pricing (PRD R5.1; PHASE5-009)."""

from __future__ import annotations

import pytest

from repo_atlas.token_comparison.cost import PricingError, cost_usd, require_pricing


def test_zero_pricing_yields_zero_cost() -> None:
    pricing = {"input_per_million_usd": 0.0, "output_per_million_usd": 0.0}
    assert cost_usd(1_000_000, 1_000_000, pricing) == 0.0


def test_cost_scales_with_tokens_and_rate() -> None:
    pricing = {"input_per_million_usd": 3.0, "output_per_million_usd": 15.0}
    assert cost_usd(1_000_000, 0, pricing) == 3.0
    assert cost_usd(0, 1_000_000, pricing) == 15.0
    assert cost_usd(500_000, 200_000, pricing) == pytest.approx(1.5 + 3.0)


def test_require_pricing_extracts_the_two_rates() -> None:
    config = {"pricing": {"input_per_million_usd": 1.0, "output_per_million_usd": 2.0}}
    assert require_pricing(config) == {
        "input_per_million_usd": 1.0,
        "output_per_million_usd": 2.0,
    }


def test_require_pricing_fails_loud_when_block_is_missing() -> None:
    with pytest.raises(PricingError, match="pricing"):
        require_pricing({})


def test_require_pricing_fails_loud_when_a_rate_is_missing() -> None:
    with pytest.raises(PricingError, match="pricing"):
        require_pricing({"pricing": {"input_per_million_usd": 1.0}})
