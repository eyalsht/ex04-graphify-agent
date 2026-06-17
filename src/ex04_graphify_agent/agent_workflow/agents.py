"""The graph-guided multi-agent crew — three specialist subgraphs (ADR-0006).

Each of the lecturer's three roles is a compiled LangGraph subgraph over the shared
``AgentState``:

- **Navigator** (the "GitHub/source" role): ``plan`` -> ``read_vault`` — make the target + the
  Graphify-produced map available and navigate it (index.md + hot.md). It navigates the committed
  map; it does not clone from GitHub at runtime (see ADR-0006 on why this is load-not-clone).
- **Analyst** (the "graph-analysis" role): ``hypothesize`` -> ``validate`` with a bounded internal
  loop — localize the architectural smell on the graph and confirm it against one source file.
- **Fixer** (the "refactor" role): ``fix`` — apply the patch for the validated finding.

The orchestrator in ``graph_def`` wires Navigator -> Analyst -> (Fixer | report). The ``plan`` /
``fix`` node objects are passed in from the shared set so token instrumentation is identical to
the naive route (AW-T8); these subgraphs add no LLM calls of their own.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from types import MappingProxyType

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from ex04_graphify_agent.agent_workflow import nodes
from ex04_graphify_agent.agent_workflow.deps import NodeDeps
from ex04_graphify_agent.agent_workflow.state import AgentState

_Builder = StateGraph[AgentState]

# The lecturer's three roles -> the nodes each specialist agent owns (single source of truth;
# node_names + the workflow diagram are derived from this). Immutable: a read-only proxy over
# tuple values, so this "single source of truth" cannot be mutated by a caller.
CREW: Mapping[str, tuple[str, ...]] = MappingProxyType(
    {
        "navigator": ("plan", "read_vault"),
        "analyst": ("hypothesize", "validate"),
        "fixer": ("fix",),
    }
)


def crew_order() -> list[str]:
    """The agents in orchestration order (Navigator -> Analyst -> Fixer)."""
    return ["navigator", "analyst", "fixer"]


def agent_nodes(agent: str) -> list[str]:
    """The nodes owned by one specialist agent (R5.5.2 inspectable stages)."""
    return list(CREW[agent])


def crew_flat() -> list[str]:
    """Every crew node in execution order (drives ``node_names`` and the diagram)."""
    return [node for agent in crew_order() for node in agent_nodes(agent)]


def _add(builder: _Builder, name: str, node: object) -> None:
    """Register a node or a compiled subgraph. LangGraph's ``add_node`` overloads only accept
    its internal protocol types, not a plain partial-update ``Callable``; one precise,
    centralized ignore is the correct idiom (mirrors ``graph_def._add``)."""
    builder.add_node(name, node)  # type: ignore[call-overload]


def build_navigator_agent(deps: NodeDeps, plan: nodes.Node) -> CompiledStateGraph[AgentState]:
    """Navigator agent: ``plan`` -> ``read_vault`` (navigate the Graphify map, no source read)."""
    builder: _Builder = StateGraph(AgentState)
    _add(builder, "plan", plan)
    _add(builder, "read_vault", nodes.make_read_vault(deps))
    builder.add_edge(START, "plan")
    builder.add_edge("plan", "read_vault")
    builder.add_edge("read_vault", END)
    return builder.compile()


def build_analyst_agent(deps: NodeDeps) -> CompiledStateGraph[AgentState]:
    """Analyst agent: ``hypothesize`` -> ``validate`` with a bounded retry loop."""
    builder: _Builder = StateGraph(AgentState)
    _add(builder, "hypothesize", nodes.make_hypothesize(deps))
    _add(builder, "validate", nodes.make_validate(deps))
    builder.add_edge(START, "hypothesize")
    builder.add_edge("hypothesize", "validate")
    builder.add_conditional_edges(
        "validate", _analyst_router(deps), {"retry": "hypothesize", "done": END}
    )
    return builder.compile()


def build_fixer_agent(deps: NodeDeps, fix: nodes.Node) -> CompiledStateGraph[AgentState]:
    """Fixer agent: ``fix`` — apply the patch for the validated finding."""
    builder: _Builder = StateGraph(AgentState)
    _add(builder, "fix", fix)
    builder.add_edge(START, "fix")
    builder.add_edge("fix", END)
    return builder.compile()


def _analyst_router(deps: NodeDeps) -> Callable[[AgentState], str]:
    """Inside the Analyst agent: confirmed or out of budget -> done; else retry next finding."""
    limit = deps.limits.max_findings_tried

    def router(state: AgentState) -> str:
        if state["validated"] or state["findings_tried"] >= limit:
            return "done"
        return "retry"

    return router


def _post_analyst_router(state: AgentState) -> str:
    """Orchestrator gate: a validated finding runs the Fixer agent; otherwise report only."""
    return "fixer" if state["validated"] else "report"
