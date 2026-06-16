"""TDD for TokenComparison.diff_graphs convenience wiring (PHASE6-054, R5.6.3)."""

from __future__ import annotations

from pathlib import Path

from ex04_graphify_agent.token_comparison.runner import TokenComparison


def test_diff_graphs_section_pending_when_post_fix_absent() -> None:
    """TC-E3: the real artifacts/graphify_post_fix/graph.json does not exist yet."""
    tc = TokenComparison()
    section = tc.graph_diff_section()
    assert "pending re-run" in section.lower()


def test_diff_graphs_section_with_explicit_post_fixture() -> None:
    fixtures = Path(__file__).resolve().parent / "fixtures"
    tc = TokenComparison()
    section = tc.graph_diff_section(post_fix_path=fixtures / "post_fix_graph.json")
    assert "23 -> 20" in section
    assert "polygons_polygons_rationale_18" in section
