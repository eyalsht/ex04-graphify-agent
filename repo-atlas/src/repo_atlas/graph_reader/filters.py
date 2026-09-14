"""Pure filters and orderings over ``NodeView`` / ``EdgeView`` sequences.

Kept free of I/O and of the reader so they can be composed and tested directly.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from repo_atlas.graph_reader.models import Confidence, EdgeView, NodeView


def as_confidence(level: str | Confidence) -> Confidence:
    """Coerce a string to a ``Confidence``, tolerating case."""
    if isinstance(level, Confidence):
        return level
    return Confidence(level.strip().upper())


def by_confidence(edges: Iterable[EdgeView], level: str | Confidence) -> list[EdgeView]:
    """Edges at exactly this confidence level."""
    wanted = as_confidence(level)
    return [edge for edge in edges if edge.confidence is wanted]


def inferred_below(edges: Iterable[EdgeView], threshold: float) -> list[EdgeView]:
    """INFERRED edges weak enough to deserve a source check before being believed."""
    return [
        edge
        for edge in edges
        if edge.confidence is Confidence.INFERRED and edge.confidence_score < threshold
    ]


def group_by_community(nodes: Iterable[NodeView]) -> dict[int, list[NodeView]]:
    """Nodes bucketed by community id."""
    grouped: dict[int, list[NodeView]] = {}
    for node in nodes:
        grouped.setdefault(node.community, []).append(node)
    return grouped


def in_community(nodes: Iterable[NodeView], community: int) -> list[NodeView]:
    """Nodes belonging to one community."""
    return [node for node in nodes if node.community == community]


def entities(nodes: Iterable[NodeView]) -> list[NodeView]:
    """Drop file-root nodes.

    A file node's degree counts everything it contains, so it mechanically outranks its
    own contents. That tells a reader nothing about where the interesting code is, so
    rankings are computed over entities only.
    """
    return [node for node in nodes if not node.is_file_root]


def sort_by_degree(nodes: Iterable[NodeView]) -> list[NodeView]:
    """Most connected first, ties broken deterministically."""
    return sorted(nodes, key=lambda n: (-n.degree, -n.betweenness, n.id))


def sort_by_betweenness(nodes: Iterable[NodeView]) -> list[NodeView]:
    """Strongest bridges first, ties broken deterministically."""
    return sorted(nodes, key=lambda n: (-n.betweenness, -n.degree, n.id))


def top_n_by_degree(nodes: Sequence[NodeView], count: int) -> list[NodeView]:
    """The ``count`` most connected entities."""
    return sort_by_degree(entities(nodes))[:count]


def top_n_by_betweenness(nodes: Sequence[NodeView], count: int) -> list[NodeView]:
    """The ``count`` strongest bridging entities."""
    return sort_by_betweenness(entities(nodes))[:count]
