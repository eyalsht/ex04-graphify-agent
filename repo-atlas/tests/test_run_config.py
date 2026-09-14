"""RED/GREEN tests for ``RunConfig`` — typed, fail-loud view over the atlas config.

Split from ``test_paths.py`` (which already covers ``RunPaths``) to keep both files under the
150-line cap in ``CLAUDE.md`` Sec.3 — one exported class from ``src/repo_atlas/paths.py`` per file.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from repo_atlas.paths import ConfigError, RunConfig

_SHIPPED_CONFIG = Path(__file__).resolve().parents[1] / "config" / "atlas.json"

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
    config_path = tmp_path / "atlas.json"
    config_path.write_text(json.dumps(data), encoding="utf-8")
    return config_path


def test_load_reads_the_shipped_config() -> None:
    config = RunConfig.load(_SHIPPED_CONFIG)
    assert config.provider == "offline"
    assert config.api_key_env == "ATLAS_API_KEY"
    assert ".git" in config.extractor.exclude_dirs
    assert config.extractor.max_file_bytes == 262144


def test_load_parses_a_minimal_config(tmp_path: Path) -> None:
    config = RunConfig.load(_write(tmp_path, _MINIMAL))
    assert config.model == "mock-offline"
    assert config.extractor.exclude_globs == ("*.lock",)
    assert config.extractor.document_extensions == (".md",)


def test_extractor_fields_are_immutable_tuples(tmp_path: Path) -> None:
    config = RunConfig.load(_write(tmp_path, _MINIMAL))
    assert isinstance(config.extractor.exclude_dirs, tuple)
    assert not isinstance(config.extractor.exclude_dirs, list)


def test_load_raises_clear_error_when_file_is_missing(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="not found"):
        RunConfig.load(tmp_path / "missing.json")


def test_load_raises_clear_error_on_invalid_json(tmp_path: Path) -> None:
    bad = tmp_path / "atlas.json"
    bad.write_text("{not json", encoding="utf-8")
    with pytest.raises(ConfigError, match="JSON"):
        RunConfig.load(bad)


def test_load_raises_clear_error_when_json_is_not_an_object(tmp_path: Path) -> None:
    bad = tmp_path / "atlas.json"
    bad.write_text("[1, 2, 3]", encoding="utf-8")
    with pytest.raises(ConfigError, match="JSON object"):
        RunConfig.load(bad)


@pytest.mark.parametrize("missing_key", ["provider", "model", "api_key_env"])
def test_load_raises_clear_error_when_a_top_level_key_is_missing(
    tmp_path: Path, missing_key: str
) -> None:
    data = {key: value for key, value in _MINIMAL.items() if key != missing_key}
    with pytest.raises(ConfigError, match=missing_key):
        RunConfig.load(_write(tmp_path, data))


def test_load_raises_clear_error_when_extractor_section_is_missing(tmp_path: Path) -> None:
    data = {key: value for key, value in _MINIMAL.items() if key != "extractor"}
    with pytest.raises(ConfigError, match="extractor"):
        RunConfig.load(_write(tmp_path, data))


@pytest.mark.parametrize(
    "missing_key", ["exclude_dirs", "exclude_globs", "max_file_bytes", "document_extensions"]
)
def test_load_raises_clear_error_when_an_extractor_key_is_missing(
    tmp_path: Path, missing_key: str
) -> None:
    extractor = {k: v for k, v in _MINIMAL["extractor"].items() if k != missing_key}
    data = {**_MINIMAL, "extractor": extractor}
    with pytest.raises(ConfigError, match=missing_key):
        RunConfig.load(_write(tmp_path, data))


def test_load_raises_clear_error_when_max_file_bytes_is_not_positive(tmp_path: Path) -> None:
    extractor = {**_MINIMAL["extractor"], "max_file_bytes": 0}
    data = {**_MINIMAL, "extractor": extractor}
    with pytest.raises(ConfigError, match="max_file_bytes"):
        RunConfig.load(_write(tmp_path, data))


def test_run_config_is_frozen(tmp_path: Path) -> None:
    config = RunConfig.load(_write(tmp_path, _MINIMAL))
    with pytest.raises(AttributeError):
        config.provider = "other"
