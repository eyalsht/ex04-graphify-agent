"""Confidence + community filters and ranking helpers (pure functions).

These operate on already-built ``NodeView`` / ``EdgeView`` lists so every consumer
(``weakness_detector``, ``obsidian_writer``) shares one query path (``docs/PLAN.md`` §4.1).
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable

from .models import Confidence, EdgeView, NodeView


def as_confidence(level: str | Confidence) -> Confidence:
    """Coerce a ``str`` or ``Confidence`` into a ``Confidence`` member."""
    return level if isinstance(level, Confidence) else Confidence(level)


def by_confidence(edges: Iterable[EdgeView], level: str | Confidence) -> list[EdgeView]:
    """Edges whose confidence equals ``level``."""
    wanted = as_confidence(level)
    return [edge for edge in edges if edge.confidence is wanted]


def inferred_below(edges: Iterable[EdgeView], threshold: float) -> list[EdgeView]:
    """INFERRED edges with ``confidence_score`` strictly below ``threshold``."""
    return [
        edge
        for edge in edges
        if edge.confidence is Confidence.INFERRED and edge.confidence_score < threshold
    ]


def group_by_community(nodes: Iterable[NodeView]) -> dict[int, list[NodeView]]:
    """Bucket nodes by their ``community`` id."""
    buckets: dict[int, list[NodeView]] = defaultdict(list)
    for node in nodes:
        buckets[node.community].append(node)
    return dict(buckets)


def in_community(nodes: Iterable[NodeView], community: int) -> list[NodeView]:
    """Nodes belonging to ``community``."""
    return [node for node in nodes if node.community == community]


def _degree_sort_key(node: NodeView) -> tuple[int, float, str]:
    return (-node.degree, -node.betweenness, node.id)


def _betweenness_sort_key(node: NodeView) -> tuple[float, int, str]:
    return (-node.betweenness, -node.degree, node.id)


def _entities(nodes: Iterable[NodeView]) -> list[NodeView]:
    """Drop file-container roots so rankings match GRAPH_REPORT "God Nodes".

    File/module root nodes (sources of ``contains`` edges) are containers, not core
    abstractions — Graphify's "most connected" list excludes them, so ``Polygon``
    (degree 4) outranks the ``polygons.py`` file node (degree 6).
    """
    return [node for node in nodes if not node.is_file_root]


def sort_by_degree(nodes: Iterable[NodeView]) -> list[NodeView]:
    """All God Nodes (file roots excluded) sorted by degree DESC, betweenness DESC, id ASC."""
    return sorted(_entities(nodes), key=_degree_sort_key)


def sort_by_betweenness(nodes: Iterable[NodeView]) -> list[NodeView]:
    """All God Nodes sorted by betweenness DESC, degree DESC, id ASC."""
    return sorted(_entities(nodes), key=_betweenness_sort_key)


def top_n_by_degree(nodes: Iterable[NodeView], n: int) -> list[NodeView]:
    """Top ``n`` God Nodes by degree DESC, betweenness DESC, then id ASC."""
    return sort_by_degree(nodes)[:n]


def top_n_by_betweenness(nodes: Iterable[NodeView], n: int) -> list[NodeView]:
    """Top ``n`` God Nodes by betweenness DESC, degree DESC, then id ASC."""
    return sort_by_betweenness(nodes)[:n]
