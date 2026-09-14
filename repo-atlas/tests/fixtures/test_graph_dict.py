"""``graph_dict``/``write_graph`` tests for ``tests/fixtures/graph_factory.py`` (PHASE1-001)."""

from __future__ import annotations

import json
from pathlib import Path

import networkx as nx
import pytest

from tests.fixtures.graph_factory import graph_dict, make_edge, make_node, write_graph


def test_envelope_has_the_plan_7_1_shape() -> None:
    data = graph_dict()
    assert data["directed"] is False
    assert data["multigraph"] is False
    assert data["graph"] == {}
    assert data["nodes"] == []
    assert data["links"] == []


def test_bare_ids_and_tuples_are_the_one_line_common_case() -> None:
    data = graph_dict(nodes=["a", "b", "c"], edges=[("a", "b"), ("b", "c")])
    assert [n["id"] for n in data["nodes"]] == ["a", "b", "c"]
    assert [(e["source"], e["target"]) for e in data["links"]] == [("a", "b"), ("b", "c")]


def test_mixed_bare_and_overridden_nodes() -> None:
    data = graph_dict(nodes=["a", make_node("b", community=2), "c"])
    by_id = {n["id"]: n for n in data["nodes"]}
    assert by_id["a"]["community"] == 0
    assert by_id["b"]["community"] == 2
    assert by_id["c"]["community"] == 0


def test_full_edge_dict_overrides_are_kept() -> None:
    edge = make_edge("a", "b", confidence="INFERRED", confidence_score=0.6)
    data = graph_dict(nodes=["a", "b"], edges=[edge])
    assert data["links"][0]["confidence"] == "INFERRED"
    assert data["links"][0]["confidence_score"] == 0.6


def test_duplicate_node_id_raises() -> None:
    with pytest.raises(ValueError, match="duplicate node id"):
        graph_dict(nodes=["a", "a"])


def test_edge_endpoint_must_be_a_known_node() -> None:
    with pytest.raises(ValueError, match="not a known node id"):
        graph_dict(nodes=["a"], edges=[("a", "ghost")])


def test_hub_node_reaches_the_requested_degree() -> None:
    leaves = ["l1", "l2", "l3", "l4", "l5"]
    data = graph_dict(nodes=["hub", *leaves], edges=[("hub", leaf) for leaf in leaves])
    degree = sum(1 for e in data["links"] if e["source"] == "hub" or e["target"] == "hub")
    assert degree == 5


def test_graph_meta_is_copied_not_aliased() -> None:
    meta = {"note": "seed"}
    data = graph_dict(graph_meta=meta)
    data["graph"]["note"] = "mutated"
    assert meta["note"] == "seed"


def test_networkx_can_load_the_envelope() -> None:
    """Matches the exact consumption contract from ``docs/PLAN.md`` §7.1."""
    data = graph_dict(nodes=["a", "b"], edges=[("a", "b")])
    graph = nx.node_link_graph(data, edges="links")
    assert set(graph.nodes) == {"a", "b"}
    assert graph.has_edge("a", "b")


def test_write_graph_round_trips_through_json(tmp_path: Path) -> None:
    data = graph_dict(nodes=["a", "b"], edges=[("a", "b")])
    path = write_graph(tmp_path, data)
    assert path == tmp_path / "graph.json"
    assert json.loads(path.read_text(encoding="utf-8")) == data


def test_write_graph_custom_filename(tmp_path: Path) -> None:
    path = write_graph(tmp_path, graph_dict(), filename="custom.json")
    assert path.name == "custom.json"
    assert path.exists()
