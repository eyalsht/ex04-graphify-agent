"""build_graph — ONE parameterized StateGraph keyed on run_type (ADR-0001, AW-T8).

A single compiled graph selects its route by ``run_type``; the shared plan/fix/report node
objects are reused across both routes so the gatekeeper token instrumentation is identical
(the comparison measures context strategy alone). The graph-guided route adds a bounded
validate->hypothesize loop: an unconfirmed AMBIGUOUS finding falls through to the next-ranked
finding (findings_tried += 1) and terminates at max_findings_tried (AW-E1/AW-T6).
"""

from __future__ import annotations

from collections.abc import Callable

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from ex04_graphify_agent.agent_workflow import nodes
from ex04_graphify_agent.agent_workflow.deps import NodeDeps
from ex04_graphify_agent.agent_workflow.state import AgentState, RunType

_Builder = StateGraph[AgentState]
_GRAPH_NODES = ["plan", "read_vault", "hypothesize", "validate", "fix", "report"]
_NAIVE_NODES = ["plan", "dump_repo", "fix", "report"]


def node_names(run_type: RunType) -> list[str]:
    """The documented node order for each route (R5.3.3)."""
    return list(_GRAPH_NODES) if run_type == "graph_guided" else list(_NAIVE_NODES)


def shared_nodes(deps: NodeDeps) -> dict[str, nodes.Node]:
    """The plan/fix/report node objects reused by BOTH routes (AW-T8 parity)."""
    return {
        "plan": nodes.make_plan(deps),
        "fix": nodes.make_fix(deps),
        "report": nodes.make_report(deps),
    }


def build_graph(run_type: RunType, deps: NodeDeps) -> CompiledStateGraph[AgentState]:
    """Compile the route for ``run_type`` from one shared node set (single graph)."""
    shared = shared_nodes(deps)
    builder: _Builder = StateGraph(AgentState)
    if run_type == "graph_guided":
        _wire_graph_guided(builder, deps, shared)
    else:
        _wire_naive(builder, shared, deps)
    return builder.compile()


def _add(builder: _Builder, name: str, node: nodes.Node) -> None:
    """Register a node — centralizes the langgraph stub narrowing (nodes return partial state)."""
    builder.add_node(name, node)  # type: ignore[call-overload]


def _wire_naive(builder: _Builder, shared: dict[str, nodes.Node], deps: NodeDeps) -> None:
    _add(builder, "plan", shared["plan"])
    _add(builder, "dump_repo", nodes.make_dump_repo(deps))
    _add(builder, "fix", shared["fix"])
    _add(builder, "report", shared["report"])
    builder.add_edge(START, "plan")
    builder.add_edge("plan", "dump_repo")
    builder.add_edge("dump_repo", "fix")
    builder.add_edge("fix", "report")
    builder.add_edge("report", END)


def _wire_graph_guided(builder: _Builder, deps: NodeDeps, shared: dict[str, nodes.Node]) -> None:
    _add(builder, "plan", shared["plan"])
    _add(builder, "read_vault", nodes.make_read_vault(deps))
    _add(builder, "hypothesize", nodes.make_hypothesize(deps))
    _add(builder, "validate", nodes.make_validate(deps))
    _add(builder, "fix", shared["fix"])
    _add(builder, "report", shared["report"])
    builder.add_edge(START, "plan")
    builder.add_edge("plan", "read_vault")
    builder.add_edge("read_vault", "hypothesize")
    builder.add_edge("hypothesize", "validate")
    builder.add_conditional_edges(
        "validate",
        _route_after_validate(deps),
        {"fix": "fix", "hypothesize": "hypothesize", "report": "report"},
    )
    builder.add_edge("fix", "report")
    builder.add_edge("report", END)


def _route_after_validate(deps: NodeDeps) -> Callable[[AgentState], str]:
    """Validated -> fix; unconfirmed & budget left -> re-hypothesize; else -> report."""
    limit = deps.limits.max_findings_tried

    def router(state: AgentState) -> str:
        if state["validated"]:
            return "fix"
        if state["findings_tried"] >= limit:
            return "report"
        return "hypothesize"

    return router
