"""The from-scratch ``.gitignore`` matcher (PRD R1.3) — no third-party dependency.

Covers exactly the syntax ``docs``/the module docstring says is supported, plus one test
per documented out-of-scope simplification, so "out of scope" always means "tested to
confirm the actual behaviour", never "untested".
"""

from __future__ import annotations

from pathlib import Path

from repo_atlas.extractor.gitignore import GitIgnore


def _write(tmp_path: Path, contents: str) -> Path:
    (tmp_path / ".gitignore").write_text(contents, encoding="utf-8")
    return tmp_path


def test_absent_gitignore_matches_nothing(tmp_path: Path) -> None:
    ignore = GitIgnore.load(tmp_path)
    assert ignore.matches("anything.py", is_dir=False) is False


def test_blank_lines_and_comments_are_skipped(tmp_path: Path) -> None:
    _write(tmp_path, "\n# a comment\n\n*.log\n")
    ignore = GitIgnore.load(tmp_path)
    assert ignore.matches("a.log", is_dir=False) is True
    assert ignore.matches("# a comment", is_dir=False) is False


def test_trailing_slash_is_a_directory_only_rule(tmp_path: Path) -> None:
    _write(tmp_path, "build/\n")
    ignore = GitIgnore.load(tmp_path)
    assert ignore.matches("build", is_dir=True) is True
    assert ignore.matches("build", is_dir=False) is False


def test_leading_slash_anchors_the_pattern_to_the_root(tmp_path: Path) -> None:
    _write(tmp_path, "/dist\n")
    ignore = GitIgnore.load(tmp_path)
    assert ignore.matches("dist", is_dir=True) is True
    assert ignore.matches("nested/dist", is_dir=True) is False


def test_unanchored_pattern_matches_the_basename_at_any_depth(tmp_path: Path) -> None:
    _write(tmp_path, "secrets.env\n")
    ignore = GitIgnore.load(tmp_path)
    assert ignore.matches("secrets.env", is_dir=False) is True
    assert ignore.matches("nested/deep/secrets.env", is_dir=False) is True


def test_star_glob_matches_via_fnmatch(tmp_path: Path) -> None:
    _write(tmp_path, "*.pyc\n")
    ignore = GitIgnore.load(tmp_path)
    assert ignore.matches("module.pyc", is_dir=False) is True
    assert ignore.matches("module.py", is_dir=False) is False


def test_negation_overrides_an_earlier_match_last_rule_wins(tmp_path: Path) -> None:
    _write(tmp_path, "*.log\n!important.log\n")
    ignore = GitIgnore.load(tmp_path)
    assert ignore.matches("debug.log", is_dir=False) is True
    assert ignore.matches("important.log", is_dir=False) is False


def test_a_later_rule_can_re_ignore_after_a_negation(tmp_path: Path) -> None:
    _write(tmp_path, "!keep.log\n*.log\n")
    ignore = GitIgnore.load(tmp_path)
    assert ignore.matches("keep.log", is_dir=False) is True


def test_double_star_has_no_special_recursive_meaning_out_of_scope(tmp_path: Path) -> None:
    """Documented simplification: ``**`` degrades to plain ``fnmatch`` ``*`` semantics."""
    _write(tmp_path, "/**/vendor\n")
    ignore = GitIgnore.load(tmp_path)
    # fnmatch's "*" already crosses "/" since it operates on the whole string, so this
    # still matches a nested path -- just not because "**" was given special meaning.
    assert ignore.matches("a/b/vendor", is_dir=True) is True


def test_dir_only_rule_never_matches_a_file(tmp_path: Path) -> None:
    _write(tmp_path, "cache/\n")
    ignore = GitIgnore.load(tmp_path)
    assert ignore.matches("cache", is_dir=False) is False
