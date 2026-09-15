"""The optional config sections RunConfig now models (vault, graph_reader, brief, provider).

These were previously read as raw JSON in two places because RunConfig did not model them.
Optional-with-defaults is the right shape: a minimal config must still work, and a partial
section must not silently discard the keys it does provide.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from repo_atlas.paths import RunConfig

_MINIMAL: dict[str, Any] = {
    "provider": "offline",
    "model": "mock-offline",
    "api_key_env": "ATLAS_API_KEY",
    "extractor": {
        "exclude_dirs": [".git"],
        "exclude_globs": ["*.lock"],
        "max_file_bytes": 1024,
        "document_extensions": [".md"],
    },
}


def _write(tmp_path: Path, data: dict[str, Any]) -> Path:
    path = tmp_path / "atlas.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_a_minimal_config_still_loads_with_defaults(tmp_path: Path) -> None:
    config = RunConfig.load(_write(tmp_path, _MINIMAL))
    assert config.vault.hot_top_k > 0
    assert config.brief.context_token_budget > 0
    assert config.graph_reader.betweenness_sample_k > 0


def test_the_shipped_config_is_read_not_defaulted() -> None:
    from repo_atlas.paths import RunPaths

    config = RunConfig.load(RunPaths.create(Path.cwd()).config_path)
    assert config.vault.hot_top_k == 8
    assert config.brief.hot_source_slices == 5
    assert config.pricing.input_per_million_usd == 0.0


def test_a_provided_section_overrides_the_default(tmp_path: Path) -> None:
    data = {**_MINIMAL, "vault": {"hot_top_k": 3, "hot_weights": {"degree": 1.0}}}
    config = RunConfig.load(_write(tmp_path, data))
    assert config.vault.hot_top_k == 3
    assert config.vault.hot_weights == {"degree": 1.0}


def test_a_partial_section_keeps_defaults_for_its_missing_keys(tmp_path: Path) -> None:
    """Providing one key must not blank out the others."""
    data = {**_MINIMAL, "vault": {"hot_top_k": 2}}
    config = RunConfig.load(_write(tmp_path, data))
    assert config.vault.hot_top_k == 2
    assert config.vault.hot_weights  # still populated


def test_retry_and_rate_limit_have_defaults(tmp_path: Path) -> None:
    config = RunConfig.load(_write(tmp_path, _MINIMAL))
    assert config.rate_limit_per_minute > 0
    assert config.retry.max_attempts >= 1


def test_gatekeeper_config_round_trips_the_keys_the_gatekeeper_reads(tmp_path: Path) -> None:
    """The gatekeeper takes a dict; it should come from typed config, not a raw re-read."""
    payload = RunConfig.load(_write(tmp_path, _MINIMAL)).gatekeeper_config()
    assert payload["provider"] == "offline"
    assert payload["model"] == "mock-offline"
    assert payload["api_key_env"] == "ATLAS_API_KEY"
    assert payload["retry"]["max_attempts"] >= 1
    assert payload["rate_limit_per_minute"] > 0


def test_a_malformed_section_is_rejected_rather_than_ignored(tmp_path: Path) -> None:
    from repo_atlas.paths import ConfigError

    data = {**_MINIMAL, "vault": "not-an-object"}
    try:
        RunConfig.load(_write(tmp_path, data))
    except ConfigError as exc:
        assert "vault" in str(exc)
    else:  # pragma: no cover - the assertion above is the point
        raise AssertionError("a malformed section must not be silently ignored")
