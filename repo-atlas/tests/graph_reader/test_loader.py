"""Loading graph.json from an explicit path (ADR-0003: no upward config discovery)."""

from __future__ import annotations

from pathlib import Path

import pytest

from repo_atlas.graph_reader import loader
from tests.fixtures import graph_factory


def _written(tmp_path: Path) -> Path:
    data = graph_factory.graph_dict(nodes=["a", "b", "c"], edges=[("a", "b"), ("b", "c")])
    return graph_factory.write_graph(tmp_path, data)


def test_loads_nodes_and_edges_from_a_given_path(tmp_path: Path) -> None:
    graph = loader.load_graph(_written(tmp_path))
    assert sorted(graph.nodes) == ["a", "b", "c"]
    assert graph.number_of_edges() == 2


def test_graph_is_undirected() -> None:
    graph = loader.build_graph(graph_factory.graph_dict(nodes=["a"]))
    assert graph.is_directed() is False


def test_node_attributes_survive_the_round_trip(tmp_path: Path) -> None:
    data = graph_factory.graph_dict(nodes=[graph_factory.make_node("a", community=7)])
    graph = loader.load_graph(graph_factory.write_graph(tmp_path, data))
    assert graph.nodes["a"]["community"] == 7


def test_a_missing_file_raises_a_clear_error(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        loader.load_graph(tmp_path / "absent.json")


def test_an_empty_graph_loads(tmp_path: Path) -> None:
    path = graph_factory.write_graph(tmp_path, graph_factory.graph_dict())
    assert loader.load_graph(path).number_of_nodes() == 0
