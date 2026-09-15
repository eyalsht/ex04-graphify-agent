"""TDD for ``OfflineClient`` in isolation, no ``Gatekeeper`` involved."""

from __future__ import annotations

import pytest

from repo_atlas.gatekeeper.offline import OfflineClient
from repo_atlas.gatekeeper.types import LLMResponse, RateLimitError


def test_generate_returns_deterministic_response() -> None:
    client = OfflineClient()
    resp = client.generate([{"role": "user", "content": "hello"}], None)
    assert isinstance(resp, LLMResponse)
    assert resp.text == "offline-response"


def test_input_tokens_counts_whitespace_tokens_in_prompt_and_system() -> None:
    client = OfflineClient()
    resp = client.generate(
        messages=[{"role": "user", "content": "a b c"}, {"role": "assistant", "content": "d"}],
        system="e f",
    )
    assert resp.input_tokens == 6  # "a b c" + "d" + "e f" -> 4 + 2


def test_no_system_prompt_still_counts_message_tokens() -> None:
    client = OfflineClient()
    resp = client.generate([{"role": "user", "content": "one two"}], None)
    assert resp.input_tokens == 2


def test_fail_times_raises_rate_limit_error_then_succeeds() -> None:
    client = OfflineClient(fail_times=1)
    with pytest.raises(RateLimitError):
        client.generate([{"role": "user", "content": "x"}], None)
    resp = client.generate([{"role": "user", "content": "x"}], None)
    assert isinstance(resp, LLMResponse)
    assert client.calls == 2
