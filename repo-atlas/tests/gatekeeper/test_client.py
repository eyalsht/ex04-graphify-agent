"""TDD for the Gatekeeper choke point's own behaviour: call, retry, rate limiting.

Provider-dispatch tests live in ``test_dispatch.py``, offline-client tests in
``test_offline.py`` (split to keep every file under CLAUDE.md sec.3's 150-line cap).
"""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from repo_atlas.gatekeeper import Gatekeeper, LLMResponse, TokenLogger
from repo_atlas.gatekeeper.offline import OfflineClient


def _config(**overrides: object) -> dict[str, object]:
    cfg: dict[str, object] = {
        "provider": "offline",
        "model": "mock-offline",
        "api_key_env": "ATLAS_FAKE_KEY",
        "rate_limit_per_minute": 6000,
        "retry": {"max_attempts": 3, "backoff_seconds": 0.0},
    }
    cfg.update(overrides)
    return cfg


def _logger(tmp_path: Path) -> TokenLogger:
    return TokenLogger(runs_dir=tmp_path)


def test_gatekeeper_constructs_from_config(tmp_path: Path) -> None:
    gk = Gatekeeper(_config(), _logger(tmp_path))
    assert gk.model == "mock-offline"
    assert gk.provider == "offline"


def test_call_returns_response_and_records_tokens(tmp_path: Path) -> None:
    logger = _logger(tmp_path)
    gk = Gatekeeper(_config(), logger)
    resp = gk.call(messages=[{"role": "user", "content": "hi"}], run_id="r1", node="plan")
    assert isinstance(resp, LLMResponse)
    assert logger.records and logger.records[0].node == "plan"
    assert logger.records[0].input_tokens >= 0
    assert logger.records[0].run_id == "r1"


def test_offline_client_input_tokens_is_whitespace_count(tmp_path: Path) -> None:
    # The evidence P5 depends on: a real, non-zero token count from a prompt, not a stub 0.
    logger = _logger(tmp_path)
    gk = Gatekeeper(_config(), logger)
    gk.call(
        messages=[{"role": "user", "content": "one two three four"}],
        run_id="r1",
        node="plan",
        system="five six",
    )
    assert logger.records[0].input_tokens == 6


def test_retry_with_backoff_on_rate_limit(tmp_path: Path) -> None:
    logger = _logger(tmp_path)
    client = OfflineClient(fail_times=2)
    gk = Gatekeeper(_config(), logger, client=client)
    resp = gk.call(messages=[{"role": "user", "content": "x"}], run_id="r1", node="fix")
    assert isinstance(resp, LLMResponse)
    assert client.calls == 3  # 2 failures + 1 success


def test_retry_exhaustion_raises(tmp_path: Path) -> None:
    client = OfflineClient(fail_times=99)
    gk = Gatekeeper(_config(), _logger(tmp_path), client=client)
    with pytest.raises(RuntimeError):
        gk.call(messages=[{"role": "user", "content": "x"}], run_id="r1", node="fix")


def test_rate_limit_queue_spaces_calls(tmp_path: Path) -> None:
    cfg = _config(rate_limit_per_minute=60)  # -> 1.0s min interval
    gk = Gatekeeper(cfg, _logger(tmp_path))
    start = time.monotonic()
    for _ in range(2):
        gk.call(messages=[{"role": "user", "content": "x"}], run_id="r1", node="plan")
    assert time.monotonic() - start >= 0.9


def test_zero_rate_limit_disables_throttling(tmp_path: Path) -> None:
    gk = Gatekeeper(_config(rate_limit_per_minute=0), _logger(tmp_path))
    start = time.monotonic()
    for _ in range(3):
        gk.call(messages=[{"role": "user", "content": "x"}], run_id="r1", node="plan")
    assert time.monotonic() - start < 0.5
