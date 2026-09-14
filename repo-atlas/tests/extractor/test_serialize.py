"""``graph.json`` envelope assembly (PHASE1-021, ``docs/EXTRACTOR_SPEC.md`` §9)."""

from __future__ import annotations

import json

import pytest

from repo_atlas import __version__
from repo_atlas.extractor import serialize
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


def _edge(source: str, target: str, confidence: str = "EXTRACTED") -> RawEdge:
    return RawEdge(
        source=source,
        target=target,
        relation="calls",
        confidence=confidence,
        confidence_score=1.0,
        source_file=f"{source}.py",
        source_location="L1",
    )


def _build(nodes=None, edges=None, community_of=None, **kwargs):
    nodes = nodes if nodes is not None else [_node("b"), _node("a")]
    edges = edges if edges is not None else [_edge("a", "b")]
    community_of = community_of if community_of is not None else {"a": 0, "b": 0}
    kwargs.setdefault("repo_name", "demo")
    kwargs.setdefault("generated_at", "2026-01-01T00:00:00Z")
    return serialize.build_graph(nodes, edges, community_of, **kwargs)


def test_envelope_shape() -> None:
    data = _build()
    assert data["directed"] is False
    assert data["multigraph"] is False
    assert isinstance(data["graph"], dict)
    assert isinstance(data["nodes"], list)
    assert isinstance(data["links"], list)


def test_nodes_carry_community_alongside_the_raw_node_fields() -> None:
    data = _build(community_of={"a": 0, "b": 1})
    by_id = {n["id"]: n for n in data["nodes"]}
    assert by_id["a"]["community"] == 0
    assert by_id["b"]["community"] == 1
    assert by_id["a"]["label"] == "a"


def test_graph_metadata_carries_tool_version_repo_and_counts() -> None:
    data = _build()
    meta = data["graph"]
    assert meta["tool_version"] == __version__
    assert meta["repo_name"] == "demo"
    assert meta["generated_at"] == "2026-01-01T00:00:00Z"
    assert meta["node_count"] == 2
    assert meta["edge_count"] == 1


def test_nodes_are_ordered_by_id() -> None:
    data = _build(
        nodes=[_node("c"), _node("a"), _node("b")], edges=[], community_of={"a": 0, "b": 0, "c": 0}
    )
    assert [n["id"] for n in data["nodes"]] == ["a", "b", "c"]


def test_links_are_ordered_by_relation_source_target() -> None:
    nodes = [_node(n) for n in ("a", "b", "c")]
    edges = [
        _edge("b", "c"),
        _edge("a", "b"),
        RawEdge(
            source="a",
            target="c",
            relation="method",
            confidence="EXTRACTED",
            confidence_score=1.0,
            source_file="a.py",
            source_location="L1",
        ),
    ]
    community_of = {"a": 0, "b": 0, "c": 0}
    data = _build(nodes=nodes, edges=edges, community_of=community_of)
    pairs = [(link["relation"], link["source"], link["target"]) for link in data["links"]]
    assert pairs == [("calls", "a", "b"), ("calls", "b", "c"), ("method", "a", "c")]


def test_output_is_byte_stable_for_unchanged_input() -> None:
    first = json.dumps(_build())
    second = json.dumps(_build())
    assert first == second


def test_raises_on_duplicate_node_id() -> None:
    with pytest.raises(ValueError, match="a"):
        _build(nodes=[_node("a"), _node("a")], edges=[], community_of={"a": 0})


def test_raises_on_edge_endpoint_missing_from_node_set() -> None:
    with pytest.raises(ValueError, match="ghost"):
        _build(edges=[_edge("a", "ghost")])


def test_raises_on_invalid_confidence() -> None:
    with pytest.raises(ValueError, match="bogus"):
        _build(edges=[_edge("a", "b", confidence="bogus")])


def test_raises_on_node_missing_a_community() -> None:
    with pytest.raises(ValueError, match="b"):
        _build(community_of={"a": 0})


def test_write_graph_creates_parent_dirs_and_trailing_newline(tmp_path) -> None:
    target = tmp_path / "nested" / "dir" / "graph.json"
    data = _build()
    serialize.write_graph(target, data)
    text = target.read_text(encoding="utf-8")
    assert text.endswith("\n")
    assert json.loads(text) == data


def test_write_graph_is_utf8(tmp_path) -> None:
    target = tmp_path / "graph.json"
    serialize.write_graph(target, _build(repo_name="ünïcödé"))
    assert "ünïcödé" in target.read_text(encoding="utf-8")
