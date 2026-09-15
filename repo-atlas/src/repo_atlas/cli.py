"""Thin Typer CLI over the SDK — zero business logic (CLAUDE.md §3).

Each command turns its arguments into a ``RunPaths``, calls exactly one ``sdk`` function,
and prints what it did. REPO existence/directory-ness is validated by Typer's own ``Path``
type (a bad value fails with a clean Click usage error, never a traceback); the errors the
SDK itself can still raise — a broken ``--config`` file, an unknown ``--seed`` — are caught
here and turned into the same kind of clean, non-zero-exit message.
"""

from __future__ import annotations

from pathlib import Path
from typing import NoReturn

import typer

from repo_atlas import __version__, sdk
from repo_atlas.paths import ConfigError, RunPaths

app = typer.Typer(
    name="atlas",
    help="Map a Python repository into a knowledge graph, an Obsidian vault, and a brief.",
    no_args_is_help=True,
)

_REPO_ARG = typer.Argument(
    ..., exists=True, file_okay=False, dir_okay=True, resolve_path=True, help="Repo to map."
)
_OUT_OPT = typer.Option(None, "--out", help="Output directory (default: <repo>/.atlas).")
_SEED_OPT = typer.Option(None, "--seed", help="Node id to rank hot.md by proximity to.")
_CONFIG_OPT = typer.Option(
    None, "--config", exists=True, dir_okay=False, resolve_path=True, help="Path to atlas.json."
)
_TOP_K_OPT = typer.Option(None, "--top-k", help="Entries in hot.md (default: from config).")


@app.callback()
def _main() -> None:
    """Root callback — forces sub-command mode so future commands stay grouped."""


@app.command()
def version() -> None:
    """Print the installed repo-atlas version."""
    typer.echo(__version__)


@app.command()
def extract(
    repo: Path = _REPO_ARG,
    out: Path | None = _OUT_OPT,
    config: Path | None = _CONFIG_OPT,
) -> None:
    """Walk REPO and write graph.json, manifest.json and GRAPH_REPORT.md."""
    try:
        result = sdk.extract(RunPaths.create(repo, out=out, config=config))
    except ConfigError as exc:
        _fail(exc)
    typer.echo(f"Extracted {result.node_count} nodes / {result.edge_count} edges.")
    typer.echo(f"  graph:    {result.graph_path}")
    typer.echo(f"  manifest: {result.manifest_path}")
    typer.echo(f"  report:   {result.report_path}")
    if result.degraded_files:
        names = ", ".join(result.degraded_files)
        typer.echo(f"  degraded parses ({len(result.degraded_files)}): {names}")


@app.command()
def vault(
    repo: Path = _REPO_ARG,
    out: Path | None = _OUT_OPT,
    seed: str | None = _SEED_OPT,
    top_k: int | None = _TOP_K_OPT,
) -> None:
    """Load (or build) the graph and write the Obsidian vault."""
    try:
        result = sdk.vault(RunPaths.create(repo, out=out), top_k=top_k, seed_id=seed)
    except (ConfigError, KeyError) as exc:
        _fail(exc)
    typer.echo(
        f"Vault written to {result.vault_dir} "
        f"({result.node_count} notes, {result.community_count} communities)."
    )


@app.command(name="map")
def map_repo(
    repo: Path = _REPO_ARG,
    out: Path | None = _OUT_OPT,
    seed: str | None = _SEED_OPT,
) -> None:
    """Extract the graph and write the vault in one pass."""
    try:
        extract_result, vault_result = sdk.map_repo(RunPaths.create(repo, out=out), seed_id=seed)
    except (ConfigError, KeyError) as exc:
        _fail(exc)
    typer.echo(f"Extracted {extract_result.node_count} nodes / {extract_result.edge_count} edges.")
    typer.echo(f"  graph: {extract_result.graph_path}")
    typer.echo(
        f"Vault written to {vault_result.vault_dir} "
        f"({vault_result.node_count} notes, {vault_result.community_count} communities)."
    )


@app.command()
def brief(
    repo: Path = _REPO_ARG,
    out: Path | None = _OUT_OPT,
    seed: str | None = _SEED_OPT,
) -> None:
    """Write BRIEF.md — an architecture brief built from the graph and vault."""
    try:
        outcome = sdk.brief(RunPaths.create(repo, out=out), seed_id=seed)
    except (ConfigError, KeyError) as exc:
        _fail(exc)
    tokens = sum(usage["input_tokens"] for usage in outcome.result.token_usage)
    typer.echo(f"Brief written to {outcome.brief_path}")
    typer.echo(
        f"  {len(outcome.result.sections)} sections, "
        f"{len(outcome.result.token_usage)} LLM calls, {tokens} input tokens."
    )


def _fail(exc: Exception) -> NoReturn:
    typer.echo(str(exc), err=True)
    raise typer.Exit(code=1) from exc
