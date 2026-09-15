"""``atlas map`` — extract + vault in one pass (CLAUDE.md §3, PHASE6-004)."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from repo_atlas.cli import app
from tests.sdk._repo import build_repo

runner = CliRunner()


def test_map_writes_graph_and_vault_and_prints_a_summary(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    out = tmp_path / "out"
    result = runner.invoke(app, ["map", str(repo), "--out", str(out)])
    assert result.exit_code == 0
    assert (out / "graph.json").is_file()
    assert (out / "vault" / "index.md").is_file()
    assert "graph.json" in result.stdout
    assert "vault" in result.stdout.lower()


def test_map_forwards_the_seed_option(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    out = tmp_path / "out"
    result = runner.invoke(app, ["map", str(repo), "--out", str(out), "--seed", "pkg_shapes_make"])
    assert result.exit_code == 0
    hot = (out / "vault" / "hot.md").read_text(encoding="utf-8")
    assert "proximity" in hot


def test_map_surfaces_an_unknown_seed_without_a_traceback(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    out = tmp_path / "out"
    result = runner.invoke(app, ["map", str(repo), "--out", str(out), "--seed", "nope"])
    assert result.exit_code != 0
    assert "Traceback" not in result.output
    assert "nope" in result.output


def test_map_fails_clearly_for_a_missing_repo(tmp_path: Path) -> None:
    result = runner.invoke(app, ["map", str(tmp_path / "does-not-exist")])
    assert result.exit_code != 0
    assert "Traceback" not in result.output


def test_brief_command_writes_a_brief(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    out = tmp_path / "out"
    result = runner.invoke(app, ["brief", str(repo), "--out", str(out)])
    assert result.exit_code == 0, result.stdout
    assert (out / "BRIEF.md").is_file()


def test_brief_command_reports_where_it_wrote(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    result = runner.invoke(app, ["brief", str(repo), "--out", str(tmp_path / "out")])
    assert "BRIEF.md" in result.stdout


def test_brief_command_rejects_an_unknown_seed(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    result = runner.invoke(
        app, ["brief", str(repo), "--out", str(tmp_path / "out"), "--seed", "no_such_node"]
    )
    assert result.exit_code == 1


def test_compare_command_writes_the_evidence_report(tmp_path: Path) -> None:
    out = tmp_path / "out"
    result = runner.invoke(app, ["compare", str(build_repo(tmp_path)), "--out", str(out)])
    assert result.exit_code == 0, result.stdout
    assert (out / "token_comparison.md").is_file()


def test_compare_command_reports_the_reduction(tmp_path: Path) -> None:
    result = runner.invoke(
        app, ["compare", str(build_repo(tmp_path)), "--out", str(tmp_path / "out")]
    )
    assert "%" in result.stdout
