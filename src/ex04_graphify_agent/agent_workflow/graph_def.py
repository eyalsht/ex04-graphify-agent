"""build_graph — the route compiler keyed on run_type (ADR-0001, ADR-0006, AW-T8).

``run_type`` selects the topology. **graph_guided** is a three-agent crew (ADR-0006): the
orchestrator wires the Navigator -> Analyst -> (Fixer | report) specialist subgraphs from
``agents.py``. **naive** is the deliberately monolithic baseline (one flat pipeline) — the
"Lost in the Middle" control. The shared plan/fix/report node objects are reused across both
routes so the gatekeeper token instrumentation is identical (the comparison measures context
strategy alone). The analysis agent owns the bounded validate->hypothesize loop: an unconfirmed
AMBIGUOUS finding falls through to the next-ranked finding (findings_tried += 1) and terminates
at max_findings_tried (AW-E1/AW-T6); the orchestrator then skips refactor when nothing validated.
"""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from ex04_graphify_agent.agent_workflow import agents, nodes
from ex04_graphify_agent.agent_workflow.deps import NodeDeps
from ex04_graphify_agent.agent_workflow.state import AgentState, RunType

_Builder = StateGraph[AgentState]
_NAIVE_NODES = ["plan", "dump_repo", "fix", "report"]


def node_names(run_type: RunType) -> list[str]:
    """The documented node execution order for each route (R5.3.3).

    For graph_guided this is the crew's nodes flattened in orchestration order plus the
    orchestrator's final ``report`` — derived from ``agents.CREW`` so there is one source of truth.
    """
    if run_type == "graph_guided":
        return [*agents.crew_flat(), "report"]
    return list(_NAIVE_NODES)


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


def _add(builder: _Builder, name: str, node: object) -> None:
    """Register a node or a compiled subgraph. LangGraph's ``add_node`` overloads only accept
    its internal protocol types, not a plain partial-update ``Callable``; this one precise,
    centralized ignore is the correct idiom (cleaner than a blanket ``cast(Any)``).
    """
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
    """Orchestrate the three specialist agents (ADR-0006): the Navigator, Analyst and Fixer
    subgraphs are composed as nodes; the orchestrator owns the final ``report`` and the
    post-analysis gate that skips the Fixer when the Analyst validated nothing."""
    _add(builder, "navigator", agents.build_navigator_agent(deps, shared["plan"]))
    _add(builder, "analyst", agents.build_analyst_agent(deps))
    _add(builder, "fixer", agents.build_fixer_agent(deps, shared["fix"]))
    _add(builder, "report", shared["report"])
    builder.add_edge(START, "navigator")
    builder.add_edge("navigator", "analyst")
    builder.add_conditional_edges(
        "analyst",
        agents._post_analyst_router,
        {"fixer": "fixer", "report": "report"},
    )
    builder.add_edge("fixer", "report")
    builder.add_edge("report", END)
