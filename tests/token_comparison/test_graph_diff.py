"""TDD for diff_graphs (PHASE6-048..057, TC-T7/E3, R5.6.3)."""

from __future__ import annotations

from pathlib import Path

import pytest

from ex04_graphify_agent.gatekeeper.config import repo_root
from ex04_graphify_agent.token_comparison.graph_diff import diff_graphs

_FIXTURES = Path(__file__).resolve().parent / "fixtures"
_PRE = repo_root() / "artifacts" / "graphify" / "graph.json"
_POST_FIXTURE = _FIXTURES / "post_fix_graph.json"


def test_diff_graphs_reports_node_count_change() -> None:
    """TC-T7: nodes: 23 -> 20."""
    diff = diff_graphs(_PRE, _POST_FIXTURE)
    assert diff.pre_node_count == 23
    assert diff.post_node_count == 20
    assert diff.node_count_change == "23 -> 20"


def test_diff_graphs_lists_removed_rationale_nodes() -> None:
    """TC-T7: lists polygons_polygons_rationale_{18,33,50} as removed."""
    diff = diff_graphs(_PRE, _POST_FIXTURE)
    assert set(diff.removed_nodes) == {
        "polygons_polygons_rationale_18",
        "polygons_polygons_rationale_33",
        "polygons_polygons_rationale_50",
    }


def test_diff_graphs_edge_count_change() -> None:
    diff = diff_graphs(_PRE, _POST_FIXTURE)
    assert diff.pre_edge_count == 20
    assert diff.post_edge_count == 17


def test_diff_graphs_polygon_usage_edge_note() -> None:
    """PHASE6-056/057: Polygon now has a usage edge (used, not dead) prediction."""
    diff = diff_graphs(_PRE, _POST_FIXTURE)
    assert "polygons_polygons_polygon" in diff.usage_edge_note
    assert "calls" in diff.usage_edge_note


def test_diff_graphs_polygon_usage_edge_absent_note() -> None:
    """If POST-FIX has no calls->Polygon edge, the note says so (not fabricated)."""
    post_no_usage = _FIXTURES / "post_fix_graph_no_usage.json"
    diff = diff_graphs(_PRE, post_no_usage)
    assert "no 'calls' usage edge found" in diff.usage_edge_note


def test_diff_graphs_missing_post_fix_fails_loud() -> None:
    """TC-E3: missing artifacts/graphify_post_fix/graph.json -> fail loud, never fabricate."""
    missing = _FIXTURES / "does_not_exist.json"
    with pytest.raises(FileNotFoundError, match="pending re-run"):
        diff_graphs(_PRE, missing)


def test_render_graph_diff_section() -> None:
    from ex04_graphify_agent.token_comparison.graph_diff import render_graph_diff

    diff = diff_graphs(_PRE, _POST_FIXTURE)
    section = render_graph_diff(diff)
    assert "23 -> 20" in section
    assert "polygons_polygons_rationale_18" in section


def test_render_graph_diff_section_pending_when_absent() -> None:
    from ex04_graphify_agent.token_comparison.graph_diff import render_graph_diff_pending

    section = render_graph_diff_pending()
    assert "pending re-run" in section.lower()
