"""NodeDeps — the per-run dependencies bound into each LangGraph node (kept out of state).

LangGraph nodes are functions of ``state`` only, so the gatekeeper handle, run id, loop
limits, and the scratch dir for the fix write are injected via this frozen container at
graph-build time (closures in ``graph_def``). The scratch dir guarantees the fix node never
overwrites the vendored ``polygons.py`` baseline during tests (CLAUDE.md §4 / PHASE5-120).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from ex04_graphify_agent.agent_workflow.config import RunLimits, load_limits
from ex04_graphify_agent.gatekeeper import Gatekeeper


@dataclass(frozen=True)
class NodeDeps:
    """Injected, run-scoped dependencies shared by both run types."""

    gatekeeper: Gatekeeper
    run_id: str
    scratch_dir: Path | None = None
    limits: RunLimits = field(default_factory=load_limits)
