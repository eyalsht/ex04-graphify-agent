"""Thin Typer CLI over the SDK — zero business logic (CLAUDE.md §3).

Sub-commands are wired as each phase lands; ``atlas --help`` and ``atlas version`` resolve from
the scaffold onward so the entry point is always exercisable.
"""

from __future__ import annotations

import typer

from repo_atlas import __version__

app = typer.Typer(
    name="atlas",
    help="Map a Python repository into a knowledge graph, an Obsidian vault, and a brief.",
    no_args_is_help=True,
)


@app.callback()
def _main() -> None:
    """Root callback — forces sub-command mode so future commands stay grouped."""


@app.command()
def version() -> None:
    """Print the installed repo-atlas version."""
    typer.echo(__version__)
