"""TDD for the typed AgentState / TokenRecord (PHASE5-001..009; R6.1.4)."""

from __future__ import annotations

from typing import get_args, get_type_hints

from ex04_graphify_agent.agent_workflow.state import AgentState, TokenRecord


def test_agent_state_has_all_required_keys() -> None:
    hints = get_type_hints(AgentState)
    expected = {
        "run_type",
        "messages",
        "vault_context",
        "dumped_context",
        "current_hypothesis",
        "validated_source",
        "validated",
        "findings_tried",
        "files_read",
        "fix_diff",
        "token_usage",
    }
    assert expected <= set(hints)


def test_run_type_is_literal_graph_guided_or_naive() -> None:
    hints = get_type_hints(AgentState)
    assert set(get_args(hints["run_type"])) == {"graph_guided", "naive"}


def test_token_record_has_node_and_token_fields() -> None:
    hints = get_type_hints(TokenRecord)
    assert set(hints) >= {"node", "input_tokens", "output_tokens"}
    assert hints["input_tokens"] is int
    assert hints["output_tokens"] is int


def test_files_read_is_a_list() -> None:
    hints = get_type_hints(AgentState)
    assert hints["files_read"] == list[str]


def test_token_usage_is_list_of_token_record() -> None:
    hints = get_type_hints(AgentState)
    assert hints["token_usage"] == list[TokenRecord]
