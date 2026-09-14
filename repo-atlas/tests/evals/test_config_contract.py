"""Structural eval: the shipped config obeys its own contract (PRD R6.2, R6.3, ADR-0003).

Keyless and deterministic — must hold on every run (pass^k = 100%).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

_CONFIG = Path(__file__).resolve().parents[2] / "config" / "atlas.json"


def _config() -> dict[str, Any]:
    data: dict[str, Any] = json.loads(_CONFIG.read_text(encoding="utf-8"))
    return data


def _string_values(
    node: Any, key: str = "", found: list[tuple[str, str]] | None = None
) -> list[tuple[str, str]]:
    """Every ``(key, value)`` string leaf, skipping ``_``-prefixed documentation keys."""
    out = found if found is not None else []
    if isinstance(node, dict):
        for child_key, value in node.items():
            if not str(child_key).startswith("_"):
                _string_values(value, str(child_key), out)
    elif isinstance(node, list):
        for item in node:
            _string_values(item, key, out)
    elif isinstance(node, str):
        out.append((key, node))
    return out


@pytest.mark.eval
def test_config_declares_provider_model_and_key_env() -> None:
    config = _config()
    for key in ("provider", "model", "api_key_env"):
        assert isinstance(config.get(key), str) and config[key], f"missing {key}"


@pytest.mark.eval
def test_config_ships_the_offline_provider_so_the_tool_runs_keyless() -> None:
    assert _config()["provider"] == "offline"


@pytest.mark.eval
def test_config_holds_no_secret_material() -> None:
    """The key is read from os.environ by the name in api_key_env — never stored here."""
    raw = _CONFIG.read_text(encoding="utf-8")
    assert "api_key" not in raw.replace("api_key_env", "")
    assert "sk-" not in raw


@pytest.mark.eval
def test_config_holds_no_filesystem_locations() -> None:
    """Behaviour lives in config; every location enters through the CLI (ADR-0003).

    A bare name like ``.git`` or ``*.lock`` is an ignore rule, not a location. A value with a
    path separator points somewhere specific — which is how the origin project ended up
    pinned to ``data/broken-python`` in a committed JSON file.
    """
    offenders = [
        (key, value) for key, value in _string_values(_config()) if "/" in value or "\\" in value
    ]
    assert offenders == [], f"config values naming a filesystem location: {offenders}"
