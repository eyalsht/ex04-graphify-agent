"""``atlas vault`` — thin CLI wrapper over ``sdk.vault`` (CLAUDE.md §3, PHASE6-004)."""

from __future__ import annotations

import re
from pathlib import Path

from typer.testing import CliRunner

from repo_atlas.cli import app
from tests.sdk._repo import build_repo

runner = CliRunner()
_RANKED_LINE = re.compile(r"^\d+\. ", re.MULTILINE)


def test_vault_writes_notes_and_prints_a_summary(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    out = tmp_path / "out"
    result = runner.invoke(app, ["vault", str(repo), "--out", str(out)])
    assert result.exit_code == 0
    assert (out / "vault" / "index.md").is_file()
    assert (out / "vault" / "hot.md").is_file()
    assert "vault" in result.stdout.lower()


def test_vault_builds_the_graph_first_when_missing(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    out = tmp_path / "out"
    result = runner.invoke(app, ["vault", str(repo), "--out", str(out)])
    assert result.exit_code == 0
    assert (out / "graph.json").is_file()


def test_vault_surfaces_an_unknown_seed_without_a_traceback(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    out = tmp_path / "out"
    result = runner.invoke(app, ["vault", str(repo), "--out", str(out), "--seed", "nope"])
    assert result.exit_code != 0
    assert "Traceback" not in result.output
    assert "nope" in result.output


def test_vault_respects_the_top_k_flag(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    out = tmp_path / "out"
    result = runner.invoke(app, ["vault", str(repo), "--out", str(out), "--top-k", "1"])
    assert result.exit_code == 0
    hot = (out / "vault" / "hot.md").read_text(encoding="utf-8")
    assert len(_RANKED_LINE.findall(hot)) == 1


def test_vault_fails_clearly_for_a_missing_repo(tmp_path: Path) -> None:
    result = runner.invoke(app, ["vault", str(tmp_path / "does-not-exist")])
    assert result.exit_code != 0
    assert "Traceback" not in result.output
