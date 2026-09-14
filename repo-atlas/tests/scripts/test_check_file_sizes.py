"""Gate tests for ``scripts/check_file_sizes.py`` (CLAUDE.md §3: ≤150 lines)."""

from __future__ import annotations

from pathlib import Path

import check_file_sizes as gate


def _module(tmp_path: Path, relative: str, lines: int) -> Path:
    path = tmp_path / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("x = 1\n" * lines, encoding="utf-8")
    return path


def test_file_at_the_limit_passes(tmp_path: Path) -> None:
    _module(tmp_path, "src/pkg/mod.py", gate.MAX_LINES)
    assert gate.find_violations(tmp_path) == []


def test_file_over_the_limit_flagged(tmp_path: Path) -> None:
    _module(tmp_path, "src/pkg/mod.py", gate.MAX_LINES + 1)
    offenders = gate.find_violations(tmp_path)
    assert [count for _, count in offenders] == [gate.MAX_LINES + 1]


def test_tests_and_scripts_are_scanned_too(tmp_path: Path) -> None:
    _module(tmp_path, "tests/test_big.py", gate.MAX_LINES + 5)
    _module(tmp_path, "scripts/big.py", gate.MAX_LINES + 5)
    assert len(gate.find_violations(tmp_path)) == 2


def test_golden_fixtures_are_exempt(tmp_path: Path) -> None:
    """Vendored third-party source is kept verbatim for regression diffs, not split."""
    _module(tmp_path, "tests/fixtures/golden/vendored.py", gate.MAX_LINES + 50)
    assert gate.find_violations(tmp_path) == []


def test_unscanned_directories_are_ignored(tmp_path: Path) -> None:
    _module(tmp_path, "docs/big.py", gate.MAX_LINES + 50)
    assert gate.find_violations(tmp_path) == []


def test_main_reports_exit_codes(tmp_path: Path) -> None:
    assert gate.main([str(tmp_path)]) == 0
    _module(tmp_path, "src/pkg/mod.py", gate.MAX_LINES + 1)
    assert gate.main([str(tmp_path)]) == 1
