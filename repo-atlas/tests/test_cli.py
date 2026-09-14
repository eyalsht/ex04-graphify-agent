"""The CLI entry point resolves and stays logic-free (CLAUDE.md §3)."""

from __future__ import annotations

from typer.testing import CliRunner

from repo_atlas import __version__
from repo_atlas.cli import app

runner = CliRunner()


def test_version_command_prints_the_package_version() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert result.stdout.strip() == __version__


def test_bare_invocation_shows_help() -> None:
    result = runner.invoke(app, [])
    assert "Map a Python repository" in result.stdout
