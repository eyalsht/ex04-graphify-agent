"""Tests for the composite hot.md ranking — centrality * proximity-to-bug (PLAN §5)."""

from __future__ import annotations

from pathlib import Path

from ex04_graphify_agent.graph_reader import GraphReader
from ex04_graphify_agent.obsidian_writer import ObsidianWriter, ranking

_BUG = "polygons_polygons_polygon"


def _reader(graph_json_path: Path) -> GraphReader:
    return GraphReader(str(graph_json_path))


def test_rank_is_deterministic_and_bug_node_leads(graph_json_path: Path, tmp_path: Path) -> None:
    writer = ObsidianWriter(_reader(graph_json_path), vault_dir=tmp_path)
    first = [n.id for n in writer.rank_hot_nodes(8)]
    second = [n.id for n in writer.rank_hot_nodes(8)]
    assert first == second  # composite ranking is deterministic
    assert first[0] == _BUG  # bug node leads (max centrality * proximity == 1.0)


def test_polygons_community_ranked_above_mathsquiz(graph_json_path: Path, tmp_path: Path) -> None:
    # Option B (R1.4 / PHASE4-030/031): the polygons subgraph is "where to look first";
    # the disconnected mathsquiz/README nodes (proximity 0) never lead, even though the
    # README has a higher raw degree than the Polygon class internals.
    writer = ObsidianWriter(_reader(graph_json_path), vault_dir=tmp_path)
    top_ids = [n.id for n in writer.rank_hot_nodes(8)]
    assert all("mathsquiz" not in nid and "readme" not in nid for nid in top_ids)
    assert "polygons_polygons_calc_polygon_details" in top_ids


def test_bfs_distance_zero_at_bug_node(graph_json_path: Path) -> None:
    distances = ranking.bfs_distances(_reader(graph_json_path), _BUG)
    assert distances[_BUG] == 0
    # A directly-related node is one hop away; an isolated/disconnected node is absent.
    assert distances["polygons_polygons_calc_polygon_details"] == 1
    assert "license_mit_license" not in distances


def test_unreachable_node_has_zero_proximity(graph_json_path: Path) -> None:
    reader = _reader(graph_json_path)
    distances = ranking.bfs_distances(reader, _BUG)
    node = reader.node("license_mit_license")  # isolated → unreachable from the bug node
    score = ranking.composite_score(node, distances, {"degree": 0.6, "betweenness": 0.4}, (4, 1.0))
    assert score == 0.0
