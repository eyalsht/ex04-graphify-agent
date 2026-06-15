"""graph_reader — the single typed read path over the Graphify ``graph.json``.

Public API (the contract ``weakness_detector`` / ``obsidian_writer`` build against):
``GraphReader`` plus the ``NodeView`` / ``EdgeView`` / ``Confidence`` data contract and the
pure ``filters`` / ``metrics`` / ``loader`` helpers. See ``docs/PRD_graph_reader.md``.
"""

from __future__ import annotations

from . import filters, loader, metrics
from .loader import default_graph_path, load_graph
from .metrics import betweenness, degree
from .models import Confidence, EdgeView, NodeView
from .reader import GraphReader

__all__ = [
    "Confidence",
    "EdgeView",
    "GraphReader",
    "NodeView",
    "betweenness",
    "default_graph_path",
    "degree",
    "filters",
    "load_graph",
    "loader",
    "metrics",
]
