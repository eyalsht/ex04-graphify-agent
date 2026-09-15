"""Notes the report adds when a number would otherwise be read as meaning something else.

A bare "0%" in the coverage column is arithmetically correct and completely misleading: it
says the brief cited nothing, when what happened is that a placeholder provider wrote prose
with no names in it. Reporting the number without the reason is how a true figure becomes a
false impression.
"""

from __future__ import annotations

from repo_atlas.token_comparison.coverage import CoverageMetrics

ZERO_COVERAGE_NOTE = (
    "> Both routes scored zero, which measures the prose rather than the retrieval: an "
    "offline or placeholder provider emits text that names nothing, so there is nothing "
    "for a citation check to find. Coverage only discriminates between the routes on a run "
    "against a real provider."
)


def both_cited_nothing(graph_cov: CoverageMetrics, naive_cov: CoverageMetrics) -> bool:
    """True when neither route cited anything and there was something to cite."""
    had_targets = bool(graph_cov.hot_nodes_total or graph_cov.modules_total)
    nothing_cited = not any(
        (
            graph_cov.hot_nodes_cited,
            graph_cov.modules_cited,
            naive_cov.hot_nodes_cited,
            naive_cov.modules_cited,
        )
    )
    return had_targets and nothing_cited
