"""RunMetrics / ComparisonResult — the R5 evidence shapes.

No ``correctness``/``iterations`` fields here (unlike the origin project's): there is no
bug-fix loop to score pass/fail, and the brief pipeline is linear rather than an
hypothesize/validate loop (ADR-0002). ``coverage`` replaces the correctness column.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from repo_atlas.token_comparison.coverage import CoverageMetrics


@dataclass
class RunMetrics:
    """One route's aggregated evidence: tokens, files, calls, timing, and coverage."""

    run_type: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    files_read: int
    num_llm_calls: int
    duration_s: float
    coverage: CoverageMetrics
    files_read_list: tuple[str, ...] = field(default_factory=tuple)


@dataclass
class ComparisonResult:
    """Both routes' metrics plus the derived token-reduction figure (PRD R5.1)."""

    graph_guided: RunMetrics
    naive: RunMetrics
    input_token_reduction_pct: float
