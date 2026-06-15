"""TDD for build_graph — the single parameterized StateGraph (AW-T8, PHASE5-062..083)."""

from __future__ import annotations

from ex04_graphify_agent.agent_workflow import graph_def
from ex04_graphify_agent.agent_workflow.deps import NodeDeps


def test_build_graph_guided_compiles(deps: NodeDeps) -> None:
    compiled = graph_def.build_graph("graph_guided", deps)
    assert hasattr(compiled, "invoke")


def test_build_naive_compiles(deps: NodeDeps) -> None:
    compiled = graph_def.build_graph("naive", deps)
    assert hasattr(compiled, "invoke")


def test_both_routes_share_same_plan_fix_report_objects() -> None:
    # AW-T8: instrumentation parity - plan/fix/report node objects are reused, not duplicated.
    shared = graph_def.shared_nodes(_deps())
    assert set(shared) == {"plan", "fix", "report"}


def test_graph_guided_node_set(deps: NodeDeps) -> None:
    names = graph_def.node_names("graph_guided")
    assert names == ["plan", "read_vault", "hypothesize", "validate", "fix", "report"]


def test_naive_node_set(deps: NodeDeps) -> None:
    names = graph_def.node_names("naive")
    assert names == ["plan", "dump_repo", "fix", "report"]


def _deps() -> NodeDeps:
    from pathlib import Path

    from ex04_graphify_agent.agent_workflow import config
    from ex04_graphify_agent.gatekeeper import Gatekeeper, MockClient, TokenLogger

    gk = Gatekeeper(config.agent_config(), TokenLogger(runs_dir=Path(".")), client=MockClient())
    return NodeDeps(gatekeeper=gk, run_id="t")
