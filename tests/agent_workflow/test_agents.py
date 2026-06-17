"""TDD for the graph-guided multi-agent crew (ADR-0006).

The graph-guided route is three specialist LangGraph subgraphs — Navigator (navigates the
Graphify map), Analyst (localizes against source), Fixer (applies the fix) — composed by the
orchestrator in ``graph_def.build_graph``. Each agent owns a distinct role; the LLM calls
(plan, fix) and the per-node context are unchanged from the flat graph, so token parity holds.
"""

from __future__ import annotations

from langgraph.graph.state import CompiledStateGraph

from ex04_graphify_agent.agent_workflow import agents, nodes
from ex04_graphify_agent.agent_workflow.deps import NodeDeps


def test_three_agents_compile(deps: NodeDeps) -> None:
    assert isinstance(agents.build_navigator_agent(deps, nodes.make_plan(deps)), CompiledStateGraph)
    assert isinstance(agents.build_analyst_agent(deps), CompiledStateGraph)
    assert isinstance(agents.build_fixer_agent(deps, nodes.make_fix(deps)), CompiledStateGraph)


def test_crew_role_to_nodes_mapping() -> None:
    # The lecturer's three roles -> the nodes each specialist owns (ADR-0006).
    assert agents.agent_nodes("navigator") == ["plan", "read_vault"]
    assert agents.agent_nodes("analyst") == ["hypothesize", "validate"]
    assert agents.agent_nodes("fixer") == ["fix"]
    assert agents.crew_order() == ["navigator", "analyst", "fixer"]
    # crew_flat is the execution order across all three agents (drives node_names + the diagram).
    assert agents.crew_flat() == ["plan", "read_vault", "hypothesize", "validate", "fix"]


def test_navigator_agent_loads_map_without_reading_source(deps: NodeDeps) -> None:
    # Navigator role: plan + navigate the Graphify map (index.md/hot.md). No source opened yet.
    agent = agents.build_navigator_agent(deps, nodes.make_plan(deps))
    out = agent.invoke(nodes.initial_state("graph_guided"))
    assert out["vault_context"]
    assert "polygon" in out["vault_context"].lower()
    assert out["validated_source"] is None  # the Analyst hasn't run
    assert len(out["files_read"]) == 2  # index.md + hot.md only
    assert any(r["node"] == "plan" for r in out["token_usage"])


def test_analyst_agent_localizes_against_source(deps: NodeDeps) -> None:
    # Analyst role: hypothesize + validate -> a validated finding on the bug file.
    out = agents.build_analyst_agent(deps).invoke(nodes.initial_state("graph_guided"))
    assert out["validated"] is True
    assert out["current_hypothesis"].source_file == "polygons/polygons.py"
    assert out["findings_tried"] >= 1


def test_fixer_agent_emits_a_diff(deps: NodeDeps) -> None:
    # Fixer role: fix -> a patch for the validated finding. Driven through the real
    # Navigator+Analyst pipeline so the input state is exactly what the orchestrator hands it.
    navigated = agents.build_navigator_agent(deps, nodes.make_plan(deps)).invoke(
        nodes.initial_state("graph_guided")
    )
    analyzed = agents.build_analyst_agent(deps).invoke(navigated)
    out = agents.build_fixer_agent(deps, nodes.make_fix(deps)).invoke(analyzed)
    assert out["fix_diff"] is not None
    assert out["target_file"] == "polygons/polygons.py"
    assert any(r["node"] == "fix" for r in out["token_usage"])
