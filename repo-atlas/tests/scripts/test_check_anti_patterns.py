"""Gate tests for ``scripts/check_anti_patterns.py``."""

from __future__ import annotations

from pathlib import Path

import check_anti_patterns as gate


def _src(tmp_path: Path, body: str) -> None:
    module = tmp_path / "src" / "pkg" / "mod.py"
    module.parent.mkdir(parents=True)
    module.write_text(body, encoding="utf-8")


def _labels(tmp_path: Path) -> list[str]:
    return [label for _, _, label in gate.find_violations(tmp_path)]


def test_clean_source_passes(tmp_path: Path) -> None:
    _src(tmp_path, "import typer\n\n\ndef show() -> None:\n    typer.echo('ok')\n")
    assert gate.find_violations(tmp_path) == []


def test_missing_src_dir_is_not_a_violation(tmp_path: Path) -> None:
    assert gate.find_violations(tmp_path) == []


def test_not_implemented_error_flagged(tmp_path: Path) -> None:
    _src(tmp_path, "def todo() -> None:\n    raise NotImplementedError\n")
    assert "NotImplementedError" in _labels(tmp_path)


def test_bare_print_flagged(tmp_path: Path) -> None:
    _src(tmp_path, "def show() -> None:\n    print('debug')\n")
    assert "debug-print" in _labels(tmp_path)


def test_attribute_print_is_not_flagged(tmp_path: Path) -> None:
    _src(tmp_path, "def show(stream: object) -> None:\n    stream.print('ok')\n")
    assert gate.find_violations(tmp_path) == []


def test_no_verify_flagged(tmp_path: Path) -> None:
    _src(tmp_path, 'CMD = ["git", "commit", "--no-verify"]\n')
    assert "no-verify" in _labels(tmp_path)


def test_main_reports_exit_codes(tmp_path: Path) -> None:
    assert gate.main([str(tmp_path)]) == 0
    _src(tmp_path, "def todo() -> None:\n    raise NotImplementedError\n")
    assert gate.main([str(tmp_path)]) == 1
