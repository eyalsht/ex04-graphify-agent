"""``atlas extract`` — thin CLI wrapper over ``sdk.extract`` (CLAUDE.md §3, PHASE6-004)."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from repo_atlas.cli import app
from tests.sdk._repo import build_repo

runner = CliRunner()


def test_extract_writes_artifacts_and_prints_a_summary(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    out = tmp_path / "out"
    result = runner.invoke(app, ["extract", str(repo), "--out", str(out)])
    assert result.exit_code == 0
    assert (out / "graph.json").is_file()
    assert (out / "manifest.json").is_file()
    assert (out / "GRAPH_REPORT.md").is_file()
    assert "graph.json" in result.stdout
    assert "node" in result.stdout.lower()


def test_extract_fails_clearly_for_a_missing_repo(tmp_path: Path) -> None:
    result = runner.invoke(app, ["extract", str(tmp_path / "does-not-exist")])
    assert result.exit_code != 0
    assert "Traceback" not in result.output


def test_extract_fails_clearly_when_repo_is_a_file(tmp_path: Path) -> None:
    not_a_dir = tmp_path / "file.txt"
    not_a_dir.write_text("hi", encoding="utf-8")
    result = runner.invoke(app, ["extract", str(not_a_dir)])
    assert result.exit_code != 0
    assert "Traceback" not in result.output


def test_extract_fails_clearly_for_a_broken_config(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    bad_config = tmp_path / "bad.json"
    bad_config.write_text("{not json", encoding="utf-8")
    result = runner.invoke(app, ["extract", str(repo), "--config", str(bad_config)])
    assert result.exit_code != 0
    assert "Traceback" not in result.output
