"""Greedy-modularity community labels (PHASE1-019, ``docs/EXTRACTOR_SPEC.md`` §9)."""

from __future__ import annotations

from repo_atlas.extractor import communities
from repo_atlas.extractor.models import RawEdge, RawNode


def _node(node_id: str) -> RawNode:
    return RawNode(
        id=node_id,
        label=node_id,
        norm_label=node_id,
        file_type="code",
        source_file=f"{node_id}.py",
        source_location="L1",
        origin="ast",
    )


def _edge(source: str, target: str) -> RawEdge:
    return RawEdge(
        source=source,
        target=target,
        relation="calls",
        confidence="EXTRACTED",
        confidence_score=1.0,
        source_file=f"{source}.py",
        source_location="L1",
    )


def test_every_node_gets_a_community() -> None:
    nodes = [_node("a"), _node("b"), _node("c")]
    edges = [_edge("a", "b")]
    result = communities.assign_communities(nodes, edges)
    assert set(result) == {"a", "b", "c"}
    assert all(isinstance(value, int) for value in result.values())


def test_empty_graph_yields_an_empty_mapping() -> None:
    assert communities.assign_communities([], []) == {}


def test_zero_edge_graph_gives_every_isolated_node_its_own_community() -> None:
    nodes = [_node("a"), _node("b"), _node("c")]
    result = communities.assign_communities(nodes, [])
    assert set(result) == {"a", "b", "c"}
    assert len(set(result.values())) == 3


def test_isolated_nodes_alongside_a_connected_cluster() -> None:
    nodes = [_node(n) for n in ("a", "b", "c", "lonely")]
    edges = [_edge("a", "b"), _edge("b", "c")]
    result = communities.assign_communities(nodes, edges)
    assert result["a"] == result["b"] == result["c"]
    assert result["lonely"] != result["a"]


def test_numbering_is_deterministic_across_builds_of_the_same_graph() -> None:
    nodes = [_node(n) for n in ("a", "b", "c", "d", "e")]
    edges = [_edge("a", "b"), _edge("b", "c"), _edge("d", "e")]
    first = communities.assign_communities(nodes, edges)
    second = communities.assign_communities(list(nodes), list(edges))
    assert first == second


def test_larger_community_gets_the_lower_number() -> None:
    nodes = [_node(n) for n in ("a", "b", "c", "d", "e")]
    edges = [_edge("a", "b"), _edge("b", "c"), _edge("d", "e")]
    result = communities.assign_communities(nodes, edges)
    assert result["a"] == result["b"] == result["c"] == 0
    assert result["d"] == result["e"] == 1
