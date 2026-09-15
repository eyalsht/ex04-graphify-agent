"""TDD for the provider registry (PHASE4-004): dispatch is data, not an import.

The origin project's ``_build_provider_client`` imported ``GeminiClient`` unconditionally
regardless of ``config["provider"]``. Here every provider name resolves through this
registry, so swapping providers is a one-line addition to ``default_registry`` and never
touches ``Gatekeeper``.
"""

from __future__ import annotations

from repo_atlas.gatekeeper.offline import OfflineClient
from repo_atlas.gatekeeper.provider import GeminiClient
from repo_atlas.gatekeeper.registry import default_registry


def test_default_registry_has_offline_provider() -> None:
    registry = default_registry()
    assert "offline" in registry
    client = registry["offline"]("", "mock-offline")
    assert isinstance(client, OfflineClient)


def test_default_registry_has_gemini_provider() -> None:
    registry = default_registry()
    assert registry["gemini"] is GeminiClient


def test_default_registry_returns_a_fresh_mutable_dict() -> None:
    first = default_registry()
    first["extra"] = GeminiClient
    second = default_registry()
    assert "extra" not in second
