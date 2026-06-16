"""RunMetrics / ComparisonResult dataclasses (PHASE6-001..004).

Mirrors the public-interface sketch in ``docs/PRD_token_comparison.md``. ``RunMetrics``
captures the mandated R5.6.5 columns for a single run (graph_guided or naive);
``ComparisonResult`` pairs both runs with the R4.1/R4.2 derived narrative inputs.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class RunMetrics:
    """Per-run metrics — tokens, files/iterations (R5.6.5 (b)/(c)), correctness."""

    run_type: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    files_read: int
    iterations: int
    num_llm_calls: int
    duration_s: float
    correctness: bool
    per_node: list[dict[str, object]] = field(default_factory=list)
    files_read_list: list[str] = field(default_factory=list)


@dataclass
class ComparisonResult:
    """Both runs' metrics plus the derived R4.1 (token reduction) / R4.2 (accuracy) facts."""

    graph_guided: RunMetrics
    naive: RunMetrics
    input_token_reduction_pct: float
    correctness_delta: str
