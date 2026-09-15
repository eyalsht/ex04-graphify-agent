"""TDD for the RunMetrics / ComparisonResult shapes (no correctness/iterations — ADR-0002)."""

from __future__ import annotations

from repo_atlas.token_comparison.coverage import CoverageMetrics
from repo_atlas.token_comparison.models import ComparisonResult, RunMetrics


def _metrics(run_type: str) -> RunMetrics:
    return RunMetrics(
        run_type=run_type,
        input_tokens=10,
        output_tokens=2,
        total_tokens=12,
        files_read=1,
        num_llm_calls=1,
        duration_s=0.5,
        coverage=CoverageMetrics(1, 2, 1, 2),
        files_read_list=("a.py",),
    )


def test_run_metrics_has_no_correctness_or_iterations_fields() -> None:
    fields = _metrics("graph_guided").__dataclass_fields__
    assert "correctness" not in fields
    assert "iterations" not in fields


def test_comparison_result_pairs_both_run_metrics() -> None:
    result = ComparisonResult(
        graph_guided=_metrics("graph_guided"),
        naive=_metrics("naive"),
        input_token_reduction_pct=50.0,
    )
    assert result.graph_guided.run_type == "graph_guided"
    assert result.naive.run_type == "naive"
    assert result.input_token_reduction_pct == 50.0
