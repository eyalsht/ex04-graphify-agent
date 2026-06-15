"""compare_metrics — derive R4.1 (token reduction) / R4.2 (correctness delta) (TC-T2/T3/E2/E4).

Pure functions over already-built ``RunMetrics`` (no I/O), so the reduction-percentage and
narrative logic is independently testable from the ``AgentState`` aggregation step.
"""

from __future__ import annotations

from ex04_graphify_agent.token_comparison.models import ComparisonResult, RunMetrics


def compare_metrics(graph_guided: RunMetrics, naive: RunMetrics) -> ComparisonResult:
    """Build a ``ComparisonResult`` from two already-aggregated ``RunMetrics``."""
    return ComparisonResult(
        graph_guided=graph_guided,
        naive=naive,
        input_token_reduction_pct=_reduction_pct(graph_guided.input_tokens, naive.input_tokens),
        correctness_delta=_correctness_delta(graph_guided.correctness, naive.correctness),
    )


def _reduction_pct(graph_guided_input: int, naive_input: int) -> float:
    """``100 * (naive - graph_guided) / naive``; 0.0 if naive input is 0 (TC-E4)."""
    if naive_input == 0:
        return 0.0
    return round(100.0 * (naive_input - graph_guided_input) / naive_input, 1)


def _correctness_delta(graph_guided_ok: bool, naive_ok: bool) -> str:
    """R4.2 narrative: both pass -> no accuracy cost; otherwise name which failed."""
    if graph_guided_ok and naive_ok:
        return "Both runs passed correctness; the token savings came at no accuracy cost."
    if graph_guided_ok and not naive_ok:
        return (
            "graph_guided passed correctness while naive failed - "
            "token savings came with improved (not worse) localization."
        )
    if not graph_guided_ok and naive_ok:
        return (
            "naive passed correctness while graph_guided failed - "
            "the graph-guided route did not reach the root cause this run."
        )
    return "Both runs failed correctness - neither route reached the root cause this run."
