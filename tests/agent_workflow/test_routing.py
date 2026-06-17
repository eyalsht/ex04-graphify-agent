"""Crew routing: the Analyst agent's internal loop + the orchestrator's post-Analyst gate.

``_analyst_router`` (inside the Analyst subgraph) bounds the validate->hypothesize loop;
``_post_analyst_router`` (orchestrator level) skips the Fixer agent when the Analyst could not
validate a finding (AW-T6 bounded loop, ADR-0006).
"""

from __future__ import annotations

from ex04_graphify_agent.agent_workflow import agents, nodes, nodes_graph
from ex04_graphify_agent.agent_workflow.deps import NodeDeps
from ex04_graphify_agent.weakness_detector import WeaknessFinding


def _state(**over: object) -> dict[str, object]:
    return {**nodes.initial_state("graph_guided"), **over}


def test_analyst_router_validated_is_done(deps: NodeDeps) -> None:
    router = agents._analyst_router(deps)
    assert router(_state(validated=True)) == "done"


def test_analyst_router_budget_exhausted_is_done(deps: NodeDeps) -> None:
    # AW-T6: an unconfirmed finding with no budget left terminates the loop — never spins forever.
    router = agents._analyst_router(deps)
    exhausted = _state(validated=False, findings_tried=deps.limits.max_findings_tried)
    assert router(exhausted) == "done"


def test_analyst_router_unconfirmed_with_budget_retries(deps: NodeDeps) -> None:
    router = agents._analyst_router(deps)
    assert router(_state(validated=False, findings_tried=0)) == "retry"


def test_post_analyst_router_validated_runs_fixer() -> None:
    assert agents._post_analyst_router(_state(validated=True)) == "fixer"


def test_post_analyst_router_unvalidated_skips_to_report() -> None:
    # No confirmable finding -> the crew skips the Fixer agent and reports honestly.
    assert agents._post_analyst_router(_state(validated=False)) == "report"


def test_validate_with_no_hypothesis_is_unvalidated(deps: NodeDeps) -> None:
    validate = nodes_graph.make_validate(deps)
    assert validate(_state(current_hypothesis=None)) == {"validated": False}


def _ambiguous(*node_ids: str) -> WeaknessFinding:
    return WeaknessFinding(
        signal=6,
        tag="AMBIGUOUS",
        hypothesis="manual source check required",
        priority="primary",
        source_file="polygons/polygons.py",
        nodes=list(node_ids),
    )


def test_ambiguous_confirmed_only_when_source_token_present() -> None:
    source = "def make_polygon(sides):\n    return sides\n"
    assert nodes_graph._confirms(_ambiguous("a_b_polygon"), source) is True
    assert nodes_graph._confirms(_ambiguous("a_b_absenttoken"), source) is False
