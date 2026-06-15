"""Node façade — re-exports the node factories from the split node modules.

The implementations live in ``nodes_shared`` (plan/fix/report — reused across both routes
for instrumentation parity, AW-T8), ``nodes_graph`` (read_vault/hypothesize/validate), and
``nodes_naive`` (dump_repo). Each ``make_*`` returns a LangGraph-compatible node bound to the
injected ``NodeDeps`` (gatekeeper handle, run id, limits, scratch dir).
"""

from __future__ import annotations

from ex04_graphify_agent.agent_workflow.nodes_graph import (
    make_hypothesize,
    make_read_vault,
    make_validate,
)
from ex04_graphify_agent.agent_workflow.nodes_naive import make_dump_repo
from ex04_graphify_agent.agent_workflow.nodes_shared import (
    Node,
    call_llm,
    initial_state,
    make_fix,
    make_plan,
    make_report,
    token_record,
)

__all__ = [
    "Node",
    "call_llm",
    "initial_state",
    "make_dump_repo",
    "make_fix",
    "make_hypothesize",
    "make_plan",
    "make_read_vault",
    "make_report",
    "make_validate",
    "token_record",
]
