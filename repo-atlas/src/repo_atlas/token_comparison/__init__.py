"""token_comparison — graph-guided vs naive-dump evidence (PRD R5; ADR-0002).

No bug-fix machinery here (no correctness oracle, no graph diff, no patch applier — those
were the origin project's and this fork dropped them). What is measured is whether a
generated brief is cheaper *and* still says something: token/cost metrics from the
gatekeeper's own log, and a coverage measure of what the brief actually cites.
"""

from __future__ import annotations

from repo_atlas.token_comparison.comparison import compare_metrics
from repo_atlas.token_comparison.cost import PricingError, cost_usd, require_pricing
from repo_atlas.token_comparison.coverage import CoverageMetrics, compute_coverage
from repo_atlas.token_comparison.metrics import assert_totals_match_log, build_run_metrics
from repo_atlas.token_comparison.models import ComparisonResult, RunMetrics
from repo_atlas.token_comparison.report import render_report, write_report
from repo_atlas.token_comparison.runner import ComparisonRunner

__all__ = [
    "ComparisonResult",
    "ComparisonRunner",
    "CoverageMetrics",
    "PricingError",
    "RunMetrics",
    "assert_totals_match_log",
    "build_run_metrics",
    "compare_metrics",
    "compute_coverage",
    "cost_usd",
    "render_report",
    "require_pricing",
    "write_report",
]
