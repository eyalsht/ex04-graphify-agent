"""TDD for TokenComparison.compare (PHASE6-029..038, TC-T2/T3/E2/E4)."""

from __future__ import annotations

from pathlib import Path

from ex04_graphify_agent.token_comparison.runner import TokenComparison
from tests.token_comparison.fixtures.states import graph_guided_state, naive_state

_FIXTURES = Path(__file__).resolve().parent / "fixtures"
_FIXED_SOURCE = (_FIXTURES / "polygons_fixed.txt").read_text(encoding="utf-8")
_BROKEN_SOURCE = "class Polygon(Object):\n    pass\npoly = new Polygon()\n"


def test_compare_input_token_reduction_pct_85() -> None:
    """TC-T2: graph_guided input=1200, naive input=8000 -> 85.0% reduction."""
    tc = TokenComparison()
    graph_guided = tc.metrics_from_state(graph_guided_state(1_200, 80), 1.0, _FIXED_SOURCE)
    naive = tc.metrics_from_state(naive_state(8_000, 80), 1.0, _FIXED_SOURCE)
    result = tc.compare_metrics(graph_guided, naive)
    assert result.input_token_reduction_pct == 85.0


def test_compare_narrative_states_85_percent_fewer() -> None:
    """TC-T2: the rendered narrative states '85% fewer input tokens'."""
    tc = TokenComparison()
    graph_guided = tc.metrics_from_state(graph_guided_state(1_200, 80), 1.0, _FIXED_SOURCE)
    naive = tc.metrics_from_state(naive_state(8_000, 80), 1.0, _FIXED_SOURCE)
    result = tc.compare_metrics(graph_guided, naive)
    report = tc.render_report(result)
    assert "85% fewer input tokens" in report


def test_compare_correctness_delta_no_accuracy_cost_when_both_pass() -> None:
    """TC-T3: both correctness=True -> narrative notes no accuracy cost."""
    tc = TokenComparison()
    graph_guided = tc.metrics_from_state(graph_guided_state(), 1.0, _FIXED_SOURCE)
    naive = tc.metrics_from_state(naive_state(), 1.0, _FIXED_SOURCE)
    result = tc.compare_metrics(graph_guided, naive)
    assert "no accuracy cost" in result.correctness_delta.lower()


def test_compare_correctness_delta_notes_naive_failure() -> None:
    """TC-E2: naive fails correctness -> report still renders, correctness=fail + narrative."""
    tc = TokenComparison()
    graph_guided = tc.metrics_from_state(graph_guided_state(), 1.0, _FIXED_SOURCE)
    naive = tc.metrics_from_state(naive_state(), 1.0, _BROKEN_SOURCE)
    assert naive.correctness is False
    result = tc.compare_metrics(graph_guided, naive)
    assert "fail" in result.correctness_delta.lower()
    report = tc.render_report(result)
    assert "fail" in report.lower()


def test_compare_zero_division_guard_on_naive_input_zero() -> None:
    """TC-E4: naive input_tokens == 0 must not raise ZeroDivisionError."""
    tc = TokenComparison()
    graph_guided = tc.metrics_from_state(graph_guided_state(1_200, 80), 1.0, _FIXED_SOURCE)
    naive = tc.metrics_from_state(naive_state(0, 0), 1.0, _FIXED_SOURCE)
    result = tc.compare_metrics(graph_guided, naive)
    assert result.input_token_reduction_pct == 0.0


def test_check_correctness_method_passthrough() -> None:
    tc = TokenComparison()
    assert tc.check_correctness(_FIXED_SOURCE) is True
    assert tc.check_correctness(_BROKEN_SOURCE) is False


def test_compare_correctness_delta_naive_passes_graph_guided_fails() -> None:
    """Edge case: graph_guided fails correctness while naive passes."""
    tc = TokenComparison()
    graph_guided = tc.metrics_from_state(graph_guided_state(), 1.0, _BROKEN_SOURCE)
    naive = tc.metrics_from_state(naive_state(), 1.0, _FIXED_SOURCE)
    result = tc.compare_metrics(graph_guided, naive)
    assert "naive passed correctness while graph_guided failed" in result.correctness_delta


def test_compare_correctness_delta_both_fail() -> None:
    tc = TokenComparison()
    graph_guided = tc.metrics_from_state(graph_guided_state(), 1.0, _BROKEN_SOURCE)
    naive = tc.metrics_from_state(naive_state(), 1.0, _BROKEN_SOURCE)
    result = tc.compare_metrics(graph_guided, naive)
    assert "Both runs failed correctness" in result.correctness_delta
