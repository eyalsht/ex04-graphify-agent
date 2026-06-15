"""Thin Typer CLI — zero business logic (SDK-first). Commands delegate to ``sdk``.

Concrete commands are wired as each phase lands; for now ``ex04 --help`` resolves.
"""

import typer

from ex04_graphify_agent.sdk import Ex04Sdk

app = typer.Typer(
    name="ex04",
    help="Graph-guided Graphify+Obsidian agent for reverse-engineering broken-python.",
    no_args_is_help=True,
)


@app.callback()
def _main() -> None:
    """EX04 CLI root (forces sub-command mode so future commands stay grouped)."""


@app.command()
def version() -> None:
    """Print the package version."""
    from ex04_graphify_agent import __version__

    typer.echo(__version__)


@app.command()
def hot() -> None:
    """Generate ``obsidian/hot.md`` — the graph-ranked "where to look first" note.

    Keyless (no LLM call): delegates entirely to ``Ex04Sdk.generate_hot``.
    """
    path = Ex04Sdk().generate_hot()
    typer.echo(f"Wrote {path}")


if __name__ == "__main__":  # pragma: no cover
    app()
