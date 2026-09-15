"""Config value types and their defaults.

Separated from loading so the shapes are readable on their own: what the tool can be
told, and what it assumes when it is not told.
"""

from __future__ import annotations

from dataclasses import dataclass, field

DEFAULT_HOT_TOP_K = 8
DEFAULT_HOT_WEIGHTS: dict[str, float] = {"degree": 0.6, "betweenness": 0.4}
DEFAULT_EXACT_MAX_NODES = 400
DEFAULT_SAMPLE_K = 200
DEFAULT_CONTEXT_BUDGET = 8000
DEFAULT_HOT_SLICES = 5
DEFAULT_RATE_LIMIT = 30
DEFAULT_MAX_ATTEMPTS = 6
DEFAULT_BACKOFF_SECONDS = 3.0


class ConfigError(RuntimeError):
    """Raised when the atlas config is missing, malformed, or incomplete."""


@dataclass(frozen=True)
class ExtractorConfig:
    """The ``extractor`` section (PRD R1.3). Required — extraction cannot guess these."""

    exclude_dirs: tuple[str, ...]
    exclude_globs: tuple[str, ...]
    max_file_bytes: int
    document_extensions: tuple[str, ...]


@dataclass(frozen=True)
class VaultConfig:
    """How ``hot.md`` is ranked."""

    hot_top_k: int = DEFAULT_HOT_TOP_K
    hot_weights: dict[str, float] = field(default_factory=lambda: dict(DEFAULT_HOT_WEIGHTS))


@dataclass(frozen=True)
class GraphReaderConfig:
    """When to stop computing betweenness exactly (PRD R2.4)."""

    betweenness_exact_max_nodes: int = DEFAULT_EXACT_MAX_NODES
    betweenness_sample_k: int = DEFAULT_SAMPLE_K


@dataclass(frozen=True)
class BriefConfig:
    """How much context the brief is allowed to assemble (PRD R4.1)."""

    context_token_budget: int = DEFAULT_CONTEXT_BUDGET
    hot_source_slices: int = DEFAULT_HOT_SLICES


@dataclass(frozen=True)
class RetryConfig:
    """Provider retry policy."""

    max_attempts: int = DEFAULT_MAX_ATTEMPTS
    backoff_seconds: float = DEFAULT_BACKOFF_SECONDS


@dataclass(frozen=True)
class PricingConfig:
    """USD per million tokens, so a cost figure is reproducible from logged counts."""

    input_per_million_usd: float = 0.0
    output_per_million_usd: float = 0.0
