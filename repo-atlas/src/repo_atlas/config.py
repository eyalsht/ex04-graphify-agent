"""Typed view over ``atlas.json``. Behaviour only — never a location (ADR-0003).

Split from ``paths.py`` so that module stays about *where things are* and this one about
*how the tool should act*. Sections other than ``extractor`` are optional with documented
defaults: a minimal config must still run, and a partially-specified section must keep
the defaults for the keys it does not mention rather than blanking them.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from repo_atlas import config_sections as sections
from repo_atlas.config_models import (
    DEFAULT_RATE_LIMIT,
    BriefConfig,
    ConfigError,
    ExtractorConfig,
    GraphReaderConfig,
    PricingConfig,
    RetryConfig,
    VaultConfig,
)


@dataclass(frozen=True)
class RunConfig:
    """Everything the tool reads from configuration."""

    provider: str
    model: str
    api_key_env: str
    extractor: ExtractorConfig
    vault: VaultConfig = field(default_factory=VaultConfig)
    graph_reader: GraphReaderConfig = field(default_factory=GraphReaderConfig)
    brief: BriefConfig = field(default_factory=BriefConfig)
    retry: RetryConfig = field(default_factory=RetryConfig)
    pricing: PricingConfig = field(default_factory=PricingConfig)
    rate_limit_per_minute: int = DEFAULT_RATE_LIMIT

    @classmethod
    def load(cls, config_path: Path) -> RunConfig:
        """Read and validate ``config_path``. Fails loudly; never guesses a required value."""
        raw = _read(config_path)
        return cls(
            provider=_require_str(raw, "provider", config_path),
            model=_require_str(raw, "model", config_path),
            api_key_env=_require_str(raw, "api_key_env", config_path),
            extractor=_load_extractor(raw, config_path),
            vault=_load_vault(raw, config_path),
            graph_reader=_load_graph_reader(raw, config_path),
            brief=_load_brief(raw, config_path),
            retry=_load_retry(raw, config_path),
            pricing=_load_pricing(raw, config_path),
            rate_limit_per_minute=int(raw.get("rate_limit_per_minute", DEFAULT_RATE_LIMIT)),
        )

    def gatekeeper_config(self) -> dict[str, Any]:
        """The dict the gatekeeper reads — sourced from typed config, not a second re-read."""
        return {
            "provider": self.provider,
            "model": self.model,
            "api_key_env": self.api_key_env,
            "rate_limit_per_minute": self.rate_limit_per_minute,
            "retry": {
                "max_attempts": self.retry.max_attempts,
                "backoff_seconds": self.retry.backoff_seconds,
            },
        }


_SECTIONS = ("vault", "graph_reader", "brief", "retry", "pricing")


def _load_extractor(raw: dict[str, Any], config_path: Path) -> ExtractorConfig:
    return sections.load_extractor(raw, config_path)


def _load_vault(raw: dict[str, Any], config_path: Path) -> VaultConfig:
    return sections.load_vault(_optional_section(raw, "vault", config_path))


def _load_graph_reader(raw: dict[str, Any], config_path: Path) -> GraphReaderConfig:
    return sections.load_graph_reader(_optional_section(raw, "graph_reader", config_path))


def _load_brief(raw: dict[str, Any], config_path: Path) -> BriefConfig:
    return sections.load_brief(_optional_section(raw, "brief", config_path))


def _load_retry(raw: dict[str, Any], config_path: Path) -> RetryConfig:
    return sections.load_retry(_optional_section(raw, "retry", config_path))


def _load_pricing(raw: dict[str, Any], config_path: Path) -> PricingConfig:
    return sections.load_pricing(_optional_section(raw, "pricing", config_path))


def _read(config_path: Path) -> dict[str, Any]:
    if not config_path.is_file():
        raise ConfigError(f"atlas config not found: {config_path}")
    try:
        raw = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigError(f"atlas config is not valid JSON: {config_path} ({exc})") from exc
    if not isinstance(raw, dict):
        raise ConfigError(f"atlas config must be a JSON object: {config_path}")
    return raw


def _require_str(raw: dict[str, Any], key: str, config_path: Path) -> str:
    value = raw.get(key)
    if isinstance(value, str) and value:
        return value
    raise ConfigError(f"atlas config {config_path} is missing required key {key!r}")


def _optional_section(raw: dict[str, Any], key: str, config_path: Path) -> dict[str, Any]:
    """An absent section is fine; a present one that is not an object is not."""
    section = raw.get(key)
    if section is None:
        return {}
    if not isinstance(section, dict):
        raise ConfigError(f"atlas config {config_path} section {key!r} must be a JSON object")
    return section
