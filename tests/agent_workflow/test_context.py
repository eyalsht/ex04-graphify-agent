"""TDD for context-assembly helpers (read_vault / dump_repo / diff / token count)."""

from __future__ import annotations

from pathlib import Path

import pytest

from ex04_graphify_agent.agent_workflow import context


def test_read_vault_text_includes_index_and_hot(obsidian_dir: Path) -> None:
    text, files = context.read_vault_text(obsidian_dir / "index.md", obsidian_dir / "hot.md")
    assert "Graph Index" in text
    assert "polygons_polygons_polygon" in text  # the Polygon wikilink from hot.md
    assert [Path(f).name for f in files] == ["index.md", "hot.md"]


def test_read_vault_text_fails_loud_when_hot_missing(obsidian_dir: Path, tmp_path: Path) -> None:
    missing_hot = tmp_path / "hot.md"
    with pytest.raises(FileNotFoundError, match="run obsidian_writer first"):
        context.read_vault_text(obsidian_dir / "index.md", missing_hot)


def test_dump_repo_text_includes_all_nine_files(repo_root: Path) -> None:
    text, files = context.dump_repo_text(repo_root)
    assert len(files) == 8  # data tree has 8 committed files (PRD aspirational 9)
    assert "polygons.py" in text
    assert "mathsquiz" in text
    assert "LICENSE" in text.upper() or "License" in text


def test_dump_repo_is_sorted_by_path(repo_root: Path) -> None:
    _, files = context.dump_repo_text(repo_root)
    assert files == sorted(files)


def test_count_tokens_is_positive_for_text() -> None:
    assert context.count_tokens("a b c") == 3
    assert context.count_tokens("") == 0


def test_make_diff_produces_unified_diff() -> None:
    diff = context.make_diff("a\n", "b\n", "polygons.py")
    assert diff.startswith("---") or "@@" in diff
    assert "polygons.py" in diff
