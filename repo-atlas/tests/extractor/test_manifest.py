"""``manifest.json`` — content-hash tracking for incremental re-runs (PHASE1-023, R1.7)."""

from __future__ import annotations

import hashlib

from repo_atlas.extractor import manifest


def _write(tmp_path, name: str, text: str):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


def test_ast_hash_is_stable_for_equivalent_source() -> None:
    first = manifest.ast_hash("x = 1\ny = 2\n")
    second = manifest.ast_hash("x = 1\ny = 2\n")
    assert first == second


def test_ast_hash_differs_for_different_source() -> None:
    assert manifest.ast_hash("x = 1\n") != manifest.ast_hash("x = 2\n")


def test_ast_hash_ignores_a_change_that_does_not_change_the_ast() -> None:
    """Whitespace-only edits reparse to the same AST, so the hash should match."""
    assert manifest.ast_hash("x = 1\n") == manifest.ast_hash("x   =   1\n")


def test_ast_hash_falls_back_to_raw_text_sha256_on_syntax_error() -> None:
    broken = "print 'py2'\n"
    expected = hashlib.sha256(broken.encode("utf-8")).hexdigest()
    assert manifest.ast_hash(broken) == expected


def test_ast_hash_fallback_still_differs_for_different_broken_text() -> None:
    assert manifest.ast_hash("print 'a'\n") != manifest.ast_hash("print 'b'\n")


def test_build_manifest_reads_mtime_and_ast_hash(tmp_path) -> None:
    path = _write(tmp_path, "a.py", "x = 1\n")
    result = manifest.build_manifest({"a.py": path})
    assert result["a.py"]["ast_hash"] == manifest.ast_hash("x = 1\n")
    assert result["a.py"]["mtime"] == path.stat().st_mtime


def test_build_manifest_handles_an_unparseable_file(tmp_path) -> None:
    path = _write(tmp_path, "broken.py", "print 'py2'\n")
    result = manifest.build_manifest({"broken.py": path})
    assert result["broken.py"]["ast_hash"] == manifest.ast_hash("print 'py2'\n")


def test_write_then_load_manifest_round_trips(tmp_path) -> None:
    data = {"a.py": {"mtime": 1.5, "ast_hash": "deadbeef"}}
    target = tmp_path / "manifest.json"
    manifest.write_manifest(target, data)
    assert manifest.load_manifest(target) == data
    assert target.read_text(encoding="utf-8").endswith("\n")


def test_load_manifest_returns_empty_dict_when_file_is_missing(tmp_path) -> None:
    assert manifest.load_manifest(tmp_path / "nope.json") == {}


def test_diff_reports_unchanged_changed_added_and_removed() -> None:
    old = {
        "a.py": {"mtime": 1.0, "ast_hash": "same"},
        "b.py": {"mtime": 1.0, "ast_hash": "old-hash"},
        "gone.py": {"mtime": 1.0, "ast_hash": "x"},
    }
    new = {
        "a.py": {"mtime": 2.0, "ast_hash": "same"},
        "b.py": {"mtime": 2.0, "ast_hash": "new-hash"},
        "fresh.py": {"mtime": 2.0, "ast_hash": "y"},
    }
    result = manifest.diff_manifest(old, new)
    assert result.unchanged == {"a.py"}
    assert result.changed == {"b.py"}
    assert result.added == {"fresh.py"}
    assert result.removed == {"gone.py"}


def test_diff_against_an_empty_old_manifest_marks_everything_added() -> None:
    result = manifest.diff_manifest({}, {"a.py": {"mtime": 1.0, "ast_hash": "x"}})
    assert result.added == {"a.py"}
    assert result.unchanged == set()
    assert result.changed == set()
    assert result.removed == set()
