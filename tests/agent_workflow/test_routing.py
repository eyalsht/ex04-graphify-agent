"""Validate-router branches + AMBIGUOUS confirm logic (AW-T6 bounded loop)."""

from __future__ import annotations

from ex04_graphify_agent.agent_workflow import graph_def, nodes, nodes_graph
from ex04_graphify_agent.agent_workflow.deps import NodeDeps
from ex04_graphify_agent.weakness_detector import WeaknessFinding


def _state(**over: object) -> dict[str, object]:
    return {**nodes.initial_state("graph_guided"), **over}


def test_router_validated_goes_to_fix(deps: NodeDeps) -> None:
    router = graph_def._route_after_validate(deps)
    assert router(_state(validated=True)) == "fix"


def test_router_budget_exhausted_goes_to_report(deps: NodeDeps) -> None:
    # AW-T6: an unconfirmed finding with no budget left terminates — never loops forever.
    router = graph_def._route_after_validate(deps)
    exhausted = _state(validated=False, findings_tried=deps.limits.max_findings_tried)
    assert router(exhausted) == "report"


def test_router_unconfirmed_with_budget_rehypothesizes(deps: NodeDeps) -> None:
    router = graph_def._route_after_validate(deps)
    assert router(_state(validated=False, findings_tried=0)) == "hypothesize"


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
