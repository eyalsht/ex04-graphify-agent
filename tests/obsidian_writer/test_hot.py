"""ObsidianWriter.hot tests (OW-T1..5). Keyless; uses the real PRE-FIX graph fixture."""

from __future__ import annotations

from pathlib import Path

from ex04_graphify_agent.graph_reader import GraphReader
from ex04_graphify_agent.obsidian_writer import ObsidianWriter


def _writer(graph_json_path: Path, vault_dir: Path) -> ObsidianWriter:
    reader = GraphReader(str(graph_json_path))
    return ObsidianWriter(reader, vault_dir=vault_dir)


def test_ow_t1_rank_hot_nodes_polygon_first(graph_json_path: Path, tmp_path: Path) -> None:
    writer = _writer(graph_json_path, tmp_path)
    ranked = writer.rank_hot_nodes(5)
    assert ranked[0].id == "polygons_polygons_polygon"
    assert ranked[0].label == "Polygon"
    assert ranked[0].degree == 4


def test_rank_hot_nodes_truncates_to_top_k(graph_json_path: Path, tmp_path: Path) -> None:
    writer = _writer(graph_json_path, tmp_path)
    assert len(writer.rank_hot_nodes(5)) == 5
    assert len(writer.rank_hot_nodes(3)) == 3


def test_rank_hot_nodes_deterministic_tie_break(graph_json_path: Path, tmp_path: Path) -> None:
    writer = _writer(graph_json_path, tmp_path)
    ranked = writer.rank_hot_nodes(8)
    # degree DESC, betweenness DESC, id ASC -- never crash, always sorted.
    keys = [(-n.degree, -n.betweenness, n.id) for n in ranked]
    assert keys == sorted(keys)


def test_ow_t2_wikilink_format(graph_json_path: Path, tmp_path: Path) -> None:
    writer = _writer(graph_json_path, tmp_path)
    polygon = writer.rank_hot_nodes(1)[0]
    assert writer.wikilink(polygon) == "[[polygons_polygons_polygon|Polygon]]"


def test_ow_t3_render_hot_md_has_heading_links_and_metric(
    graph_json_path: Path, tmp_path: Path
) -> None:
    writer = _writer(graph_json_path, tmp_path)
    md = writer.render_hot_md(5)
    assert md.startswith("# Hot — Where to look first")
    assert "[[polygons_polygons_polygon|Polygon]]" in md
    assert "degree DESC" in md
    assert "betweenness DESC" in md


def test_render_hot_md_item_metadata(graph_json_path: Path, tmp_path: Path) -> None:
    writer = _writer(graph_json_path, tmp_path)
    md = writer.render_hot_md(5)
    assert "degree=4" in md
    assert "bw=" in md
    assert "community=4" in md
    assert "polygons/polygons.py:L3" in md


def test_render_hot_md_null_source_location_renders_gracefully(
    graph_json_path: Path, tmp_path: Path
) -> None:
    writer = _writer(graph_json_path, tmp_path)
    # top_k large enough to include a document node with source_location == None
    md = writer.render_hot_md(8)
    assert ":None" not in md
    assert "None" not in md


def test_ow_t4_write_hot_md_creates_file_and_is_deterministic(
    graph_json_path: Path, tmp_path: Path
) -> None:
    writer = _writer(graph_json_path, tmp_path)
    path1 = writer.write_hot_md(5)
    assert path1.exists()
    assert path1.name == "hot.md"
    content1 = path1.read_bytes()

    path2 = writer.write_hot_md(5)
    content2 = path2.read_bytes()
    assert content1 == content2


def test_ow_t5_write_hot_md_leaves_baselines_untouched(
    graph_json_path: Path, obsidian_dir: Path, tmp_path: Path
) -> None:
    # Write into a copy of the real vault dir so we can assert baseline files untouched.
    import shutil

    vault_copy = tmp_path / "vault"
    shutil.copytree(obsidian_dir, vault_copy)

    index_path = vault_copy / "index.md"
    polygon_path = vault_copy / "polygons_polygons_polygon.md"
    index_before = index_path.read_bytes()
    polygon_before = polygon_path.read_bytes()
    index_mtime_before = index_path.stat().st_mtime_ns
    polygon_mtime_before = polygon_path.stat().st_mtime_ns

    writer = _writer(graph_json_path, vault_copy)
    writer.write_hot_md(5)

    assert index_path.read_bytes() == index_before
    assert polygon_path.read_bytes() == polygon_before
    assert index_path.stat().st_mtime_ns == index_mtime_before
    assert polygon_path.stat().st_mtime_ns == polygon_mtime_before


def test_hot_md_distinct_from_index(
    graph_json_path: Path, obsidian_dir: Path, tmp_path: Path
) -> None:
    writer = _writer(graph_json_path, tmp_path)
    hot_md = writer.render_hot_md(5)
    index_md = (obsidian_dir / "index.md").read_text(encoding="utf-8")
    assert hot_md != index_md


def test_default_vault_dir_is_config_driven(graph_json_path: Path) -> None:
    reader = GraphReader(str(graph_json_path))
    writer = ObsidianWriter(reader)
    assert writer.vault_dir.name == "obsidian"


def test_render_hot_md_default_top_k_is_config_driven(
    graph_json_path: Path, tmp_path: Path
) -> None:
    writer = _writer(graph_json_path, tmp_path)
    md_default = writer.render_hot_md()
    md_explicit = writer.render_hot_md(8)
    assert md_default == md_explicit


def test_write_hot_md_default_top_k(graph_json_path: Path, tmp_path: Path) -> None:
    writer = _writer(graph_json_path, tmp_path)
    path = writer.write_hot_md()
    assert path.read_text(encoding="utf-8") == writer.render_hot_md(8)
