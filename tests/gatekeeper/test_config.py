"""TDD for config-driven gatekeeper loading (PHASE3-097/103, no-hardcoded rule)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ex04_graphify_agent.gatekeeper.config import (
    default_runs_dir,
    load_agent_config,
)


def test_load_agent_config_from_repo_default() -> None:
    cfg = load_agent_config()
    assert cfg["provider"] == "gemini"
    assert cfg["api_key_env"] == "GEMINI_API_KEY"


def test_load_agent_config_explicit_path(tmp_path: Path) -> None:
    p = tmp_path / "agent.json"
    p.write_text(json.dumps({"provider": "x"}), encoding="utf-8")
    assert load_agent_config(p)["provider"] == "x"


def test_load_agent_config_missing_fails_loud(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_agent_config(tmp_path / "nope.json")


def test_default_runs_dir_resolves_under_artifacts() -> None:
    runs = default_runs_dir()
    assert runs.name == "runs"
    assert runs.parent.name == "artifacts"
