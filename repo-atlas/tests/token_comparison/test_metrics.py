"""TDD for build_run_metrics / assert_totals_match_log (PRD R5.2; PHASE5-002)."""

from __future__ import annotations

import pytest

from repo_atlas.brief.models import BriefResult
from repo_atlas.gatekeeper import TokenRecord
from repo_atlas.token_comparison.coverage import CoverageMetrics
from repo_atlas.token_comparison.metrics import assert_totals_match_log, build_run_metrics

_COVERAGE = CoverageMetrics(1, 2, 1, 2)


def _result(token_usage: list[dict[str, object]]) -> BriefResult:
    return BriefResult(
        repo_name="proj",
        run_type="graph_guided",
        files_read=("pkg/core.py",),
        token_usage=token_usage,
    )


def _record(node: str, input_tokens: int, output_tokens: int) -> TokenRecord:
    return TokenRecord(
        run_id="graph_guided",
        run_type="graph_guided",
        node=node,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        model="mock-offline",
    )


def test_build_run_metrics_sums_tokens_from_the_log() -> None:
    result = _result(
        [
            {"node": "section_0", "input_tokens": 10, "output_tokens": 2},
            {"node": "section_1", "input_tokens": 20, "output_tokens": 3},
        ]
    )
    log = [_record("section_0", 10, 2), _record("section_1", 20, 3)]
    metrics = build_run_metrics(result, log, duration_s=1.5, coverage=_COVERAGE)
    assert metrics.input_tokens == 30
    assert metrics.output_tokens == 5
    assert metrics.total_tokens == 35
    assert metrics.num_llm_calls == 2
    assert metrics.files_read == 1
    assert metrics.duration_s == 1.5
    assert metrics.coverage is _COVERAGE


def test_build_run_metrics_raises_when_brief_and_log_disagree() -> None:
    result = _result([{"node": "section_0", "input_tokens": 10, "output_tokens": 2}])
    log = [_record("section_0", 999, 2)]  # tampered/mismatched
    with pytest.raises(ValueError, match="disagree"):
        build_run_metrics(result, log, duration_s=0.0, coverage=_COVERAGE)


def test_build_run_metrics_raises_when_call_counts_differ() -> None:
    result = _result([{"node": "section_0", "input_tokens": 10, "output_tokens": 2}])
    log = [_record("section_0", 10, 2), _record("section_1", 1, 1)]
    with pytest.raises(ValueError, match="disagree"):
        build_run_metrics(result, log, duration_s=0.0, coverage=_COVERAGE)


def test_assert_totals_match_log_passes_when_consistent() -> None:
    result = _result([{"node": "section_0", "input_tokens": 10, "output_tokens": 2}])
    log = [_record("section_0", 10, 2)]
    metrics = build_run_metrics(result, log, duration_s=0.0, coverage=_COVERAGE)
    assert_totals_match_log(metrics, log)  # no raise


def test_assert_totals_match_log_raises_on_a_later_mismatch() -> None:
    result = _result([{"node": "section_0", "input_tokens": 10, "output_tokens": 2}])
    log = [_record("section_0", 10, 2)]
    metrics = build_run_metrics(result, log, duration_s=0.0, coverage=_COVERAGE)
    tampered_log = [_record("section_0", 10, 999)]
    with pytest.raises(ValueError, match="disagrees"):
        assert_totals_match_log(metrics, tampered_log)
