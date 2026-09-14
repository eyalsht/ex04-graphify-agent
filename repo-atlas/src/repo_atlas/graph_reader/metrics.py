"""Degree and betweenness centrality (PRD R2.1, R2.4).

Betweenness is O(V*E) exactly, which is fine for a toy graph and not fine for a real
repository's. Above a configurable node count we switch to networkx's sampled estimator
with a fixed seed, trading a little precision for a bound on runtime while keeping runs
reproducible — an unstable ranking would make ``hot.md`` reshuffle for no reason.
"""

from __future__ import annotations

import networkx as nx  # type: ignore[import-untyped]

#: Above this many nodes, estimate betweenness instead of computing it exactly.
DEFAULT_EXACT_MAX_NODES = 400
#: Pivot count for the sampled estimator.
DEFAULT_SAMPLE_K = 200
#: Fixed so the same graph always yields the same ranking.
_SEED = 7


def degree(graph: nx.Graph) -> dict[str, int]:
    """Per-node degree (number of incident edges)."""
    return {str(node): int(value) for node, value in graph.degree()}


def betweenness(
    graph: nx.Graph,
    exact_max_nodes: int = DEFAULT_EXACT_MAX_NODES,
    sample_k: int = DEFAULT_SAMPLE_K,
) -> dict[str, float]:
    """Per-node betweenness centrality, sampled on graphs above ``exact_max_nodes``."""
    node_count = graph.number_of_nodes()
    if node_count > exact_max_nodes:
        pivots = min(sample_k, node_count)
        scores = nx.betweenness_centrality(graph, k=pivots, seed=_SEED)
    else:
        scores = nx.betweenness_centrality(graph)
    return {str(node): float(value) for node, value in scores.items()}
