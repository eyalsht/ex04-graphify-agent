"""TDD for render_report / write_report (PHASE6-039..047, TC-T1/T9/T10)."""

from __future__ import annotations

from pathlib import Path

from ex04_graphify_agent.token_comparison.runner import TokenComparison
from tests.token_comparison.fixtures.states import graph_guided_state, naive_state

_FIXTURES = Path(__file__).resolve().parent / "fixtures"
_FIXED_SOURCE = (_FIXTURES / "polygons_fixed.txt").read_text(encoding="utf-8")


def _result(tc: TokenComparison) -> object:
    graph_guided = tc.metrics_from_state(graph_guided_state(), 1.0, _FIXED_SOURCE)
    naive = tc.metrics_from_state(naive_state(), 2.0, _FIXED_SOURCE)
    return tc.compare_metrics(graph_guided, naive)


def test_render_report_has_table_with_both_run_rows() -> None:
    """TC-T1: markdown contains a table with rows graph_guided and naive."""
    tc = TokenComparison()
    report = tc.render_report(_result(tc))  # type: ignore[arg-type]
    assert "| graph_guided |" in report
    assert "| naive |" in report


def test_render_report_per_run_token_sums_correct() -> None:
    """TC-T1: the table rows show the correct per-run input/output/total sums."""
    tc = TokenComparison()
    report = tc.render_report(_result(tc))  # type: ignore[arg-type]
    assert "| graph_guided | 1200 | 80 | 1280 |" in report
    assert "| naive | 8000 | 80 | 8080 |" in report


def test_render_report_mandates_files_read_and_iterations_columns() -> None:
    """TC-T9: Files read (3 vs 9) and Iterations (1 vs 1) columns are present."""
    tc = TokenComparison()
    report = tc.render_report(_result(tc))  # type: ignore[arg-type]
    assert "Files read" in report
    assert "Iterations" in report
    assert "| graph_guided | 1200 | 80 | 1280 | 3 | 1 |" in report
    assert "| naive | 8000 | 80 | 8080 | 9 | 1 |" in report


def test_render_report_includes_narrative_sections() -> None:
    tc = TokenComparison()
    report = tc.render_report(_result(tc))  # type: ignore[arg-type]
    assert "## R4.1 - Token reduction" in report
    assert "## R4.2 - Accuracy cost" in report


def test_write_report_writes_file(tmp_path: Path) -> None:
    tc = TokenComparison()
    out_path = tmp_path / "token_comparison.md"
    written = tc.write_report(_result(tc), path=out_path)  # type: ignore[arg-type]
    assert written == out_path
    assert out_path.is_file()
    assert "graph_guided" in out_path.read_text(encoding="utf-8")


def test_write_report_default_path_is_reports_dir() -> None:
    from ex04_graphify_agent.token_comparison.report import default_report_path

    path = default_report_path()
    assert path.name == "token_comparison.md"
    assert path.parent.name == "reports"
