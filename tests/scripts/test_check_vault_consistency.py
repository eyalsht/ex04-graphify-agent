"""Tests for scripts/check_vault_consistency.py (Phase 4 vault wikilink consistency)."""

from __future__ import annotations

from pathlib import Path

import check_vault_consistency


def _vault(tmp_path: Path) -> Path:
    vault = tmp_path / "obsidian"
    vault.mkdir()
    return vault


def test_resolves_existing_wikilink(tmp_path: Path) -> None:
    vault = _vault(tmp_path)
    (vault / "index.md").write_text("- [[polygons_polygons_polygon|Polygon]]\n", encoding="utf-8")
    (vault / "polygons_polygons_polygon.md").write_text("# Polygon\n", encoding="utf-8")

    assert check_vault_consistency.find_dangling_links(vault) == []
    assert check_vault_consistency.main([str(vault)]) == 0


def test_flags_dangling_wikilink(tmp_path: Path) -> None:
    vault = _vault(tmp_path)
    (vault / "hot.md").write_text("1. [[does_not_exist|Ghost]] — degree=1\n", encoding="utf-8")

    dangling = check_vault_consistency.find_dangling_links(vault)
    assert ("hot.md", "does_not_exist") in dangling
    assert check_vault_consistency.main([str(vault)]) == 1


def test_link_without_label_resolves(tmp_path: Path) -> None:
    vault = _vault(tmp_path)
    (vault / "index.md").write_text("- [[community-0]]\n", encoding="utf-8")
    (vault / "community-0.md").write_text("# Community 0\n", encoding="utf-8")

    assert check_vault_consistency.find_dangling_links(vault) == []


def test_real_vault_index_and_hot_are_consistent(obsidian_dir: Path) -> None:
    dangling = check_vault_consistency.find_dangling_links(obsidian_dir)
    assert dangling == []


def test_only_scans_index_and_hot(tmp_path: Path) -> None:
    vault = _vault(tmp_path)
    # A dangling link inside a per-node note must NOT be flagged (out of scope).
    (vault / "polygons_polygons_polygon.md").write_text("- [[nope|Nope]]\n", encoding="utf-8")
    (vault / "index.md").write_text("# Graph Index\n", encoding="utf-8")

    assert check_vault_consistency.find_dangling_links(vault) == []
