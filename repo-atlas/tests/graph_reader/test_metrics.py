"""Degree and betweenness, including the large-graph sampling switch (PRD R2.4)."""

from __future__ import annotations

from repo_atlas.graph_reader import loader, metrics
from tests.fixtures import graph_factory


def _star(spokes: int) -> object:
    nodes = ["hub", *[f"s{i}" for i in range(spokes)]]
    edges = [("hub", f"s{i}") for i in range(spokes)]
    return loader.build_graph(graph_factory.graph_dict(nodes=nodes, edges=edges))


def test_degree_counts_incident_edges() -> None:
    assert metrics.degree(_star(3))["hub"] == 3


def test_isolated_node_has_degree_zero() -> None:
    graph = loader.build_graph(graph_factory.graph_dict(nodes=["lonely"]))
    assert metrics.degree(graph)["lonely"] == 0


def test_betweenness_finds_the_bridge() -> None:
    nodes = ["a", "bridge", "b"]
    graph = loader.build_graph(
        graph_factory.graph_dict(nodes=nodes, edges=[("a", "bridge"), ("bridge", "b")])
    )
    scores = metrics.betweenness(graph)
    assert scores["bridge"] > scores["a"]


def test_betweenness_of_an_empty_graph_is_empty() -> None:
    assert metrics.betweenness(loader.build_graph(graph_factory.graph_dict())) == {}


def test_small_graphs_are_computed_exactly() -> None:
    graph = _star(5)
    assert metrics.betweenness(graph, exact_max_nodes=100) == metrics.betweenness(graph)


def test_large_graphs_switch_to_sampling_and_stay_deterministic() -> None:
    """Above the threshold we sample — but a fixed seed keeps runs reproducible."""
    graph = _star(40)
    first = metrics.betweenness(graph, exact_max_nodes=10, sample_k=5)
    second = metrics.betweenness(graph, exact_max_nodes=10, sample_k=5)
    assert first == second
    assert set(first) == set(graph.nodes)


def test_sample_size_is_clamped_to_the_node_count() -> None:
    """Asking for more samples than nodes must not raise."""
    assert metrics.betweenness(_star(3), exact_max_nodes=1, sample_k=999) != {}
