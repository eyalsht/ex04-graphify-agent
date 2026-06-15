"""Loader helper coverage: config-driven default path + raw networkx access."""

from __future__ import annotations

from pathlib import Path

import pytest

from ex04_graphify_agent.graph_reader import GraphReader, load_graph
from ex04_graphify_agent.graph_reader.loader import default_graph_path


def test_default_graph_path_resolves_from_config() -> None:
    path = default_graph_path()
    assert path.name == "graph.json"
    assert path.is_file()


def test_load_graph_default_matches_explicit(graph_json_path: Path) -> None:
    explicit = load_graph(graph_json_path)
    default = load_graph()
    assert explicit.number_of_nodes() == default.number_of_nodes() == 23
    assert explicit.number_of_edges() == default.number_of_edges() == 20


def test_load_graph_accepts_str(graph_json_path: Path) -> None:
    graph = load_graph(str(graph_json_path))
    assert graph.number_of_nodes() == 23


def test_edges_of_unknown_node_raises(graph_json_path: Path) -> None:
    reader = GraphReader(str(graph_json_path))
    with pytest.raises(KeyError):
        reader.edges_of("nope_missing")
