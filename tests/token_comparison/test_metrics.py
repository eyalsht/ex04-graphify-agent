"""TDD for TokenComparison.metrics_from_state (PHASE6-007..014, TC-T1/T6/T10/E5)."""

from __future__ import annotations

from pathlib import Path

import pytest

from ex04_graphify_agent.token_comparison.runner import TokenComparison
from tests.token_comparison.fixtures.states import graph_guided_state, naive_state

_FIXTURES = Path(__file__).resolve().parent / "fixtures"
_FIXED_SOURCE = (_FIXTURES / "polygons_fixed.txt").read_text(encoding="utf-8")


def test_metrics_from_state_sums_tokens() -> None:
    """TC-T1: input/output/total are summed across token_usage."""
    tc = TokenComparison()
    metrics = tc.metrics_from_state(
        graph_guided_state(), duration_s=1.0, fixed_source=_FIXED_SOURCE
    )
    assert metrics.input_tokens == 1_200
    assert metrics.output_tokens == 80
    assert metrics.total_tokens == 1_280


def test_metrics_from_state_per_node_breakdown() -> None:
    """TC-T6: per_node lists each node distinctly (fix != plan)."""
    tc = TokenComparison()
    metrics = tc.metrics_from_state(
        graph_guided_state(), duration_s=1.0, fixed_source=_FIXED_SOURCE
    )
    by_node = {row["node"]: row for row in metrics.per_node}
    assert by_node["plan"]["input_tokens"] == 50
    assert by_node["fix"]["input_tokens"] == 1_150
    assert by_node["fix"] != by_node["plan"]


def test_metrics_from_state_num_llm_calls() -> None:
    tc = TokenComparison()
    metrics = tc.metrics_from_state(
        graph_guided_state(), duration_s=1.0, fixed_source=_FIXED_SOURCE
    )
    assert metrics.num_llm_calls == 2


def test_metrics_from_state_files_read_list_is_evidence() -> None:
    """TC-T10: files_read_list equals the actual paths counted by files_read."""
    tc = TokenComparison()
    state = graph_guided_state()
    metrics = tc.metrics_from_state(state, duration_s=1.0, fixed_source=_FIXED_SOURCE)
    assert metrics.files_read == 3
    assert metrics.files_read_list == state["files_read"]


def test_metrics_from_state_iterations_at_least_one() -> None:
    tc = TokenComparison()
    metrics = tc.metrics_from_state(
        graph_guided_state(), duration_s=1.0, fixed_source=_FIXED_SOURCE
    )
    assert metrics.iterations == 1
    naive_metrics = tc.metrics_from_state(naive_state(), duration_s=1.0, fixed_source=_FIXED_SOURCE)
    assert naive_metrics.iterations == 1  # findings_tried=0 for naive -> floors to 1


def test_metrics_from_state_correctness_uses_fixed_source() -> None:
    tc = TokenComparison()
    metrics = tc.metrics_from_state(
        graph_guided_state(), duration_s=1.0, fixed_source=_FIXED_SOURCE
    )
    assert metrics.correctness is True


def test_metrics_from_state_duration_passthrough() -> None:
    tc = TokenComparison()
    metrics = tc.metrics_from_state(
        graph_guided_state(), duration_s=2.5, fixed_source=_FIXED_SOURCE
    )
    assert metrics.duration_s == 2.5


def test_metrics_from_state_run_type_passthrough() -> None:
    tc = TokenComparison()
    g = tc.metrics_from_state(graph_guided_state(), duration_s=1.0, fixed_source=_FIXED_SOURCE)
    n = tc.metrics_from_state(naive_state(), duration_s=1.0, fixed_source=_FIXED_SOURCE)
    assert g.run_type == "graph_guided"
    assert n.run_type == "naive"


def test_metrics_from_state_fails_loud_on_gatekeeper_log_disagreement() -> None:
    """TC-E5: if a supplied gatekeeper log disagrees with state['token_usage'], fail loud."""
    tc = TokenComparison()
    state = graph_guided_state()
    mismatched_log = [{"node": "plan", "input_tokens": 999, "output_tokens": 5}]
    with pytest.raises(ValueError, match="gatekeeper log"):
        tc.metrics_from_state(
            state,
            duration_s=1.0,
            fixed_source=_FIXED_SOURCE,
            gatekeeper_records=mismatched_log,
        )


def test_metrics_from_state_agrees_with_matching_gatekeeper_log() -> None:
    """TC-E5 (happy path): a matching gatekeeper log does not raise."""
    tc = TokenComparison()
    state = graph_guided_state()
    matching_log = [dict(rec) for rec in state["token_usage"]]
    metrics = tc.metrics_from_state(
        state, duration_s=1.0, fixed_source=_FIXED_SOURCE, gatekeeper_records=matching_log
    )
    assert metrics.total_tokens == 1_280
