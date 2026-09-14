"""Symlink handling in ``discover_files`` (PRD R1.3): never escape ``repo_root``.

Split from ``test_discovery.py`` to keep both files under the 150-line cap
(``CLAUDE.md`` Sec.3).
"""

from __future__ import annotations

from pathlib import Path

from repo_atlas.extractor.discovery import discover_files
from repo_atlas.paths import ExtractorConfig

_CONFIG = ExtractorConfig(
    exclude_dirs=(".git",),
    exclude_globs=(),
    max_file_bytes=1024,
    document_extensions=(".md",),
)


def test_never_traverses_a_symlinked_directory(tmp_path: Path) -> None:
    real = tmp_path / "real"
    real.mkdir()
    (real / "a.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / "link").symlink_to(real, target_is_directory=True)
    found = discover_files(tmp_path, _CONFIG)
    rels = [f.rel_path for f in found]
    # "real/a.py" is reached through its own, non-symlinked directory entry and is found
    # normally. Documented out-of-scope simplification: the *symlinked* "link" directory --
    # even though its target sits inside repo_root -- is never descended into, so the same
    # file reached only through "link/a.py" never appears.
    assert rels == ["real/a.py"]


def test_skips_a_file_symlink_that_escapes_repo_root(tmp_path: Path) -> None:
    outside = tmp_path.parent / f"outside-{tmp_path.name}.py"
    outside.write_text("x = 1\n", encoding="utf-8")
    try:
        (tmp_path / "escape.py").symlink_to(outside)
        assert discover_files(tmp_path, _CONFIG) == ()
    finally:
        outside.unlink()


def test_skips_a_broken_symlink_inside_repo_root(tmp_path: Path) -> None:
    # Resolves inside repo_root (so it passes the escape check) but points at nothing, so
    # the size stat() itself raises OSError -- the defensive branch _consider() must handle.
    (tmp_path / "broken.py").symlink_to(tmp_path / "missing.py")
    assert discover_files(tmp_path, _CONFIG) == ()


def test_includes_a_file_symlink_that_stays_inside_repo_root(tmp_path: Path) -> None:
    real = tmp_path / "real.py"
    real.write_text("x = 1\n", encoding="utf-8")
    (tmp_path / "link.py").symlink_to(real)
    found = discover_files(tmp_path, _CONFIG)
    rels = [f.rel_path for f in found]
    assert rels == ["link.py", "real.py"]
    linked = next(f for f in found if f.rel_path == "link.py")
    assert linked.abs_path == real.resolve()
