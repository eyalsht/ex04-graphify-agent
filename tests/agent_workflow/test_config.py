"""TDD for agent_workflow config/path resolution (no hardcoded values — CLAUDE.md §3)."""

from __future__ import annotations

from ex04_graphify_agent.agent_workflow import config


def test_limits_loaded_from_agent_json() -> None:
    limits = config.load_limits()
    assert limits.max_findings_tried == 3
    assert limits.max_validation_attempts == 1


def test_agent_config_dict_exposes_provider_and_api_key_env() -> None:
    cfg = config.agent_config()
    assert cfg["provider"] == "gemini"
    assert cfg["api_key_env"] == "GEMINI_API_KEY"


def test_model_is_config_driven_not_hardcoded() -> None:
    # D6: the model id is supplied by config/agent.json (config-driven, swappable),
    # never pinned in code — and specifically never a Claude Haiku default.
    model = config.agent_config()["model"]
    assert model, "config/agent.json 'model' must name a provider model id for the real run"
    assert "haiku" not in model.lower()


def test_resolves_vault_and_repo_paths() -> None:
    assert config.index_md_path().name == "index.md"
    assert config.hot_md_path().name == "hot.md"
    assert config.data_repo_root().name == "broken-python"


def test_repo_path_resolves_relative_source_dynamically() -> None:
    # No hardcoded target: a finding's repo-relative source_file resolves under the repo root.
    resolved = config.repo_path("polygons/polygons.py")
    assert resolved.name == "polygons.py"
    assert resolved.parent == config.data_repo_root() / "polygons"
