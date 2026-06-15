"""Smoke test for the SDK façade package (real surface lands per-phase)."""

from __future__ import annotations

import ex04_graphify_agent.sdk as sdk


def test_sdk_module_importable() -> None:
    assert sdk.__doc__ is not None
