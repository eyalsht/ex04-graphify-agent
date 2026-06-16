"""Config-driven paths + run limits for agent_workflow (CLAUDE.md §3: no hardcoded values).

Mirrors the resolution pattern used by ``graph_reader`` / ``obsidian_writer`` — walk up to
the directory holding ``config/``, then read ``config/agent.json`` (provider, model,
api_key_env, loop bounds) and ``config/paths.json`` (vault + repo paths). No path or model
literal ever lives in node logic.
"""

from __future__ import annotations

import functools
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_AGENT_CONFIG = "config/agent.json"
_PATHS_CONFIG = "config/paths.json"


@dataclass(frozen=True)
class RunLimits:
    """Stop-condition bounds from ``config/agent.json`` (default 3 / 1)."""

    max_findings_tried: int
    max_validation_attempts: int


@functools.cache
def _repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / _AGENT_CONFIG).is_file():
            return parent
    msg = f"could not locate {_AGENT_CONFIG} above {__file__}"
    raise FileNotFoundError(msg)


@functools.cache
def _load(relative_path: str) -> dict[str, Any]:
    data: dict[str, Any] = json.loads((_repo_root() / relative_path).read_text(encoding="utf-8"))
    return data


def agent_config() -> dict[str, Any]:
    """The raw agent runtime config dict (passed verbatim to the gatekeeper)."""
    return _load(_AGENT_CONFIG)


def load_limits() -> RunLimits:
    """Resolve the loop bounds (config-driven, never hardcoded in node logic)."""
    cfg = agent_config()
    return RunLimits(
        max_findings_tried=int(cfg["max_findings_tried"]),
        max_validation_attempts=int(cfg["max_validation_attempts"]),
    )


def _path(key: str) -> Path:
    return _repo_root() / str(_load(_PATHS_CONFIG)[key])


def index_md_path() -> Path:
    """``obsidian/index.md`` (graph-guided map; read by read_vault)."""
    return _path("index_md")


def hot_md_path() -> Path:
    """``obsidian/hot.md`` (Phase-4 ranked map; read by read_vault)."""
    return _path("hot_md")


def data_repo_root() -> Path:
    """``data/broken-python`` root (naive dump source / source-file resolution root)."""
    return _path("data_repo_root")


def repo_path(relative: str) -> Path:
    """Resolve a repo-relative source path (e.g. a finding's ``source_file``) under the repo.

    The validate/fix nodes resolve whatever file the hypothesis (or the naive LLM) names —
    there is no hardcoded target file in node logic (CLAUDE.md §3).
    """
    return data_repo_root() / relative
