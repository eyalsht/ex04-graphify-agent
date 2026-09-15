"""Loaders for each optional config section. Split out to keep ``config.py`` inside the cap."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from repo_atlas.config_models import (
    DEFAULT_BACKOFF_SECONDS,
    DEFAULT_CONTEXT_BUDGET,
    DEFAULT_EXACT_MAX_NODES,
    DEFAULT_HOT_SLICES,
    DEFAULT_HOT_TOP_K,
    DEFAULT_HOT_WEIGHTS,
    DEFAULT_MAX_ATTEMPTS,
    DEFAULT_SAMPLE_K,
    BriefConfig,
    ConfigError,
    ExtractorConfig,
    GraphReaderConfig,
    PricingConfig,
    RetryConfig,
    VaultConfig,
)


def load_extractor(raw: dict[str, Any], config_path: Path) -> ExtractorConfig:
    """The one required section — extraction cannot sensibly guess these."""
    section = raw.get("extractor")
    if not isinstance(section, dict):
        raise ConfigError(f"atlas config {config_path} is missing the 'extractor' section")
    return ExtractorConfig(
        exclude_dirs=_str_tuple(section, "exclude_dirs", config_path),
        exclude_globs=_str_tuple(section, "exclude_globs", config_path),
        max_file_bytes=_positive_int(section, "max_file_bytes", config_path),
        document_extensions=_str_tuple(section, "document_extensions", config_path),
    )


def load_vault(section: dict[str, Any]) -> VaultConfig:
    weights = section.get("hot_weights")
    return VaultConfig(
        hot_top_k=int(section.get("hot_top_k", DEFAULT_HOT_TOP_K)),
        hot_weights=dict(weights) if isinstance(weights, dict) else dict(DEFAULT_HOT_WEIGHTS),
    )


def load_graph_reader(section: dict[str, Any]) -> GraphReaderConfig:
    return GraphReaderConfig(
        betweenness_exact_max_nodes=int(
            section.get("betweenness_exact_max_nodes", DEFAULT_EXACT_MAX_NODES)
        ),
        betweenness_sample_k=int(section.get("betweenness_sample_k", DEFAULT_SAMPLE_K)),
    )


def load_brief(section: dict[str, Any]) -> BriefConfig:
    return BriefConfig(
        context_token_budget=int(section.get("context_token_budget", DEFAULT_CONTEXT_BUDGET)),
        hot_source_slices=int(section.get("hot_source_slices", DEFAULT_HOT_SLICES)),
    )


def load_retry(section: dict[str, Any]) -> RetryConfig:
    return RetryConfig(
        max_attempts=int(section.get("max_attempts", DEFAULT_MAX_ATTEMPTS)),
        backoff_seconds=float(section.get("backoff_seconds", DEFAULT_BACKOFF_SECONDS)),
    )


def load_pricing(section: dict[str, Any]) -> PricingConfig:
    return PricingConfig(
        input_per_million_usd=float(section.get("input_per_million_usd", 0.0)),
        output_per_million_usd=float(section.get("output_per_million_usd", 0.0)),
    )


def _str_tuple(section: dict[str, Any], key: str, config_path: Path) -> tuple[str, ...]:
    value = section.get(key)
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return tuple(value)
    raise ConfigError(f"atlas config {config_path} extractor.{key} must be a list of strings")


def _positive_int(section: dict[str, Any], key: str, config_path: Path) -> int:
    value = section.get(key)
    if isinstance(value, int) and not isinstance(value, bool) and value > 0:
        return value
    raise ConfigError(f"atlas config {config_path} extractor.{key} must be a positive integer")
