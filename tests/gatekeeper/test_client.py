"""TDD for the provider-agnostic Gatekeeper choke point (PHASE3-097..112)."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from ex04_graphify_agent.gatekeeper import Gatekeeper, LLMResponse, MockClient, TokenLogger


def _config() -> dict[str, object]:
    return {
        "provider": "gemini",
        "model": "",
        "api_key_env": "EX04_FAKE_KEY",
        "rate_limit_per_minute": 6000,
        "retry": {"max_attempts": 3, "backoff_seconds": 0.0},
    }


def test_gatekeeper_constructs_from_config() -> None:
    gk = Gatekeeper(_config(), TokenLogger(runs_dir=Path(".")))
    assert gk.model == ""
    assert gk.provider == "gemini"


def test_call_returns_response_and_records_tokens() -> None:
    logger = TokenLogger(runs_dir=Path("."))
    gk = Gatekeeper(_config(), logger)
    resp = gk.call(messages=[{"role": "user", "content": "hi"}], run_id="r1", node="plan")
    assert isinstance(resp, LLMResponse)
    assert logger.records and logger.records[0].node == "plan"
    assert logger.records[0].input_tokens >= 0
    assert logger.records[0].run_id == "r1"


def test_keyless_uses_mock_client(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("EX04_FAKE_KEY", raising=False)
    gk = Gatekeeper(_config(), TokenLogger(runs_dir=Path(".")))
    assert isinstance(gk.client, MockClient)


def test_api_key_read_from_environ_only(monkeypatch: pytest.MonkeyPatch) -> None:
    # Key must never come from the config dict — only os.environ[api_key_env].
    cfg = _config()
    cfg["api_key_env"] = "EX04_FAKE_KEY"
    monkeypatch.delenv("EX04_FAKE_KEY", raising=False)
    gk = Gatekeeper(cfg, TokenLogger(runs_dir=Path(".")))
    assert gk.api_key is None  # absent in env → None, mock selected
    assert isinstance(gk.client, MockClient)


def test_retry_with_backoff_on_rate_limit() -> None:
    logger = TokenLogger(runs_dir=Path("."))
    client = MockClient(fail_times=2)
    gk = Gatekeeper(_config(), logger, client=client)
    resp = gk.call(messages=[{"role": "user", "content": "x"}], run_id="r1", node="fix")
    assert isinstance(resp, LLMResponse)
    assert client.calls == 3  # 2 failures + 1 success


def test_retry_exhaustion_raises() -> None:
    client = MockClient(fail_times=99)
    gk = Gatekeeper(_config(), TokenLogger(runs_dir=Path(".")), client=client)
    with pytest.raises(RuntimeError):
        gk.call(messages=[{"role": "user", "content": "x"}], run_id="r1", node="fix")


def test_rate_limit_queue_spaces_calls() -> None:
    cfg = _config()
    cfg["rate_limit_per_minute"] = 60  # → 1.0s min interval
    gk = Gatekeeper(cfg, TokenLogger(runs_dir=Path(".")))
    start = time.monotonic()
    for _ in range(2):
        gk.call(messages=[{"role": "user", "content": "x"}], run_id="r1", node="plan")
    # Second call must wait ~1s behind the first (queue respects rate limit).
    assert time.monotonic() - start >= 0.9


def test_single_choke_point_documented() -> None:
    # The provider client is only ever reached via Gatekeeper.call (single seam).
    gk = Gatekeeper(_config(), TokenLogger(runs_dir=Path(".")))
    assert hasattr(gk, "call")
    assert not hasattr(MockClient, "queue")  # mock has no rate logic of its own
