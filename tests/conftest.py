"""Shared pytest fixtures. Keyless by default — no provider key is ever required."""

from __future__ import annotations

from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def graph_json_path() -> Path:
    """Path to the real PRE-FIX Graphify graph (read-only baseline)."""
    return _REPO_ROOT / "artifacts" / "graphify" / "graph.json"


@pytest.fixture
def repo_root() -> Path:
    """Path to the vendored target repo (the code the agent fixes)."""
    return _REPO_ROOT / "data" / "broken-python"


@pytest.fixture
def obsidian_dir() -> Path:
    """Path to the Obsidian vault."""
    return _REPO_ROOT / "obsidian"


@pytest.fixture
def mock_llm_response() -> dict[str, object]:
    """Deterministic canned LLM response for keyless tests (ADR-0005).

    The real gatekeeper mock is built in Phase 3; this is the canned payload shape.
    """
    return {"text": "", "input_tokens": 0, "output_tokens": 0}
