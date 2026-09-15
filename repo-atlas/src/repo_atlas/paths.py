"""Every path the tool touches enters here, as an explicit parameter (ADR-0003).

``RunPaths.create`` builds the three paths every pipeline stage needs from CLI-ish arguments.
``RunConfig.load`` turns the atlas config into typed values. Neither caches a module-level
value, walks the filesystem hunting for a project marker, nor reads a global: everything is
computed once, right here, from what the caller passes in.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from repo_atlas.config import RunConfig
from repo_atlas.config_models import (
    BriefConfig,
    ConfigError,
    ExtractorConfig,
    GraphReaderConfig,
    PricingConfig,
    RetryConfig,
    VaultConfig,
)


@dataclass(frozen=True)
class RunPaths:
    """The three paths every pipeline stage needs, resolved to absolute form once."""

    repo_root: Path
    out_dir: Path
    config_path: Path

    @classmethod
    def create(cls, repo: Path, out: Path | None = None, config: Path | None = None) -> RunPaths:
        """Build a ``RunPaths`` from CLI-ish arguments; every field ends up absolute.

        ``repo`` must exist and be a directory. ``out`` defaults to ``<repo>/.atlas``.
        ``config`` defaults to the config shipped with this installation of repo-atlas.
        """
        repo_root = repo.resolve()
        if not repo_root.exists():
            raise FileNotFoundError(f"repo root does not exist: {repo_root}")
        if not repo_root.is_dir():
            raise NotADirectoryError(f"repo root is not a directory: {repo_root}")
        out_dir = (out if out is not None else repo_root / ".atlas").resolve()
        config_path = (config if config is not None else _default_config_path()).resolve()
        return cls(repo_root=repo_root, out_dir=out_dir, config_path=config_path)


def _default_config_path() -> Path:
    """The config shipped with this installation, located relative to this file.

    A fixed two-level jump to this project's own top-level config directory — not the upward
    filesystem *search* ADR-0003 forbids. That rule targets discovering the *target repo*: a
    loop that walks up from ``cwd`` testing each ancestor for a marker so the tool only works
    from inside the checkout it lives in. There is no target repo involved here, no loop, and
    no test-and-continue — just this package's own shipped resource at an offset fixed by the
    repository layout, the same one ``tests/evals/test_config_contract.py`` already relies on.
    """
    project_root = Path(__file__).resolve().parents[2]
    return project_root / "config" / "atlas.json"


# Config types live in ``repo_atlas.config`` — re-exported here because callers naturally
# reach for "paths and config" together, and moving them was a refactor, not an API change.
__all__ = [
    "BriefConfig",
    "ConfigError",
    "ExtractorConfig",
    "GraphReaderConfig",
    "PricingConfig",
    "RetryConfig",
    "RunConfig",
    "RunPaths",
    "VaultConfig",
]
