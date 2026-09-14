"""Load ``graph.json`` into an in-memory networkx graph.

The path is always supplied by the caller (ADR-0003). The origin project walked up the
filesystem hunting for its own config file, which is what confined it to one checkout;
here every location arrives through ``RunPaths``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import networkx as nx


def load_graph_data(path: Path) -> dict[str, Any]:
    """Read the raw node-link JSON payload from ``path``."""
    with path.open(encoding="utf-8") as handle:
        data: dict[str, Any] = json.load(handle)
    return data


def build_graph(data: dict[str, Any]) -> nx.Graph[str]:
    """Reconstruct an undirected networkx graph from node-link JSON.

    ``edges="links"`` matches the schema's key name and needs networkx >= 3.4.
    """
    graph: nx.Graph[str] = nx.node_link_graph(data, edges="links")
    return graph


def load_graph(path: str | Path) -> nx.Graph[str]:
    """Load a graph file into a networkx graph."""
    return build_graph(load_graph_data(Path(path)))
