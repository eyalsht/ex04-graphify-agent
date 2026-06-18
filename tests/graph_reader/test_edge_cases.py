"""Edge-case coverage (PHASE2-012/013, 031-034, 055/056, 061-064, 080/081)."""

from __future__ import annotations

from pathlib import Path

import pytest

from ex04_graphify_agent.graph_reader import GraphReader


def test_missing_graph_file_raises_clear_error(tmp_path: Path) -> None:  # PHASE2-012/013
    with pytest.raises(FileNotFoundError):
        GraphReader(str(tmp_path / "nope_graph.json"))


def test_degree_of_maths_quiz_readme_is_three(graph_json_path: Path) -> None:  # PHASE2-031/032
    reader = GraphReader(str(graph_json_path))
    assert reader.degree("mathsquiz_readme_maths_quiz") == 3


def test_degree_of_calc_polygon_details_is_two(graph_json_path: Path) -> None:  # PHASE2-033/034
    reader = GraphReader(str(graph_json_path))
    assert reader.degree("polygons_polygons_calc_polygon_details") == 2


def test_isolated_license_node_is_ranked_without_crash(graph_json_path: Path) -> None:
    # PHASE2-055/056: the isolated document node is still returned deterministically.
    reader = GraphReader(str(graph_json_path))
    ranked_ids = [n.id for n in reader.top_n_by_degree(1000)]
    assert "license_mit_license" in ranked_ids
    assert ranked_ids == [n.id for n in reader.top_n_by_degree(1000)]


def test_community_four_holds_the_polygon_subgraph(graph_json_path: Path) -> None:  # PHASE2-061/062
    reader = GraphReader(str(graph_json_path))
    ids = {n.id for n in reader.nodes_in_community(4)}
    assert ids == {
        "polygons_polygons_polygon",
        "object",
        "polygons_polygons_polygon_init",
        "polygons_polygons_calc_polygon_details",
    }


def test_unknown_community_returns_empty(graph_json_path: Path) -> None:  # PHASE2-063/064
    reader = GraphReader(str(graph_json_path))
    assert reader.nodes_in_community(99) == []


def test_duplicate_labels_are_keyed_by_distinct_ids(graph_json_path: Path) -> None:  # 080/081
    reader = GraphReader(str(graph_json_path))
    welcome = [n for n in reader.all_nodes() if n.label == "welcome_message()"]
    ids = {n.id for n in welcome}
    assert ids == {
        "mathsquiz_mathsquiz_step2_welcome_message",
        "mathsquiz_mathsquiz_step3_welcome_message",
    }
    # Same label, distinct ids — node() keys by id, never label.
    assert reader.node("mathsquiz_mathsquiz_step2_welcome_message").label == "welcome_message()"
