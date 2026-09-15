"""Rank the nodes worth reading first (PRD R3.2, R3.3).

Score is a weighted blend of degree and betweenness, each normalised against the
graph's maximum. With a ``seed_id`` it is additionally multiplied by proximity to that
node, ``1 / (1 + hops)``, so "what matters near here" beats "what matters overall".

The origin project made the seed mandatory and hardcoded to one bug node. Worse, when
that id was missing from the graph every node scored 0.0 and the ranking silently
collapsed to alphabetical — while the rendered output still claimed it had ranked by
proximity. Here the seed is optional, and an explicit seed that is not in the graph is
an error rather than a quiet lie.
"""

from __future__ import annotations

from collections import deque
from collections.abc import Mapping

from repo_atlas.graph_reader import GraphReader
from repo_atlas.graph_reader.filters import entities
from repo_atlas.graph_reader.models import NodeView

DEGREE = "degree"
BETWEENNESS = "betweenness"

#: Test code is real structure and often a repo's best documentation, so it stays on the
#: map — but someone asking "where do I start reading" means the source. Without this, a
#: helper called by a dozen tests in one file outranks the code it exercises.
DEFAULT_TEST_PENALTY = 0.3
_TEST_FILENAMES = ("conftest.py",)
_TEST_PREFIX = "test_"
_TEST_SUFFIX = "_test.py"
_TEST_DIRS = ("tests", "test")


def is_test_path(source_file: str) -> bool:
    """Whether a repo-relative path looks like test code, by layout convention."""
    if not source_file:
        return False
    parts = source_file.split("/")
    name = parts[-1]
    if name in _TEST_FILENAMES or name.startswith(_TEST_PREFIX) or name.endswith(_TEST_SUFFIX):
        return True
    return any(part in _TEST_DIRS for part in parts[:-1])


def bfs_distances(reader: GraphReader, source_id: str) -> dict[str, int]:
    """Hop counts from ``source_id`` to every node it can reach."""
    adjacency: dict[str, set[str]] = {}
    for edge in reader.all_edges():
        adjacency.setdefault(edge.source, set()).add(edge.target)
        adjacency.setdefault(edge.target, set()).add(edge.source)
    distances = {source_id: 0}
    queue = deque([source_id])
    while queue:
        current = queue.popleft()
        for neighbour in sorted(adjacency.get(current, ())):
            if neighbour not in distances:
                distances[neighbour] = distances[current] + 1
                queue.append(neighbour)
    return distances


def _normalisers(nodes: list[NodeView]) -> tuple[float, float]:
    max_degree = max((node.degree for node in nodes), default=0) or 1
    max_betweenness = max((node.betweenness for node in nodes), default=0.0) or 1.0
    return float(max_degree), max_betweenness


def _centrality(node: NodeView, weights: Mapping[str, float], norms: tuple[float, float]) -> float:
    max_degree, max_betweenness = norms
    return weights.get(DEGREE, 0.0) * (node.degree / max_degree) + weights.get(BETWEENNESS, 0.0) * (
        node.betweenness / max_betweenness
    )


def score_nodes(
    reader: GraphReader,
    weights: Mapping[str, float],
    seed_id: str | None = None,
    test_penalty: float = DEFAULT_TEST_PENALTY,
) -> dict[str, float]:
    """Score every entity node. Raises ``KeyError`` if an explicit seed is unknown."""
    if seed_id is not None and not reader.node_exists(seed_id):
        raise KeyError(
            f"seed node {seed_id!r} is not in this graph — "
            "pass an id the graph contains, or omit the seed to rank on centrality alone"
        )
    candidates = entities(reader.all_nodes())
    norms = _normalisers(candidates)
    distances = bfs_distances(reader, seed_id) if seed_id is not None else None
    scores: dict[str, float] = {}
    for node in candidates:
        score = _centrality(node, weights, norms)
        if is_test_path(node.source_file):
            score *= test_penalty
        if distances is not None:
            hops = distances.get(node.id)
            score = 0.0 if hops is None else score / (1 + hops)
        scores[node.id] = score
    return scores


def rank_nodes(
    reader: GraphReader,
    top_k: int,
    weights: Mapping[str, float],
    seed_id: str | None = None,
    test_penalty: float = DEFAULT_TEST_PENALTY,
) -> list[NodeView]:
    """The ``top_k`` nodes worth reading first, most important last-tie-broken by id."""
    scores = score_nodes(reader, weights, seed_id, test_penalty)
    candidates = entities(reader.all_nodes())
    ordered = sorted(candidates, key=lambda n: (-scores[n.id], -n.degree, -n.betweenness, n.id))
    return ordered[:top_k]


def metric_description(weights: Mapping[str, float], seed_id: str | None) -> str:
    """One honest sentence naming the metric actually used, for the rendered header."""
    blend = (
        f"{weights.get(DEGREE, 0.0):g}*degree + {weights.get(BETWEENNESS, 0.0):g}*betweenness, "
        "each normalised against this graph's maximum"
    )
    if seed_id is None:
        return f"Ranked by centrality ({blend})."
    return f"Ranked by centrality ({blend}) * proximity to `{seed_id}` (1 / (1 + hops))."
