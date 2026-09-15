"""The public façade — every business decision funnels through here (CLAUDE.md §3).

``cli.py`` builds a ``RunPaths`` and calls into this module; it never imports an
extractor, graph_reader, or vault module directly. ``compare()`` joins this surface with the
token-comparison layer; the seam is left clean rather than stubbed with a fake.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from repo_atlas.brief import GRAPH_GUIDED, BriefResult, BriefRunner
from repo_atlas.extractor.build import GRAPH_FILENAME, ExtractResult
from repo_atlas.extractor.build import extract as _build_extract
from repo_atlas.gatekeeper import Gatekeeper, TokenLogger
from repo_atlas.graph_reader import GraphReader
from repo_atlas.paths import RunConfig, RunPaths
from repo_atlas.vault import VaultWriter

VAULT_DIRNAME = "vault"
RUNS_DIRNAME = "runs"
BRIEF_FILENAME = "BRIEF.md"


@dataclass(frozen=True)
class BriefOutcome:
    """Where the brief landed, plus the run it came from (tokens, sources, sections)."""

    brief_path: Path
    result: BriefResult


@dataclass(frozen=True)
class VaultResult:
    """Where the vault landed, and how many notes/communities it holds."""

    vault_dir: Path
    node_count: int
    community_count: int


def extract(paths: RunPaths, marker_limit: int | None = None) -> ExtractResult:
    """Walk ``paths.repo_root`` and write graph.json, manifest.json, GRAPH_REPORT.md."""
    return _build_extract(paths, marker_limit=marker_limit)


def vault(paths: RunPaths, top_k: int | None = None, seed_id: str | None = None) -> VaultResult:
    """Load the graph — extracting first if none exists yet — and write the vault.

    Raises:
        KeyError: ``seed_id`` is not a node in the graph.
    """
    RunConfig.load(paths.config_path)  # fail loud on a missing/invalid config, as extract() does
    graph_path = paths.out_dir / GRAPH_FILENAME
    if not graph_path.is_file():
        extract(paths)
    config = RunConfig.load(paths.config_path)
    reader = GraphReader(
        graph_path,
        exact_max_nodes=config.graph_reader.betweenness_exact_max_nodes,
        sample_k=config.graph_reader.betweenness_sample_k,
    )
    writer = VaultWriter(reader, paths.out_dir / VAULT_DIRNAME)
    vault_dir = writer.write_all(
        top_k=top_k if top_k is not None else config.vault.hot_top_k,
        weights=config.vault.hot_weights,
        seed_id=seed_id,
    )
    return VaultResult(
        vault_dir=vault_dir,
        node_count=len(reader.all_nodes()),
        community_count=len(reader.communities()),
    )


def map_repo(
    paths: RunPaths,
    marker_limit: int | None = None,
    seed_id: str | None = None,
) -> tuple[ExtractResult, VaultResult]:
    """Extract, then write the vault, in one pass. ``brief()`` joins this seam later.

    Raises:
        KeyError: ``seed_id`` is not a node in the freshly extracted graph.
    """
    extract_result = extract(paths, marker_limit=marker_limit)
    vault_result = vault(paths, seed_id=seed_id)
    return extract_result, vault_result


def brief(
    paths: RunPaths,
    seed_id: str | None = None,
    run_type: str = GRAPH_GUIDED,
) -> BriefOutcome:
    """Write ``BRIEF.md`` for a repository, extracting and building the vault if needed.

    The gatekeeper is constructed here rather than inside the brief layer: choosing a
    provider is a run-level decision, and keeping it at the façade means the brief layer
    stays a pure consumer that tests can hand any client.
    """
    vault_result = vault(paths, seed_id=seed_id)
    config = RunConfig.load(paths.config_path)
    reader = GraphReader(
        paths.out_dir / GRAPH_FILENAME,
        exact_max_nodes=config.graph_reader.betweenness_exact_max_nodes,
        sample_k=config.graph_reader.betweenness_sample_k,
    )
    logger = TokenLogger(paths.out_dir / RUNS_DIRNAME)
    runner = BriefRunner(Gatekeeper(config.gatekeeper_config(), logger), logger)
    result = runner.run(
        reader=reader,
        repo_root=paths.repo_root,
        vault_text=_vault_text(vault_result.vault_dir),
        repo_name=paths.repo_root.name,
        run_type=run_type,
        budget=config.brief.context_token_budget,
        hot_slices=config.brief.hot_source_slices,
        seed_id=seed_id,
    )
    if logger.records:
        logger.dump()
    return BriefOutcome(brief_path=result.write(paths.out_dir / BRIEF_FILENAME), result=result)


def _vault_text(vault_dir: Path) -> str:
    """index.md + hot.md — the map the brief reasons over, not the whole vault."""
    parts = [
        (vault_dir / name).read_text(encoding="utf-8")
        for name in ("index.md", "hot.md")
        if (vault_dir / name).is_file()
    ]
    return "\n\n".join(parts)
