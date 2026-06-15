"""hot.md composite ranking — centrality * proximity to the bug node (PLAN §5, R5.6.1).

Scores every entity node (file-container roots excluded) by a *documented, non-arbitrary*
metric: a normalized degree/betweenness centrality blend multiplied by proximity to the
bug location (``1 / (1 + shortest-path distance)``). This pulls the polygons community —
where the bug lives — to the top, instead of the raw-degree metric that floated the
higher-degree mathsquiz README above it (R1.4).
"""

from __future__ import annotations

from collections import deque

from ex04_graphify_agent.graph_reader import GraphReader, NodeView


def bfs_distances(reader: GraphReader, source_id: str) -> dict[str, int]:
    """Undirected BFS hop-distance from ``source_id`` to every reachable node."""
    adjacency: dict[str, list[str]] = {}
    for edge in reader.all_edges():
        adjacency.setdefault(edge.source, []).append(edge.target)
        adjacency.setdefault(edge.target, []).append(edge.source)
    distances = {source_id: 0}
    queue = deque([source_id])
    while queue:
        current = queue.popleft()
        for neighbour in adjacency.get(current, []):
            if neighbour not in distances:
                distances[neighbour] = distances[current] + 1
                queue.append(neighbour)
    return distances


def composite_score(
    node: NodeView, distances: dict[str, int], weights: dict[str, float], norms: tuple[float, float]
) -> float:
    """``(w_deg·degree + w_betw·betweenness)`` (max-normalized) * proximity-to-bug."""
    max_degree, max_betweenness = norms
    centrality = weights["degree"] * (node.degree / max_degree) + weights["betweenness"] * (
        node.betweenness / max_betweenness
    )
    hops = distances.get(node.id)
    proximity = 1.0 / (1.0 + hops) if hops is not None else 0.0
    return centrality * proximity


def rank_nodes(
    reader: GraphReader, top_k: int, weights: dict[str, float], bug_node_id: str
) -> list[NodeView]:
    """Top ``top_k`` entities by composite score (tie-break: degree, betweenness, id)."""
    entities = [node for node in reader.all_nodes() if not node.is_file_root]
    distances = bfs_distances(reader, bug_node_id)
    norms = (
        max((node.degree for node in entities), default=1) or 1,
        max((node.betweenness for node in entities), default=0.0) or 1.0,
    )
    ranked = sorted(
        entities,
        key=lambda node: (
            -composite_score(node, distances, weights, norms),
            -node.degree,
            -node.betweenness,
            node.id,
        ),
    )
    return ranked[:top_k]
