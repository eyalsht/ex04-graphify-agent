"""GraphReader query surface (PRD R2.1-R2.4)."""

from __future__ import annotations

from pathlib import Path

import pytest

from repo_atlas.graph_reader import Confidence, GraphReader
from tests.fixtures import graph_factory


def _reader(tmp_path: Path) -> GraphReader:
    nodes = [
        graph_factory.make_node("mod", file_type="code", community=0),
        graph_factory.make_node("mod_hub", community=0),
        graph_factory.make_node("mod_leaf", community=1),
        graph_factory.make_node("orphan", community=2),
    ]
    edges = [
        graph_factory.make_edge("mod", "mod_hub", relation="contains"),
        graph_factory.make_edge("mod", "mod_leaf", relation="contains"),
        graph_factory.make_edge("mod_hub", "mod_leaf", relation="calls"),
        graph_factory.make_edge(
            "mod_hub", "orphan", relation="inherits", confidence="INFERRED", confidence_score=0.7
        ),
    ]
    path = graph_factory.write_graph(tmp_path, graph_factory.graph_dict(nodes, edges))
    return GraphReader(path)


def test_node_lookup_returns_a_typed_view(tmp_path: Path) -> None:
    node = _reader(tmp_path).node("mod_hub")
    assert (node.id, node.community, node.degree) == ("mod_hub", 0, 3)


def test_node_exists_is_cheap_and_correct(tmp_path: Path) -> None:
    reader = _reader(tmp_path)
    assert reader.node_exists("mod") is True
    assert reader.node_exists("nope") is False


def test_unknown_node_raises(tmp_path: Path) -> None:
    with pytest.raises(KeyError):
        _reader(tmp_path).node("nope")


def test_file_roots_are_flagged_by_their_contains_edges(tmp_path: Path) -> None:
    reader = _reader(tmp_path)
    assert reader.node("mod").is_file_root is True
    assert reader.node("mod_hub").is_file_root is False


def test_top_n_by_degree_excludes_file_roots(tmp_path: Path) -> None:
    """A file node outranks its own contents on degree, which is never interesting."""
    top = _reader(tmp_path).top_n_by_degree(2)
    assert [n.id for n in top] == ["mod_hub", "mod_leaf"]


def test_communities_group_every_node(tmp_path: Path) -> None:
    communities = _reader(tmp_path).communities()
    assert sorted(communities) == [0, 1, 2]
    assert {n.id for n in communities[0]} == {"mod", "mod_hub"}


def test_edges_of_returns_incident_edges(tmp_path: Path) -> None:
    assert len(_reader(tmp_path).edges_of("mod_hub")) == 3


def test_edges_of_an_unknown_node_raises(tmp_path: Path) -> None:
    with pytest.raises(KeyError):
        _reader(tmp_path).edges_of("nope")


def test_edges_can_be_filtered_by_confidence(tmp_path: Path) -> None:
    reader = _reader(tmp_path)
    assert len(reader.edges_with_confidence(Confidence.INFERRED)) == 1
    assert len(reader.edges_with_confidence("EXTRACTED")) == 3


def test_inferred_edges_below_a_threshold(tmp_path: Path) -> None:
    reader = _reader(tmp_path)
    assert len(reader.inferred_edges_below(0.8)) == 1
    assert reader.inferred_edges_below(0.5) == []


def test_an_unknown_confidence_degrades_to_ambiguous(tmp_path: Path) -> None:
    """A third-party graph must not crash the reader (PRD R2.3)."""
    nodes = ["a", "b"]
    edges = [graph_factory.make_edge("a", "b", confidence="HIGH")]
    path = graph_factory.write_graph(
        tmp_path, graph_factory.graph_dict(nodes, edges), filename="odd.json"
    )
    with pytest.warns(UserWarning, match="unknown confidence"):
        reader = GraphReader(path)
    assert reader.all_edges()[0].confidence is Confidence.AMBIGUOUS


def test_confidence_parsing_is_case_insensitive(tmp_path: Path) -> None:
    edges = [graph_factory.make_edge("a", "b", confidence="extracted")]
    path = graph_factory.write_graph(
        tmp_path, graph_factory.graph_dict(["a", "b"], edges), filename="lower.json"
    )
    assert GraphReader(path).all_edges()[0].confidence is Confidence.EXTRACTED


def test_a_missing_community_defaults_rather_than_crashing(tmp_path: Path) -> None:
    node = graph_factory.make_node("x")
    del node["community"]
    path = graph_factory.write_graph(
        tmp_path, graph_factory.graph_dict([node]), filename="nocom.json"
    )
    assert GraphReader(path).node("x").community == -1


def test_top_n_by_betweenness_ranks_bridges(tmp_path: Path) -> None:
    top = _reader(tmp_path).top_n_by_betweenness(1)
    assert top[0].id == "mod_hub"


def test_nodes_in_community_selects_one_bucket(tmp_path: Path) -> None:
    assert [n.id for n in _reader(tmp_path).nodes_in_community(1)] == ["mod_leaf"]
