"""TDD for the shared provider-agnostic types."""

from __future__ import annotations

from repo_atlas.gatekeeper.types import LLMResponse, RateLimitError


def test_llm_response_is_a_frozen_value_object() -> None:
    resp = LLMResponse(text="hi", input_tokens=1, output_tokens=2)
    assert (resp.text, resp.input_tokens, resp.output_tokens) == ("hi", 1, 2)
    assert resp == LLMResponse(text="hi", input_tokens=1, output_tokens=2)


def test_rate_limit_error_is_a_runtime_error() -> None:
    assert isinstance(RateLimitError("x"), RuntimeError)
