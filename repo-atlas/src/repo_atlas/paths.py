"""Every path the tool touches enters here, as an explicit parameter (ADR-0003).

``RunPaths.create`` builds the three paths every pipeline stage needs from CLI-ish arguments.
``RunConfig.load`` turns the atlas config into typed values. Neither caches a module-level
value, walks the filesystem hunting for a project marker, nor reads a global: everything is
computed once, right here, from what the caller passes in.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class ConfigError(RuntimeError):
    """The atlas config file is missing, unreadable, or missing a required key."""


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


@dataclass(frozen=True)
class ExtractorConfig:
    """The ``extractor`` section of the atlas config (PRD R1.3)."""

    exclude_dirs: tuple[str, ...]
    exclude_globs: tuple[str, ...]
    max_file_bytes: int
    document_extensions: tuple[str, ...]


@dataclass(frozen=True)
class RunConfig:
    """Typed view over the atlas config. Behaviour only — never a location (ADR-0003)."""

    provider: str
    model: str
    api_key_env: str
    extractor: ExtractorConfig

    @classmethod
    def load(cls, config_path: Path) -> RunConfig:
        """Read and validate ``config_path``. Fails loudly; never guesses a missing value."""
        if not config_path.is_file():
            raise ConfigError(f"atlas config not found: {config_path}")
        try:
            raw = json.loads(config_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ConfigError(f"atlas config is not valid JSON: {config_path} ({exc})") from exc
        if not isinstance(raw, dict):
            raise ConfigError(f"atlas config must be a JSON object: {config_path}")
        return cls(
            provider=_require_str(raw, "provider", config_path),
            model=_require_str(raw, "model", config_path),
            api_key_env=_require_str(raw, "api_key_env", config_path),
            extractor=_load_extractor(raw, config_path),
        )


def _require_str(raw: dict[str, Any], key: str, config_path: Path) -> str:
    value = raw.get(key)
    if isinstance(value, str) and value:
        return value
    raise ConfigError(f"atlas config {config_path} is missing required key {key!r}")


def _load_extractor(raw: dict[str, Any], config_path: Path) -> ExtractorConfig:
    section = raw.get("extractor")
    if not isinstance(section, dict):
        raise ConfigError(f"atlas config {config_path} is missing the 'extractor' section")
    return ExtractorConfig(
        exclude_dirs=_require_str_tuple(section, "exclude_dirs", config_path),
        exclude_globs=_require_str_tuple(section, "exclude_globs", config_path),
        max_file_bytes=_require_positive_int(section, "max_file_bytes", config_path),
        document_extensions=_require_str_tuple(section, "document_extensions", config_path),
    )


def _require_str_tuple(section: dict[str, Any], key: str, config_path: Path) -> tuple[str, ...]:
    value = section.get(key)
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return tuple(value)
    raise ConfigError(f"atlas config {config_path} extractor.{key} must be a list of strings")


def _require_positive_int(section: dict[str, Any], key: str, config_path: Path) -> int:
    value = section.get(key)
    if isinstance(value, int) and not isinstance(value, bool) and value > 0:
        return value
    raise ConfigError(f"atlas config {config_path} extractor.{key} must be a positive integer")
