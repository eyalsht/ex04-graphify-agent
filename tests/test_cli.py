"""Smoke tests for the thin CLI (zero business logic lives here)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

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


def test_hot_command_delegates_to_sdk(tmp_path: Path) -> None:
    expected = tmp_path / "hot.md"
    with patch("ex04_graphify_agent.cli.Ex04Sdk") as mock_sdk_cls:
        mock_sdk_cls.return_value.generate_hot.return_value = expected
        result = runner.invoke(app, ["hot"])

    assert result.exit_code == 0
    mock_sdk_cls.return_value.generate_hot.assert_called_once_with()
    assert str(expected) in result.output


def test_hot_command_is_keyless() -> None:
    """``ex04 hot`` runs without any provider API key (CLAUDE.md keyless default)."""
    result = runner.invoke(app, ["hot"])
    assert result.exit_code == 0
    assert "hot.md" in result.output


def test_compare_command_delegates_to_sdk(tmp_path: Path) -> None:
    expected = tmp_path / "token_comparison.md"
    with patch("ex04_graphify_agent.cli.Ex04Sdk") as mock_sdk_cls:
        mock_sdk_cls.return_value.compare_tokens.return_value = expected
        result = runner.invoke(app, ["compare"])

    assert result.exit_code == 0
    mock_sdk_cls.return_value.compare_tokens.assert_called_once_with()
    assert str(expected) in result.output
