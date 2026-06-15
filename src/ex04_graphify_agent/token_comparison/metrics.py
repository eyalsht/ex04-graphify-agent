"""metrics_from_state aggregation helpers (PHASE6-007..014, TC-T1/T6/T10/E5).

``state["token_usage"]`` is the per-node mirror of the gatekeeper's per-call log (AW-T7 —
``nodes_shared.token_record``), so it is the authoritative token source for a completed
``AgentState`` (R10.5). When an explicit ``gatekeeper_records`` log is supplied (e.g. a
``TokenLogger`` dump), it is cross-checked against ``token_usage`` and any disagreement
fails loud (TC-E5) rather than silently picking a number.
"""

from __future__ import annotations

from typing import Any

from ex04_graphify_agent.agent_workflow.state import AgentState
from ex04_graphify_agent.token_comparison.correctness import check_correctness
from ex04_graphify_agent.token_comparison.models import RunMetrics


def build_run_metrics(
    state: AgentState,
    duration_s: float,
    fixed_source: str,
    gatekeeper_records: list[dict[str, Any]] | None = None,
) -> RunMetrics:
    """Aggregate one completed ``AgentState`` into a ``RunMetrics`` (R5.6.5)."""
    token_usage = state["token_usage"]
    if gatekeeper_records is not None:
        _assert_logs_agree(token_usage, gatekeeper_records)
    input_tokens = sum(rec["input_tokens"] for rec in token_usage)
    output_tokens = sum(rec["output_tokens"] for rec in token_usage)
    files_read = state["files_read"]
    return RunMetrics(
        run_type=state["run_type"],
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=input_tokens + output_tokens,
        files_read=len(files_read),
        iterations=max(state["findings_tried"], 1),
        num_llm_calls=len(token_usage),
        duration_s=duration_s,
        correctness=check_correctness(fixed_source),
        per_node=[dict(rec) for rec in token_usage],
        files_read_list=list(files_read),
    )


def _token_view(rec: dict[str, Any]) -> dict[str, Any]:
    """Project a token-usage record to its comparable (node, input, output) fields."""
    return {
        "node": rec["node"],
        "input_tokens": rec["input_tokens"],
        "output_tokens": rec["output_tokens"],
    }


def _assert_logs_agree(token_usage: list[Any], gatekeeper_records: list[dict[str, Any]]) -> None:
    """TC-E5: ``state['token_usage']`` must match the supplied gatekeeper log exactly."""
    state_view = [_token_view(rec) for rec in token_usage]
    log_view = [_token_view(rec) for rec in gatekeeper_records]
    if state_view != log_view:
        msg = (
            "token_usage and the supplied gatekeeper log disagree "
            f"(state={state_view!r} vs log={log_view!r}) - refusing to report estimates (R10.5)"
        )
        raise ValueError(msg)
