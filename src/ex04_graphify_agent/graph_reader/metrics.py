"""Degree / betweenness centrality over the loaded networkx graph.

Thin wrappers around networkx so the metric code stays simple and correct
(``docs/PLAN.md`` §4.1). Returned dicts are keyed by node id.
"""

from __future__ import annotations

import networkx as nx  # type: ignore[import-untyped]


def degree(graph: nx.Graph) -> dict[str, int]:
    """Per-node degree (number of incident edges)."""
    return {str(node): int(deg) for node, deg in graph.degree()}


def betweenness(graph: nx.Graph) -> dict[str, float]:
    """Per-node betweenness centrality (cross-community bridge proxy)."""
    return {str(node): float(value) for node, value in nx.betweenness_centrality(graph).items()}
