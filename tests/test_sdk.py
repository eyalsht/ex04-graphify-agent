"""Smoke test for the SDK façade package (real surface lands per-phase)."""

from __future__ import annotations

from pathlib import Path

import ex04_graphify_agent.sdk as sdk
from ex04_graphify_agent.sdk import Ex04Sdk


def test_sdk_module_importable() -> None:
    assert sdk.__doc__ is not None


def test_generate_hot_writes_hot_md_to_given_vault(tmp_path: Path) -> None:
    out = Ex04Sdk().generate_hot(vault_dir=tmp_path)
    assert out == tmp_path / "hot.md"
    assert out.exists()
    assert out.read_text(encoding="utf-8").startswith("# Hot — Where to look first")


def test_generate_hot_default_vault_is_config_driven() -> None:
    out = Ex04Sdk().generate_hot()
    assert out.name == "hot.md"
    assert out.parent.name == "obsidian"
