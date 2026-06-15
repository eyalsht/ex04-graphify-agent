"""Tests for scripts/check_anti_patterns.py."""

from __future__ import annotations

from pathlib import Path

import check_anti_patterns


def _src(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "src" / "mod.py"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def test_not_implemented_error_flagged(tmp_path: Path) -> None:
    _src(tmp_path, "def f() -> None:\n    raise NotImplementedError\n")
    labels = [label for _, _, label in check_anti_patterns.find_violations(tmp_path)]
    assert "NotImplementedError" in labels


def test_debug_print_flagged(tmp_path: Path) -> None:
    _src(tmp_path, 'print("debug")\n')
    labels = [label for _, _, label in check_anti_patterns.find_violations(tmp_path)]
    assert "debug-print" in labels


def test_clean_source_passes(tmp_path: Path) -> None:
    _src(tmp_path, "import typer\ntyper.echo('ok')\n")
    assert check_anti_patterns.find_violations(tmp_path) == []
    assert check_anti_patterns.main([str(tmp_path)]) == 0
