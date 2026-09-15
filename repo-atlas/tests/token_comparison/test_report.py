"""TDD for render_report (PRD R5; PHASE5-007/008/010/011) — no hardcoded prose/numbers."""

from __future__ import annotations

from pathlib import Path

import pytest

from repo_atlas.gatekeeper import TokenRecord
from repo_atlas.token_comparison.coverage import CoverageMetrics
from repo_atlas.token_comparison.models import ComparisonResult, RunMetrics
from repo_atlas.token_comparison.report import render_report, write_report

_ZERO_PRICING = {"input_per_million_usd": 0.0, "output_per_million_usd": 0.0}


def _metrics(run_type: str, input_tokens: int, output_tokens: int = 10) -> RunMetrics:
    return RunMetrics(
        run_type=run_type,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=input_tokens + output_tokens,
        files_read=1,
        num_llm_calls=1,
        duration_s=0.25,
        coverage=CoverageMetrics(1, 2, 1, 2),
        files_read_list=("pkg/core.py",),
    )


def _result(graph_in: int, naive_in: int) -> ComparisonResult:
    pct = round(100.0 * (naive_in - graph_in) / naive_in, 1) if naive_in else 0.0
    return ComparisonResult(
        graph_guided=_metrics("graph_guided", graph_in),
        naive=_metrics("naive", naive_in),
        input_token_reduction_pct=pct,
    )


def test_report_names_the_supplied_repo_and_model() -> None:
    text = render_report(_result(100, 400), _ZERO_PRICING, "widgets", "mock-offline")
    assert "widgets" in text
    assert "mock-offline" in text


def test_report_reduction_pct_is_read_from_the_result_not_hardcoded() -> None:
    text = render_report(_result(25, 100), _ZERO_PRICING, "proj", "m")
    assert "75%" in text
    assert "25" in text and "100" in text


def test_report_offline_pricing_yields_zero_cost() -> None:
    text = render_report(_result(1_000_000, 1_000_000), _ZERO_PRICING, "proj", "m")
    assert "$0.0000" in text


def test_report_cost_reflects_a_real_rate() -> None:
    pricing = {"input_per_million_usd": 2.0, "output_per_million_usd": 0.0}
    text = render_report(_result(1_000_000, 1_000_000), pricing, "proj", "m")
    assert "$2.0000" in text


def test_report_includes_coverage_figures_for_both_routes() -> None:
    text = render_report(_result(25, 100), _ZERO_PRICING, "proj", "m")
    assert "1/2" in text


def test_report_reconciles_against_a_supplied_log_when_it_agrees() -> None:
    result = _result(30, 100)
    log = [TokenRecord("graph_guided", "graph_guided", "section_0", 30, 10, "m")]
    text = render_report(result, _ZERO_PRICING, "proj", "m", graph_log=log)
    assert "proj" in text


def test_report_raises_when_the_supplied_log_disagrees_with_the_metrics() -> None:
    result = _result(30, 100)
    bad_log = [TokenRecord("graph_guided", "graph_guided", "section_0", 999, 10, "m")]
    with pytest.raises(ValueError, match="disagrees"):
        render_report(result, _ZERO_PRICING, "proj", "m", graph_log=bad_log)


def test_report_raises_when_the_naive_log_disagrees_with_the_metrics() -> None:
    result = _result(30, 100)
    bad_log = [TokenRecord("naive", "naive", "section_0", 1, 10, "m")]
    with pytest.raises(ValueError, match="disagrees"):
        render_report(result, _ZERO_PRICING, "proj", "m", naive_log=bad_log)


def test_write_report_creates_parent_dirs_and_returns_the_path(tmp_path: Path) -> None:
    result = _result(25, 100)
    out = tmp_path / "reports" / "token_comparison.md"
    written = write_report(result, _ZERO_PRICING, "proj", "m", out)
    assert written == out
    assert "proj" in out.read_text(encoding="utf-8")


def _result_with_coverage(coverage: CoverageMetrics, naive_same: bool = True) -> ComparisonResult:
    graph = _metrics("graph_guided", 100)
    naive = _metrics("naive", 500)
    graph.coverage = coverage
    naive.coverage = coverage if naive_same else CoverageMetrics(1, 2, 1, 2)
    return ComparisonResult(graph_guided=graph, naive=naive, input_token_reduction_pct=80.0)


def test_zero_coverage_on_both_routes_is_explained_not_left_bare() -> None:
    """Offline placeholder prose cites nothing, so coverage is structurally 0 for both
    routes. Printing a bare 0% invites the reader to conclude the brief was empty."""
    result = _result_with_coverage(CoverageMetrics(0, 5, 0, 9))
    body = render_report(result, _ZERO_PRICING, "proj", "mock-offline")
    assert "placeholder" in body.lower()


def test_nonzero_coverage_is_not_given_the_caveat() -> None:
    result = _result_with_coverage(CoverageMetrics(3, 5, 4, 9), naive_same=False)
    body = render_report(result, _ZERO_PRICING, "proj", "some-model")
    assert "placeholder" not in body.lower()
