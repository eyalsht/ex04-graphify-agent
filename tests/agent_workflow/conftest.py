"""Fixtures for agent_workflow tests — keyless gatekeeper + wired NodeDeps (ADR-0005)."""

from __future__ import annotations

from pathlib import Path

import pytest

from ex04_graphify_agent.agent_workflow import config
from ex04_graphify_agent.agent_workflow.deps import NodeDeps
from ex04_graphify_agent.gatekeeper import Gatekeeper, MockClient, TokenLogger


@pytest.fixture
def gatekeeper() -> Gatekeeper:
    """Keyless gatekeeper driven by the deterministic MockClient (no real API call)."""
    return Gatekeeper(config.agent_config(), TokenLogger(runs_dir=Path(".")), client=MockClient())


@pytest.fixture
def deps(gatekeeper: Gatekeeper, tmp_path: Path) -> NodeDeps:
    """NodeDeps wired to a scratch dir so the fix node never overwrites the baseline."""
    return NodeDeps(gatekeeper=gatekeeper, run_id="test-run", scratch_dir=tmp_path)
