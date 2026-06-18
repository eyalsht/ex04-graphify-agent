"""Vault rendering: per-node notes + index + scratch regen + hot.md golden snapshot.

Covers PHASE2-114..117, PHASE4-020, PHASE4-036. Keyless; writes only to tmp/scratch dirs
so the committed PRE-FIX vault (CLAUDE.md §4) is never touched.
"""

from __future__ import annotations

from pathlib import Path

from ex04_graphify_agent.graph_reader import GraphReader
from ex04_graphify_agent.obsidian_writer import ObsidianWriter

_GOLDEN = Path(__file__).parent / "golden_hot.md"


def _writer(graph_json_path: Path) -> ObsidianWriter:
    return ObsidianWriter(GraphReader(str(graph_json_path)))


def test_render_node_note_has_wikilinks_and_relations(graph_json_path: Path) -> None:
    note = _writer(graph_json_path).render_node_note(
        GraphReader(str(graph_json_path)).node("polygons_polygons_polygon")
    )
    assert "# Polygon" in note
    assert "[[object|Object]]" in note  # outgoing inherits edge
    assert "Outgoing relations" in note
    assert "Community: [[community-4|Community 4]]" in note


def test_render_node_note_handles_null_source_location(graph_json_path: Path) -> None:
    note = _writer(graph_json_path).render_node_note(
        GraphReader(str(graph_json_path)).node("license_mit_license")
    )
    assert "source_location: null" in note
    assert ":None" not in note


def test_render_index_lists_six_communities_and_all_nodes(graph_json_path: Path) -> None:
    rendered = _writer(graph_json_path).render_index()
    for community in range(6):
        assert f"[[community-{community}|Community {community}]]" in rendered
    assert rendered.count("\n- [[") >= 23  # every node + 6 communities as wikilinks


def test_regenerate_vault_matches_baseline_structure(graph_json_path: Path, tmp_path: Path) -> None:
    writer = _writer(graph_json_path)
    scratch = writer.regenerate_vault(tmp_path / "scratch")
    assert (scratch / "index.md").is_file()
    node_ids = {n.id for n in GraphReader(str(graph_json_path)).all_nodes()}
    note_files = {p.stem for p in scratch.glob("*.md")} - {"index"}
    assert note_files == node_ids  # one note per node, no overwrite of baseline


def test_hot_md_matches_committed_golden(graph_json_path: Path) -> None:
    rendered = _writer(graph_json_path).render_hot_md()
    assert rendered == _GOLDEN.read_text(encoding="utf-8")
