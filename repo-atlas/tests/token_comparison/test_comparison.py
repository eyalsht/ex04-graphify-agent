"""TDD for compare_metrics — the R5.1 input-token reduction figure."""

from __future__ import annotations

from repo_atlas.token_comparison.comparison import compare_metrics
from repo_atlas.token_comparison.coverage import CoverageMetrics
from repo_atlas.token_comparison.models import RunMetrics


def _metrics(run_type: str, input_tokens: int) -> RunMetrics:
    return RunMetrics(
        run_type=run_type,
        input_tokens=input_tokens,
        output_tokens=1,
        total_tokens=input_tokens + 1,
        files_read=1,
        num_llm_calls=1,
        duration_s=0.1,
        coverage=CoverageMetrics(0, 0, 0, 0),
    )


def test_reduction_pct_from_naive_to_graph_guided() -> None:
    result = compare_metrics(_metrics("graph_guided", 25), _metrics("naive", 100))
    assert result.input_token_reduction_pct == 75.0


def test_reduction_pct_is_zero_when_naive_used_no_input_tokens() -> None:
    result = compare_metrics(_metrics("graph_guided", 0), _metrics("naive", 0))
    assert result.input_token_reduction_pct == 0.0


def test_reduction_pct_can_be_negative_when_graph_guided_used_more() -> None:
    result = compare_metrics(_metrics("graph_guided", 150), _metrics("naive", 100))
    assert result.input_token_reduction_pct == -50.0
