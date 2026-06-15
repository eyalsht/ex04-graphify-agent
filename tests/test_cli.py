"""Smoke tests for the thin CLI (zero business logic lives here)."""

from __future__ import annotations

from typer.testing import CliRunner

from ex04_graphify_agent import __version__
from ex04_graphify_agent.cli import app

runner = CliRunner()


def test_help_resolves() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "ex04" in result.output


def test_version_command_prints_version() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert __version__ in result.output
