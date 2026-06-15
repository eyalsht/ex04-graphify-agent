"""Metric tests (GR-T2, GR-T3): degree, betweenness, top-N ranking."""

from __future__ import annotations

from pathlib import Path

import pytest

from ex04_graphify_agent.graph_reader import GraphReader


def test_gr_t2_degree_god_node(graph_json_path: Path) -> None:
    reader = GraphReader(str(graph_json_path))
    assert reader.degree("polygons_polygons_polygon") == 4


def test_rationale_nodes_have_degree_one(graph_json_path: Path) -> None:
    reader = GraphReader(str(graph_json_path))
    for suffix in (18, 33, 50):
        assert reader.degree(f"polygons_polygons_rationale_{suffix}") == 1


def test_betweenness_god_node(graph_json_path: Path) -> None:
    reader = GraphReader(str(graph_json_path))
    bw = reader.betweenness("polygons_polygons_polygon")
    assert bw == pytest.approx(0.0563, abs=0.001)


def test_file_root_nodes_are_flagged(graph_json_path: Path) -> None:
    # polygons.py is a container (source of `contains` edges) — excluded from God-Node rank.
    reader = GraphReader(str(graph_json_path))
    assert reader.node("polygons_polygons").is_file_root is True
    assert reader.node("polygons_polygons_polygon").is_file_root is False


def test_node_view_carries_metrics(graph_json_path: Path) -> None:
    reader = GraphReader(str(graph_json_path))
    node = reader.node("polygons_polygons_polygon")
    assert node.degree == 4
    assert node.betweenness == pytest.approx(0.0563, abs=0.001)


def test_gr_t3_top_n_by_degree(graph_json_path: Path) -> None:
    # God-Node ranking excludes file-container roots (GRAPH_REPORT "most connected"):
    # Polygon (degree 4) is #1, not the polygons.py file node (degree 6).
    reader = GraphReader(str(graph_json_path))
    top = reader.top_n_by_degree(1)
    assert len(top) == 1
    assert top[0].id == "polygons_polygons_polygon"
    assert top[0].label == "Polygon"


def test_top_n_by_degree_excludes_file_roots(graph_json_path: Path) -> None:
    reader = GraphReader(str(graph_json_path))
    top_ids = {n.id for n in reader.top_n_by_degree(1000)}
    assert "polygons_polygons" not in top_ids  # file root excluded
    assert "polygons_polygons_polygon" in top_ids


def test_top_n_by_degree_tie_break(graph_json_path: Path) -> None:
    # Tie-break is betweenness DESC then id ASC — deterministic ordering.
    reader = GraphReader(str(graph_json_path))
    top = reader.top_n_by_degree(5)
    assert top[0].id == "polygons_polygons_polygon"
    ids = [n.id for n in top]
    assert len(ids) == len(set(ids))


def test_top_n_by_betweenness(graph_json_path: Path) -> None:
    reader = GraphReader(str(graph_json_path))
    top = reader.top_n_by_betweenness(1)
    assert top[0].id == "polygons_polygons_polygon"


def test_top_n_larger_than_node_count_returns_all_entities(graph_json_path: Path) -> None:
    # 23 nodes minus the 3 file-container roots = 20 ranked entities; no padding.
    reader = GraphReader(str(graph_json_path))
    top = reader.top_n_by_degree(1000)
    assert len(top) == 20


def test_top_n_is_deterministic(graph_json_path: Path) -> None:
    reader = GraphReader(str(graph_json_path))
    first = [n.id for n in reader.top_n_by_degree(10)]
    second = [n.id for n in reader.top_n_by_degree(10)]
    assert first == second
