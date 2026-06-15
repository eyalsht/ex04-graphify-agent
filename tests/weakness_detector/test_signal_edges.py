"""Edge-case branches for the signals (empty-graph tolerance, id-keyed access)."""

from __future__ import annotations

from pathlib import Path

import networkx as nx

from ex04_graphify_agent.graph_reader import GraphReader
from ex04_graphify_agent.weakness_detector import signals_graph_b, signals_source


def _empty_reader(tmp_path: Path) -> GraphReader:
    data = nx.node_link_data(nx.Graph(), edges="links")
    p = tmp_path / "empty.json"
    p.write_text(__import__("json").dumps(data), encoding="utf-8")
    return GraphReader(p)


def test_signal_4_empty_when_nodes_absent(tmp_path: Path) -> None:
    assert signals_graph_b.critical_path_break(_empty_reader(tmp_path)) == []


def test_signal_5_empty_when_no_rationale(tmp_path: Path) -> None:
    thresholds = {"isolated_cluster_max_edges": 1}
    assert signals_graph_b.isolated_cluster(_empty_reader(tmp_path), thresholds) == []


def test_signal_6_empty_when_nodes_absent(tmp_path: Path) -> None:
    assert signals_source.semantic_duplicate(_empty_reader(tmp_path), tmp_path) == []
