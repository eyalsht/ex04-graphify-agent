"""Config-driven paths/weights for ``obsidian_writer`` (CLAUDE.md §3: no hardcoded values).

Mirrors the resolution pattern used by ``graph_reader.loader`` — walk up from this file
until ``config/paths.json`` is found, then read ``config/paths.json`` /
``config/weakness_thresholds.json`` for the vault dir and ``hot.md`` ranking knobs.
"""

from __future__ import annotations

import functools
import json
from pathlib import Path
from typing import Any

_PATHS_CONFIG = "config/paths.json"
_THRESHOLDS_CONFIG = "config/weakness_thresholds.json"


@functools.cache
def _find_repo_root() -> Path:
    """Walk up from this module until a directory containing ``config/`` is found."""
    for parent in Path(__file__).resolve().parents:
        if (parent / _PATHS_CONFIG).is_file():
            return parent
    msg = f"could not locate {_PATHS_CONFIG} above {__file__}"
    raise FileNotFoundError(msg)


def _load_json(relative_path: str) -> dict[str, Any]:
    root = _find_repo_root()
    data: dict[str, Any] = json.loads((root / relative_path).read_text(encoding="utf-8"))
    return data


def default_vault_dir() -> Path:
    """Resolve the Obsidian vault directory from ``config/paths.json`` (``obsidian_dir``)."""
    config = _load_json(_PATHS_CONFIG)
    return _find_repo_root() / str(config["obsidian_dir"])


def default_hot_md_top_k() -> int:
    """Resolve the default ``hot.md`` top-k from ``config/weakness_thresholds.json``."""
    config = _load_json(_THRESHOLDS_CONFIG)
    return int(config["hot_md_top_k"])
