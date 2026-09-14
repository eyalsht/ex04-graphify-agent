"""``GraphReader`` — the query surface over one extracted graph (PRD R2).

Two deliberate departures from the origin project. Unknown confidence values degrade to
AMBIGUOUS with a warning instead of raising, so a graph from another producer is
readable rather than fatal; and adjacency is indexed once at construction instead of
rescanning every edge per lookup, which was O(V*E) across a whole vault render.
"""

from __future__ import annotations

from pathlib import Path

import networkx as nx  # type: ignore[import-untyped]

from repo_atlas.graph_reader import filters, loader, metrics, views
from repo_atlas.graph_reader.models import Confidence, EdgeView, NodeView

CONTAINS = "contains"


class GraphReader:
    """Loads a graph once, then answers questions about it."""

    def __init__(
        self,
        graph_path: str | Path,
        exact_max_nodes: int = metrics.DEFAULT_EXACT_MAX_NODES,
        sample_k: int = metrics.DEFAULT_SAMPLE_K,
    ) -> None:
        self._data = loader.load_graph_data(Path(graph_path))
        self._graph: nx.Graph = loader.build_graph(self._data)
        degrees = metrics.degree(self._graph)
        betweens = metrics.betweenness(self._graph, exact_max_nodes, sample_k)
        self._edges = tuple(
            views.edge_view(source, target, attrs)
            for source, target, attrs in self._graph.edges(data=True)
        )
        roots = {edge.source for edge in self._edges if edge.relation == CONTAINS}
        self._nodes = {
            node_id: views.node_view(node_id, attrs, degrees, betweens, roots)
            for node_id, attrs in self._graph.nodes(data=True)
        }
        self._incident: dict[str, list[EdgeView]] = {node_id: [] for node_id in self._nodes}
        for edge in self._edges:
            for endpoint in (edge.source, edge.target):
                if endpoint in self._incident:
                    self._incident[endpoint].append(edge)

    def node(self, node_id: str) -> NodeView:
        """One node, by id. Raises ``KeyError`` if it is not in the graph."""
        return self._nodes[node_id]

    def node_exists(self, node_id: str) -> bool:
        """Whether the graph contains this id."""
        return node_id in self._nodes

    def all_nodes(self) -> list[NodeView]:
        """Every node."""
        return list(self._nodes.values())

    def all_edges(self) -> list[EdgeView]:
        """Every edge."""
        return list(self._edges)

    def top_n_by_degree(self, count: int) -> list[NodeView]:
        """The most connected entities (file roots excluded)."""
        return filters.top_n_by_degree(self.all_nodes(), count)

    def top_n_by_betweenness(self, count: int) -> list[NodeView]:
        """The strongest bridging entities (file roots excluded)."""
        return filters.top_n_by_betweenness(self.all_nodes(), count)

    def communities(self) -> dict[int, list[NodeView]]:
        """Nodes grouped by community id."""
        return filters.group_by_community(self.all_nodes())

    def nodes_in_community(self, community: int) -> list[NodeView]:
        """Nodes in one community."""
        return filters.in_community(self.all_nodes(), community)

    def edges_with_confidence(self, level: str | Confidence) -> list[EdgeView]:
        """Edges at exactly one confidence level."""
        return filters.by_confidence(self._edges, level)

    def inferred_edges_below(self, threshold: float) -> list[EdgeView]:
        """INFERRED edges weak enough to warrant a source check."""
        return filters.inferred_below(self._edges, threshold)

    def edges_of(self, node_id: str) -> list[EdgeView]:
        """Edges incident to a node, from the index built at construction."""
        return list(self._incident[node_id])
