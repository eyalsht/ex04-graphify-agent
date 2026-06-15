"""Tests for scripts/check_file_sizes.py (≤150-line gate)."""

from __future__ import annotations

from pathlib import Path

import check_file_sizes


def _write(path: Path, n_lines: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join("x = 1" for _ in range(n_lines)), encoding="utf-8")


def test_over_long_file_is_flagged(tmp_path: Path) -> None:
    _write(tmp_path / "src" / "big.py", 200)
    offenders = check_file_sizes.find_violations(tmp_path)
    assert [p.name for p, _ in offenders] == ["big.py"]
    assert offenders[0][1] == 200


def test_within_limit_passes(tmp_path: Path) -> None:
    _write(tmp_path / "src" / "ok.py", 150)
    assert check_file_sizes.find_violations(tmp_path) == []


def test_main_exit_codes(tmp_path: Path) -> None:
    _write(tmp_path / "src" / "ok.py", 10)
    assert check_file_sizes.main([str(tmp_path)]) == 0
    _write(tmp_path / "scripts" / "big.py", 151)
    assert check_file_sizes.main([str(tmp_path)]) == 1
