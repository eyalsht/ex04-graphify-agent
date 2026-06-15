"""Filter tests (GR-T4..GR-T7): community grouping + confidence filtering."""

from __future__ import annotations

from pathlib import Path

from ex04_graphify_agent.graph_reader import Confidence, GraphReader


def test_gr_t4_community_grouping(graph_json_path: Path) -> None:
    reader = GraphReader(str(graph_json_path))
    ids = {n.id for n in reader.nodes_in_community(1)}
    assert ids == {
        "polygons_polygons",
        "polygons_polygons_draw_polygon",
        "polygons_polygons_rationale_18",
        "polygons_polygons_rationale_33",
        "polygons_polygons_rationale_50",
    }


def test_communities_cover_six_buckets(graph_json_path: Path) -> None:
    reader = GraphReader(str(graph_json_path))
    buckets = reader.communities()
    assert set(buckets) == {0, 1, 2, 3, 4, 5}
    total = sum(len(v) for v in buckets.values())
    assert total == 23


def test_gr_t5_inferred_edges(graph_json_path: Path) -> None:
    reader = GraphReader(str(graph_json_path))
    inferred = reader.edges_with_confidence("INFERRED")
    assert len(inferred) == 2
    # Undirected edges — compare endpoint pairs orientation-agnostically.
    pairs = {(frozenset((e.source, e.target)), e.confidence_score) for e in inferred}
    assert (
        frozenset(("mathsquiz_mathsquiz_final_py", "mathsquiz_mathsquiz")),
        0.8,
    ) in pairs
    assert (
        frozenset(("mathsquiz_readme_maths_quiz", "readme_broken_python")),
        0.9,
    ) in pairs


def test_extracted_edges_are_the_rest(graph_json_path: Path) -> None:
    reader = GraphReader(str(graph_json_path))
    extracted = reader.edges_with_confidence(Confidence.EXTRACTED)
    assert len(extracted) == 18
    assert all(e.confidence is Confidence.EXTRACTED for e in extracted)


def test_gr_t6_inferred_below_threshold(graph_json_path: Path) -> None:
    reader = GraphReader(str(graph_json_path))
    below = reader.inferred_edges_below(0.85)
    assert len(below) == 1
    assert below[0].relation == "semantically_similar_to"
    assert below[0].confidence_score == 0.8


def test_inferred_below_high_threshold_returns_both(graph_json_path: Path) -> None:
    reader = GraphReader(str(graph_json_path))
    assert len(reader.inferred_edges_below(1.0)) == 2


def test_gr_t7_ambiguous_is_empty(graph_json_path: Path) -> None:
    reader = GraphReader(str(graph_json_path))
    assert reader.edges_with_confidence("AMBIGUOUS") == []
    assert reader.edges_with_confidence(Confidence.AMBIGUOUS) == []


def test_edges_of_god_node(graph_json_path: Path) -> None:
    reader = GraphReader(str(graph_json_path))
    edges = reader.edges_of("polygons_polygons_polygon")
    assert len(edges) == 4
    neighbors = {e.target for e in edges} | {e.source for e in edges}
    assert "polygons_polygons_polygon" in neighbors
