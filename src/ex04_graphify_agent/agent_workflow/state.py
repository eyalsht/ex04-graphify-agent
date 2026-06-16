"""AgentState (typed) — the single state object passed between LangGraph nodes.

Shared by both run types so the gatekeeper token instrumentation is identical across the
graph-guided and naive routes (R6.1.4 — explicit typed state, not ad-hoc dicts). Every
node that pulls a file into context appends to ``files_read`` (R5.6.5); every gatekeeper
call appends one ``TokenRecord`` to ``token_usage`` (AW-T7). See
``docs/PRD_agent_workflow.md`` §"State schema".
"""

from __future__ import annotations

from typing import Any, Literal, TypedDict

from ex04_graphify_agent.weakness_detector import WeaknessFinding

RunType = Literal["graph_guided", "naive"]


class TokenRecord(TypedDict):
    """One LLM call's token accounting, mirrored from the gatekeeper response (AW-T7)."""

    node: str
    input_tokens: int
    output_tokens: int


class AgentState(TypedDict):
    """Typed LangGraph state — every node's input/output is inspectable here (R5.5.2)."""

    run_type: RunType
    messages: list[dict[str, Any]]
    vault_context: str
    dumped_context: str
    current_hypothesis: WeaknessFinding | None
    validated_source: str | None
    validated: bool
    findings_tried: int
    files_read: list[str]
    target_file: str | None  # repo-relative path the run is fixing (from the hypothesis / LLM)
    fix_diff: str | None
    token_usage: list[TokenRecord]
