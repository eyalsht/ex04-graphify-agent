"""Locate the repo root and load ``config/self_grade.json`` (config-driven; no literals)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

_CONFIG_REL = "config/self_grade.json"


def repo_root() -> Path:
    """Repo root resolved from this file: src/ex04_graphify_agent/self_grade/ -> root."""
    return Path(__file__).resolve().parents[3]


def load_config(root: Path | None = None) -> dict[str, Any]:
    """Read the self-grade rubric/requirement-map/baseline config as a dict."""
    base = root if root is not None else repo_root()
    with (base / _CONFIG_REL).open(encoding="utf-8") as handle:
        data: dict[str, Any] = json.load(handle)
    return data


def sha256_of(path: Path) -> str:
    """SHA-256 of a file's bytes — used to prove PRE-FIX baselines are unmodified."""
    return hashlib.sha256(path.read_bytes()).hexdigest()
