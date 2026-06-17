"""TDD for scripts/run_comparison.py key-gating (PHASE6-060/061, TC-T8, ADR-0005)."""

from __future__ import annotations

import pytest

import run_comparison


def test_exits_nonzero_with_key_required_message_when_key_absent(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """TC-T8: configured provider key env var unset -> clear "key required" message."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    exit_code = run_comparison.main([])
    captured = capsys.readouterr()
    assert exit_code == 1
    assert "key required" in captured.out.lower()
    assert "GEMINI_API_KEY" in captured.out


def test_missing_key_message_names_the_configured_env_var() -> None:
    assert "GEMINI_API_KEY" in run_comparison._missing_key_message("GEMINI_API_KEY")


def test_load_local_env_delegates_to_dotenv(monkeypatch: pytest.MonkeyPatch) -> None:
    """The manual real run loads a local .env via python-dotenv (key never committed).

    Called only from the script's ``__main__`` entry, never from ``main()`` — so the
    keyless suite (ADR-0005) never picks up a developer's local .env.
    """
    calls: list[bool] = []
    monkeypatch.setattr(run_comparison, "load_dotenv", lambda *a, **k: calls.append(True))
    run_comparison._load_local_env()
    assert calls == [True]
