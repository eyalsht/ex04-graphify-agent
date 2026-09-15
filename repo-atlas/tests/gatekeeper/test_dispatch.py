"""TDD for provider dispatch (PHASE4-003/004): honours ``config["provider"]`` via a registry.

The defect fixed: the origin's ``_build_provider_client`` imported ``GeminiClient``
unconditionally, so ``config["provider"]`` was read into an attribute and then ignored.
"""

from __future__ import annotations

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


def test_keyless_falls_back_to_offline(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ATLAS_FAKE_KEY", raising=False)
    # Even a non-offline provider must fall back to offline when no key is set (R6.1).
    gk = Gatekeeper(_config(provider="gemini"), _logger(tmp_path))
    assert isinstance(gk.client, OfflineClient)


def test_empty_env_value_is_treated_as_absent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("ATLAS_FAKE_KEY", "")
    gk = Gatekeeper(_config(provider="gemini"), _logger(tmp_path))
    assert gk.api_key is None
    assert isinstance(gk.client, OfflineClient)


def test_api_key_read_from_environ_only(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # The key must never come from the config dict -- only os.environ[api_key_env].
    monkeypatch.delenv("ATLAS_FAKE_KEY", raising=False)
    gk = Gatekeeper(_config(), _logger(tmp_path))
    assert gk.api_key is None
    assert isinstance(gk.client, OfflineClient)


def test_dispatch_honours_config_provider_via_registry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("ATLAS_FAKE_KEY", "a-real-key")

    class _FakeClient:
        def __init__(self, api_key: str, model: str) -> None:
            self.api_key = api_key
            self.model = model

        def generate(self, messages: list[dict[str, object]], system: str | None) -> LLMResponse:
            return LLMResponse(text="fake", input_tokens=1, output_tokens=1)

    registry = {"fake-provider": _FakeClient}
    gk = Gatekeeper(_config(provider="fake-provider"), _logger(tmp_path), registry=registry)
    assert isinstance(gk.client, _FakeClient)
    assert gk.client.api_key == "a-real-key"


def test_unknown_provider_with_a_key_raises(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("ATLAS_FAKE_KEY", "a-real-key")
    with pytest.raises(ValueError, match="unknown provider"):
        Gatekeeper(_config(provider="nope"), _logger(tmp_path), registry={})
