"""Walking a repo for extraction-eligible files (PRD R1.3, PHASE1-005/006).

Fixture trees are built under ``tmp_path`` -- never against ``tests/fixtures/golden/``,
which is reserved for the golden-regression eval (``CLAUDE.md`` Sec.7).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from repo_atlas.extractor.discovery import DiscoveredFile, discover_files, read_discovered_text
from repo_atlas.paths import ExtractorConfig

_CONFIG = ExtractorConfig(
    exclude_dirs=(".git", "__pycache__", "node_modules"),
    exclude_globs=("*.lock", "generated_*.py"),
    max_file_bytes=1024,
    document_extensions=(".md", ".txt"),
)


def _rels(files: tuple[DiscoveredFile, ...]) -> list[str]:
    return [f.rel_path for f in files]


def test_classifies_python_files(tmp_path: Path) -> None:
    (tmp_path / "a.py").write_text("x = 1\n", encoding="utf-8")
    found = discover_files(tmp_path, _CONFIG)
    assert _rels(found) == ["a.py"]
    assert found[0].kind == "python"


def test_classifies_configured_document_extensions(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("hello\n", encoding="utf-8")
    found = discover_files(tmp_path, _CONFIG)
    assert found[0].kind == "document"


def test_skips_a_file_with_an_unrecognized_extension(tmp_path: Path) -> None:
    (tmp_path / "image.png").write_bytes(b"\x89PNG\r\n")
    assert discover_files(tmp_path, _CONFIG) == ()


def test_extension_matching_is_case_insensitive(tmp_path: Path) -> None:
    (tmp_path / "A.PY").write_text("x = 1\n", encoding="utf-8")
    found = discover_files(tmp_path, _CONFIG)
    assert found[0].kind == "python"


def test_excludes_a_directory_named_in_exclude_dirs_at_any_depth(tmp_path: Path) -> None:
    nested = tmp_path / "pkg" / "__pycache__"
    nested.mkdir(parents=True)
    (nested / "a.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / "pkg" / "keep.py").write_text("x = 1\n", encoding="utf-8")
    assert _rels(discover_files(tmp_path, _CONFIG)) == ["pkg/keep.py"]


def test_excludes_files_matching_an_exclude_glob(tmp_path: Path) -> None:
    # "generated_x.py" has an otherwise-eligible ".py" suffix -- the exclude_globs check,
    # not the extension check, is what must reject it.
    (tmp_path / "generated_x.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / "keep.py").write_text("x = 1\n", encoding="utf-8")
    assert _rels(discover_files(tmp_path, _CONFIG)) == ["keep.py"]


def test_exclude_glob_matches_the_basename_at_any_depth(tmp_path: Path) -> None:
    nested = tmp_path / "sub"
    nested.mkdir()
    (nested / "generated_x.py").write_text("x = 1\n", encoding="utf-8")
    assert discover_files(tmp_path, _CONFIG) == ()


def test_skips_a_file_larger_than_max_file_bytes(tmp_path: Path) -> None:
    (tmp_path / "big.py").write_bytes(b"x" * 2048)
    assert discover_files(tmp_path, _CONFIG) == ()


def test_size_check_never_reads_the_oversized_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "big.py").write_bytes(b"x" * 2048)

    def _boom(self: Path) -> bytes:  # pragma: no cover - only invoked on failure
        raise AssertionError("discovery read a file it should have skipped by size alone")

    monkeypatch.setattr(Path, "read_bytes", _boom)
    assert discover_files(tmp_path, _CONFIG) == ()


def test_skips_a_file_that_is_not_valid_utf8(tmp_path: Path) -> None:
    (tmp_path / "bad.py").write_bytes(b"\xff\xfe\x00\x01")
    assert discover_files(tmp_path, _CONFIG) == ()


def test_honours_the_root_gitignore(tmp_path: Path) -> None:
    (tmp_path / ".gitignore").write_text("ignored.md\n", encoding="utf-8")
    (tmp_path / "ignored.md").write_text("x\n", encoding="utf-8")
    (tmp_path / "kept.md").write_text("x\n", encoding="utf-8")
    assert _rels(discover_files(tmp_path, _CONFIG)) == ["kept.md"]


def test_result_is_sorted_and_deterministic(tmp_path: Path) -> None:
    for name in ("z.py", "a.py", "m.md"):
        (tmp_path / name).write_text("x\n", encoding="utf-8")
    assert _rels(discover_files(tmp_path, _CONFIG)) == ["a.py", "m.md", "z.py"]


def test_read_discovered_text_reads_the_file(tmp_path: Path) -> None:
    path = tmp_path / "a.py"
    path.write_text("x = 1\n", encoding="utf-8")
    discovered = discover_files(tmp_path, _CONFIG)[0]
    assert read_discovered_text(discovered) == "x = 1\n"


def test_read_discovered_text_falls_back_to_replace_on_a_toctou_decode_error(
    tmp_path: Path,
) -> None:
    path = tmp_path / "a.py"
    path.write_text("x = 1\n", encoding="utf-8")
    discovered = discover_files(tmp_path, _CONFIG)[0]
    # Simulate the file changing on disk *after* discovery validated it (a TOCTOU race).
    path.write_bytes(b"\xff\xfey = 2\n")
    text = read_discovered_text(discovered)
    assert "y = 2" in text
    assert "�" in text  # the U+FFFD replacement character, not a raised exception


def test_directory_matching_the_extension_check_is_not_mistaken_for_a_file(
    tmp_path: Path,
) -> None:
    (tmp_path / "package.py").mkdir()
    assert discover_files(tmp_path, _CONFIG) == ()
