"""GraphReader — the single typed read path over the Graphify ``graph.json``.

No other module parses ``graph.json`` directly (R5.2.1). Builds ``NodeView`` /
``EdgeView`` objects once at construction (degree + betweenness precomputed) and exposes
the query surface that ``weakness_detector`` and ``obsidian_writer`` depend on.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import networkx as nx  # type: ignore[import-untyped]

from . import filters, metrics
from .loader import build_graph, default_graph_path, load_graph_data
from .models import Confidence, EdgeView, NodeView


class GraphReader:
    """Typed, in-memory query layer over a single ``graph.json`` baseline."""

    def __init__(self, graph_path: str | Path | None = None) -> None:
        resolved = Path(graph_path) if graph_path is not None else default_graph_path()
        data = load_graph_data(resolved)
        self._graph: nx.Graph = build_graph(data)
        self._roots = _file_root_ids(data)
        self._degree = metrics.degree(self._graph)
        self._betweenness = metrics.betweenness(self._graph)
        self._nodes = self._build_nodes()
        self._edges = self._build_edges()

    def _build_nodes(self) -> dict[str, NodeView]:
        nodes: dict[str, NodeView] = {}
        for node_id, attrs in self._graph.nodes(data=True):
            key = str(node_id)
            nodes[key] = NodeView(
                id=key,
                label=str(attrs.get("label", key)),
                file_type=str(attrs.get("file_type", "")),
                source_file=str(attrs.get("source_file", "")),
                source_location=_clean_location(attrs.get("source_location")),
                community=int(attrs.get("community", -1)),
                norm_label=str(attrs.get("norm_label", "")),
                degree=self._degree[key],
                betweenness=self._betweenness[key],
                is_file_root=key in self._roots,
            )
        return nodes

    def _build_edges(self) -> list[EdgeView]:
        edges: list[EdgeView] = []
        for source, target, attrs in self._graph.edges(data=True):
            edges.append(_edge_view(str(source), str(target), attrs))
        return edges

    # -- node queries -----------------------------------------------------
    def node(self, node_id: str) -> NodeView:
        return self._nodes[node_id]

    def node_exists(self, node_id: str) -> bool:
        return node_id in self._nodes

    def all_nodes(self) -> list[NodeView]:
        return list(self._nodes.values())

    # -- metrics ----------------------------------------------------------
    def degree(self, node_id: str) -> int:
        return self._nodes[node_id].degree

    def betweenness(self, node_id: str) -> float:
        return self._nodes[node_id].betweenness

    def top_n_by_degree(self, n: int) -> list[NodeView]:
        return filters.top_n_by_degree(self._nodes.values(), n)

    def top_n_by_betweenness(self, n: int) -> list[NodeView]:
        return filters.top_n_by_betweenness(self._nodes.values(), n)

    # -- communities ------------------------------------------------------
    def nodes_in_community(self, community: int) -> list[NodeView]:
        return filters.in_community(self._nodes.values(), community)

    def communities(self) -> dict[int, list[NodeView]]:
        return filters.group_by_community(self._nodes.values())

    # -- edges ------------------------------------------------------------
    def all_edges(self) -> list[EdgeView]:
        return list(self._edges)

    def edges_with_confidence(self, confidence: str | Confidence) -> list[EdgeView]:
        return filters.by_confidence(self._edges, confidence)

    def inferred_edges_below(self, threshold: float) -> list[EdgeView]:
        return filters.inferred_below(self._edges, threshold)

    def edges_of(self, node_id: str) -> list[EdgeView]:
        if node_id not in self._nodes:
            raise KeyError(node_id)
        return [edge for edge in self._edges if node_id in (edge.source, edge.target)]


def _file_root_ids(data: dict[str, Any]) -> set[str]:
    """Ids that are the ``source`` of a ``contains`` edge (file/module containers)."""
    return {
        str(link["source"]) for link in data.get("links", []) if link.get("relation") == "contains"
    }


def _clean_location(value: Any) -> str | None:
    """Treat ``null`` and empty-string ``source_location`` as ``None``."""
    if value is None or value == "":
        return None
    return str(value)


def _edge_view(source: str, target: str, attrs: dict[str, Any]) -> EdgeView:
    return EdgeView(
        source=source,
        target=target,
        relation=str(attrs.get("relation", "")),
        confidence=Confidence(str(attrs.get("confidence", "EXTRACTED"))),
        confidence_score=float(attrs.get("confidence_score", 0.0)),
        weight=float(attrs.get("weight", 0.0)),
        source_file=str(attrs.get("source_file", "")),
        source_location=_clean_location(attrs.get("source_location")),
    )
