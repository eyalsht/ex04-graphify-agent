"""Loader + model tests (GR-T1). Keyless; uses the real PRE-FIX graph fixture."""

from __future__ import annotations

from pathlib import Path

import pytest

from ex04_graphify_agent.graph_reader import (
    Confidence,
    EdgeView,
    GraphReader,
    NodeView,
)


def test_gr_t1_load_node_and_edge_counts(graph_json_path: Path) -> None:
    reader = GraphReader(str(graph_json_path))
    assert len(reader.all_nodes()) == 23
    assert len(reader.all_edges()) == 20


def test_node_view_is_typed(graph_json_path: Path) -> None:
    reader = GraphReader(str(graph_json_path))
    node = reader.node("polygons_polygons_polygon")
    assert isinstance(node, NodeView)
    assert node.id == "polygons_polygons_polygon"
    assert node.label == "Polygon"
    assert node.file_type == "code"
    assert node.source_file == "polygons/polygons.py"
    assert node.source_location == "L3"
    assert node.community == 4


def test_document_node_has_null_source_location(graph_json_path: Path) -> None:
    reader = GraphReader(str(graph_json_path))
    node = reader.node("license_mit_license")
    assert node.source_location is None
    assert node.file_type == "document"


def test_object_node_has_empty_source_file(graph_json_path: Path) -> None:
    reader = GraphReader(str(graph_json_path))
    node = reader.node("object")
    assert node.source_file == ""


def test_edge_view_is_typed(graph_json_path: Path) -> None:
    reader = GraphReader(str(graph_json_path))
    edges = reader.edges_of("polygons_polygons_rationale_18")
    assert len(edges) == 1
    edge = edges[0]
    assert isinstance(edge, EdgeView)
    assert edge.relation == "rationale_for"
    assert edge.confidence is Confidence.EXTRACTED
    assert edge.confidence_score == 1.0
    assert edge.weight == 1.0


def test_node_exists_probe(graph_json_path: Path) -> None:
    reader = GraphReader(str(graph_json_path))
    assert reader.node_exists("polygons_polygons_polygon") is True
    assert reader.node_exists("nope_missing") is False


def test_missing_node_raises_keyerror(graph_json_path: Path) -> None:
    reader = GraphReader(str(graph_json_path))
    with pytest.raises(KeyError):
        reader.node("nope_missing")
    with pytest.raises(KeyError):
        reader.degree("nope_missing")


def test_default_path_is_config_driven(graph_json_path: Path) -> None:
    # No path argument => resolved from config/paths.json, not a literal.
    reader = GraphReader()
    assert len(reader.all_nodes()) == 23
