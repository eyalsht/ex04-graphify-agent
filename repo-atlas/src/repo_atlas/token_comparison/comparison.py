"""compare_metrics — derive the R5.1 token-reduction figure from two RunMetrics.

Pure, no I/O — so the reduction-percentage logic is testable independently of how each
``RunMetrics`` was built.
"""

from __future__ import annotations

from repo_atlas.token_comparison.models import ComparisonResult, RunMetrics


def compare_metrics(graph_guided: RunMetrics, naive: RunMetrics) -> ComparisonResult:
    """Build a ``ComparisonResult`` from two already-aggregated ``RunMetrics``."""
    return ComparisonResult(
        graph_guided=graph_guided,
        naive=naive,
        input_token_reduction_pct=_reduction_pct(graph_guided.input_tokens, naive.input_tokens),
    )


def _reduction_pct(graph_guided_input: int, naive_input: int) -> float:
    """``100 * (naive - graph_guided) / naive``; ``0.0`` when naive used no input tokens."""
    if naive_input == 0:
        return 0.0
    return round(100.0 * (naive_input - graph_guided_input) / naive_input, 1)
