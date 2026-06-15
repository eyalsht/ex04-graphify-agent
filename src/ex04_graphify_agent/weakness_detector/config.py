"""Config-driven threshold + path loading for the weakness detector.

No threshold literal lives in detector logic (CLAUDE.md §3). Thresholds come from
``config/weakness_thresholds.json``; the repo root (and thus default config / data paths)
is discovered by walking up to the directory holding ``config/``. Missing config fails
loud (WD-E5) — no silently-baked defaults.
"""

from __future__ import annotations

import functools
import json
from pathlib import Path
from typing import Any

_THRESHOLDS_CONFIG = "config/weakness_thresholds.json"
_DATA_ROOT_KEY = "data_repo_root"
_PATHS_CONFIG = "config/paths.json"


@functools.cache
def repo_root() -> Path:
    """Walk up from this module to the directory containing ``config/`` (cached)."""
    for parent in Path(__file__).resolve().parents:
        if (parent / _THRESHOLDS_CONFIG).is_file():
            return parent
    msg = f"could not locate {_THRESHOLDS_CONFIG} above {__file__}"
    raise FileNotFoundError(msg)


def default_thresholds_path() -> Path:
    """The config-driven default thresholds file path."""
    return repo_root() / _THRESHOLDS_CONFIG


def load_thresholds(path: str | Path | None = None) -> dict[str, Any]:
    """Read tunable detector thresholds; fail loud if the file is absent (WD-E5)."""
    resolved = Path(path) if path is not None else default_thresholds_path()
    if not resolved.is_file():
        msg = f"weakness thresholds config not found: {resolved}"
        raise FileNotFoundError(msg)
    data: dict[str, Any] = json.loads(resolved.read_text(encoding="utf-8"))
    return data


def default_data_root() -> Path:
    """Resolve ``data/broken-python/`` from ``config/paths.json`` (config-driven)."""
    root = repo_root()
    paths = json.loads((root / _PATHS_CONFIG).read_text(encoding="utf-8"))
    return root / str(paths[_DATA_ROOT_KEY])
